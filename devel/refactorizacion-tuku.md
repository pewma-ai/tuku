# Refactorización de tuku

Plan para simplificar la arquitectura del comando `tuku` y, después, acortar sus tests. Este documento permite retomar el trabajo en cualquier fase.

## Fases

1. **Auditar `tuku`.** Diagnóstico de `src/tuku/` y propuesta de mejoras. No se toca código ni tests. Estado: diagnóstico y propuesta escritos abajo, a la espera de que el autor los apruebe.
2. **Refactorizar `tuku`** según lo aprobado, **sin tocar los tests**. Los tests actuales son la red de seguridad: si el refactor es correcto, pasan tal cual.
3. **Revisar los tests.** Con la arquitectura ya simplificada, decidir cuáles se combinan o acortan, y proponerlo al autor antes de editar.

## Estado

- [x] Fase 1: diagnóstico (2026-10-18).
- [ ] Fase 1: el autor aprueba o corrige la propuesta y resuelve las decisiones abiertas.
- [ ] Fase 2: P1 a P7, un paso a la vez.
- [ ] Fase 3: tests (ver las hipótesis al final).

## Restricciones de la fase 2

- Ningún archivo de `tests/` cambia. Criterio de cada paso: `git diff --stat tests/` vacío, `uv run pytest` (unitarios y escenarios deterministas), `uv run ruff check .` y `uv run mypy src tests` en verde.
- Las firmas públicas que los tests usan se mantienen: `todo.abrir_en_vault`, `todo.cerrar_en_vault`, `entry.add_al_vault`, `scope.crear_con_constancia`, `note.crear_con_constancia`, `scope.rutas`, `scope.nombres`, `scope.canonico`, entre otras.
- **El reloj no se inyecta en esta fase.** Los tests congelan `date` y `datetime` parchando el módulo donde se leen (`entry`, `todo`, `scope`, `note`, `cycle`, `context`, `init`, `cli.opciones`; ver [`tests/scripts/tiempo.py`](../tests/scripts/tiempo.py) y `test_cli_opciones.py`). Quitar esas lecturas, o moverlas a otro módulo, rompe esos tests. Por la misma razón, el código que lee el reloj se queda en el módulo donde está hoy.
- Dividir un módulo se hace sacando código a un módulo nuevo y reexportándolo desde el original, para que `scope.algo` siga existiendo.

## Línea base (2026-10-18)

| Medida | Valor |
|---|---|
| Tests unitarios | 285 verdes en 4,45 s (el [README de tests](../tests/README.md) promete menos de 1,5 s) |
| Ciclo de dependencias | 11 módulos: `config`, `context`, `cyclelint`, `doctor`, `entry`, `note`, `regenerate`, `scope`, `style`, `todo`, `vocab` |
| Líneas de import dentro de funciones | 85 (`doctor` 12, `entry` 21, `todo` 16, `scope` 15) |
| `scope.py` | 1335 líneas |
| Recorridos de `ambitos/` en un `todo open` | al menos 4, antes de regenerar |
| Sitios que estampan una línea en `AHORA.md` | 5 |

## Diagnóstico

### 1. El ciclo de dependencias está escondido en imports locales

A nivel de módulo solo hay un ciclo, `cli` con `cli.system`. El del núcleo existe, pero cada import cruzado se hizo dentro de una función. Los fan-out más altos: `doctor` 12, `scope` 11, `entry` 10, `context` 10, `todo` 9, `note` 9. El núcleo puro (`todo`, `entry`) llama hacia arriba, a `scope`, `regenerate` y `config`, y `config` importa `doctor`. Las tres capas que describe [DEVEL.md](../DEVEL.md) se cumplen en `cli/`, pero no entre los módulos de abajo.

### 2. "Dejar constancia en `AHORA.md`" está escrito cinco veces

[`entry.add_al_vault`](../src/tuku/entry.py), [`todo.abrir_en_vault`](../src/tuku/todo.py), [`todo.cerrar_en_vault`](../src/tuku/todo.py), [`scope.crear_con_constancia`](../src/tuku/scope.py) y [`note.crear_con_constancia`](../src/tuku/note.py) repiten la misma secuencia: validar el ámbito (`canonico` más `rechazo_si_no_existe`), resolver día y hora con el reloj, componer la línea, probar `entry.add` en memoria capturando `ValueError`, escribir y regenerar. La idempotencia diverge: `todo` compara por clave (`ya_abierto`, `ya_cerrado`), `note` con `constancia not in texto`, `scope` escribe solo si creó la carpeta. Es el foco principal de redundancia y de divergencia.

### 3. El árbol de ámbitos se relee en cada llamada

`scope.nombres`, `scope.rutas` y `scope.leer` recorren `ambitos/` con `rglob` cada vez (10 `glob` en [`scope.py`](../src/tuku/scope.py)). Un `todo open` los llama por `canonico`, `rechazo_si_no_existe` y dos veces `rutas`. `archivo_vault` aparece 18 veces, `leer_config` 7 y `rutas` en 9 sitios. No existe un snapshot que se lea una vez por comando. La validación `canonico` más `rechazo_si_no_existe` se copia en 8 sitios.

### 4. Módulos con varias responsabilidades

- [`scope.py`](../src/tuku/scope.py) (1335 líneas) junta: nombres y rutas del árbol, keywords, creación y jerarquía de hijos, actividad de la página, lint, constancia, registros que nombran a un ámbito, y `rename` y `move`.
- [`todo.py`](../src/tuku/todo.py) (856) junta el parser de marcas, la tabla, los casos de uso y el lint.
- [`doctor.revisar_vault`](../src/tuku/doctor.py) es una función de 130 líneas con una cadena de `if quiere(...)`. Hay cuatro registros de temas sin estructura común: `doctor.TEMAS`, `fix.TEMAS`, `regenerate.TEMAS` y `context.TEMAS`.

### 5. Código que `doctor` ya reemplazó

Cinco `lint_del_vault` no tienen llamador directo según `grep`: `entry`, `scope`, `style`, `cyclelint` y `todo`. `doctor` reimplementa esas revisiones inline o llama a `todo.hallazgos_del_vault` y `note.lint_del_vault`. Son restos de cuando cada noun tenía su `lint`, retirado el 2026-10-18 ([iteración](iteraciones/2026-10-18.md)). No hay funciones con cero referencias en todo `src` más `tests`.

### 6. La regla del ámbito por defecto vive en dos capas

`todo open` y `entry create` la resuelven en el CLI ([`cli/todo.py`](../src/tuku/cli/todo.py), [`cli/entry.py`](../src/tuku/cli/entry.py)); `todo close` la resuelve en el caso de uso. Esa asimetría produjo el bug D6 (`todo close` cerraba en `personal`). Según [DEVEL.md](../DEVEL.md), una regla del sistema dentro de un `_cmd_*` está en la capa equivocada.

### 7. Nombres que confunden

`abrir_en_vault` existe en `cycle` (abre el ciclo) y en `todo` (abre un pendiente). También se repiten `renombrar_en_vault`, `mover_en_vault`, `crear_con_constancia`, `registro_de_constancia`, `slug` y `canonico` (con significado distinto en `todo` y `scope`). `vocab.mostrar_del_vault` conserva el nombre del verbo `vocab show`, retirado.

### 8. Documentación desfasada en el código

- El docstring de [`doctor.py`](../src/tuku/doctor.py) dice que los lint sueltos (`cycle`, `entry`, `todo`, `style`) "siguen existiendo para uso fino".
- El de [`resultado.py`](../src/tuku/resultado.py) nombra `cli.py`, que ahora es un paquete.
- La promesa de 1,5 s de los unitarios en [`tests/README.md`](../tests/README.md) ya no se cumple.

## Propuesta para la fase 2

Orden por retorno y riesgo. Cada paso se hace solo, con la verificación de arriba.

- **P1. Un solo punto que estampa en `AHORA.md`.** Una función en [`entry.py`](../src/tuku/entry.py) recibe el texto de `AHORA.md` y los campos (hora, ámbito, cuerpo, día, rutas) y devuelve el texto nuevo o el rechazo, con una sola regla de idempotencia. Los cinco casos de uso la llaman. Lee el reloj quien la llama, como hoy.
- **P2. Leer el árbol de ámbitos una vez.** Un `Arbol` inmutable (nombres, rutas, ámbitos con sus keywords) que cada comando construye al empezar y pasa hacia abajo. `resolver_ambito(arbol, nombre) -> str | Resultado` reemplaza las 8 copias de `canonico` más `rechazo_si_no_existe`. Las funciones actuales `nombres(vault)`, `rutas(vault)` y `leer(vault)` quedan como envoltorios de una línea sobre `Arbol`, para no tocar tests. Sin caché global: los tests llaman `main` muchas veces en un proceso.
- **P3. Retirar los `lint_del_vault` sin llamador** (`entry`, `scope`, `style`, `cyclelint`, `todo`), tras confirmar con `grep` y `mypy` que nadie los usa.
- **P4. `doctor` como tabla.** `REVISIONES = {tema: función}` reemplaza la cadena de `if quiere(...)`, y `doctor.TEMAS` se deriva de la tabla. No cambia ningún mensaje.
- **P5. Romper el ciclo con capas explícitas.** Sacar el código puro a módulos nuevos, con reexport desde el original: el árbol de ámbitos (nombres, rutas, keywords, jerarquía de hijos) y la actividad de la página salen de `scope.py`; el parser de marcas y la tabla salen de `todo.py`. Los casos de uso que leen el reloj se quedan en su módulo. Meta: los imports locales pasan de 85 a una cifra que quede en el diario, y el ciclo de 11 módulos se parte.
- **P6. Una sola capa para el ámbito por defecto.** Mover `args.scope or ambito_por_defecto(...)` de `cli/todo.py` y `cli/entry.py` al caso de uso, como ya hace `todo close`. Riesgo: un test que llame `abrir_en_vault` o `add_al_vault` sin `scope` y espere un registro sin ámbito cambiaría de resultado. Se verifica antes de aplicar; si algún test lo contradice, este paso pasa a la fase 3.
- **P7. Corregir los docstrings desfasados** del punto 8. No cambia comportamiento.

Diferido a la fase 3, porque obliga a editar tests: inyectar el reloj, renombrar los nombres duplicados del punto 7 y la separación completa entre planificar y ejecutar.

## Decisiones abiertas para el autor

1. ¿P5 con reexport? Mantiene `scope.algo` y los parches de tests, a cambio de módulos que conviven con su fachada hasta la fase 3.
2. ¿P3 retira de verdad los `lint_del_vault` sin llamador? Si el autor prefiere conservarlos como API, P3 se descarta.
3. ¿P6 en la fase 2? Puede cambiar un resultado que algún test observa; si pasa, se mueve a la fase 3.

## Hipótesis para la fase 3 (tests)

Se confirman o descartan al llegar; hoy son estimaciones sobre la lectura del código.

- Con P1 y P2, las reglas de rechazo y de idempotencia de los cinco casos de uso se pueden probar una vez sobre `Arbol` y el texto de `AHORA.md`, sin `init.init`.
- Hoy 15 archivos unitarios siembran un vault; `test_scope_arbol` hace 43 llamadas a `main`, `test_scope_keywords` 23 y `test_cli_sobre_un_vault` 23.
- Para `todo open`, `todo close` y `entry create`, 17 funciones con vault (en `test_cierre_vault`, `test_cli_opciones`, `test_cli_sobre_un_vault` y `test_archivo`) bajarían a 4, más unas 12 puras. Requiere separar planificar de ejecutar y el reloj inyectado.
- `main` y los escenarios quedan para códigos de salida y delta, como pide [`tests/AGENTS.md`](../tests/AGENTS.md).
