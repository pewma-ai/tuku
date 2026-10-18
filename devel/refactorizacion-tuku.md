# Refactorización de tuku

Plan para simplificar la arquitectura del comando `tuku` y, después, acortar sus tests. Este documento permite retomar el trabajo en cualquier fase.

## Fases

1. **Auditar `tuku`.** Diagnóstico de `src/tuku/` y propuesta de mejoras. Hecha el 2026-10-18.
2. **Refactorizar `tuku`** según lo aprobado, **sin tocar los tests**. Los tests actuales son la red de seguridad: si el refactor es correcto, pasan tal cual.
3. **Revisar los tests.** Con la arquitectura ya simplificada, fundir los que afirman lo mismo. Hecha el 2026-10-18 sobre 18 archivos; ver el resultado al final.
4. **Planificar y ejecutar por separado, y reloj inyectado.** Levanta la restricción de no editar tests. Hecha el 2026-10-18 para `todo`, `entry` y `note`; ver "Resultado de la fase 4".

## Estado

- [x] Fase 1: diagnóstico (2026-10-18).
- [x] Fase 1: el autor aprobó la propuesta y delegó las decisiones al agente (2026-10-18).
- [x] Fase 2, P1 (2026-10-18): `entry.stamp` y `todo.is_registered`.
- [x] Fase 2, P2 (2026-10-18): `scope.Tree`, `read_tree` y `resolve_scope`. Recorridos de `ambitos/`: `todo open` 6 a 3, `todo close` 5 a 3, `entry create` 7 a 5 (medido contra `HEAD`, e incluyen los de `regenerate`).
- [x] Fase 2, P3 (2026-10-18): retirados cinco `lint_del_vault` sin llamador en `src`, `tests` ni docs.
- [x] Fase 2, P4 (2026-10-18): `doctor.revisar_vault` es una tabla (`_CHECKS`) de revisiones; `doctor.TEMAS` sale de ella.
- [x] Fase 2, P5 (2026-10-18): [`scope_tree.py`](../src/tuku/scope_tree.py) (231 líneas) y [`todo_core.py`](../src/tuku/todo_core.py) (601) salen de `scope.py` y `todo.py`, que los reexportan. `entry`, `todo`, `context`, `regenerate`, `fix` y `scope` importan el núcleo directamente. Ciclo de dependencias: de 11 módulos a 8. Imports dentro de funciones: de 85 a 76.
- [x] Fase 2, P6 (2026-10-18): **revertido**. Ver la propuesta.
- [x] Fase 2, P7 (2026-10-18): docstrings de `doctor`, `resultado` e `init`.
- [x] Fase 3 (2026-10-18): 192 funciones de test unitario (antes 237) y 194 casos (antes 286), con **los mismos arcos de ramas ejecutados** y los 317 tests de la suite no agéntica en verde.
- [x] Fase 4 (2026-10-18): `plan.py` con `Change` y `apply`; planners de `todo open`, `todo close`, `entry create` y `note create`; el reloj se lee solo en `cli.main`.
- [ ] Pendiente: ver "Lo que queda" al final.

## Restricciones de la fase 2

Las del reloj y de las firmas se levantaron en la fase 4.

- Ningún archivo de `tests/` cambia. Criterio de cada paso: `git diff --stat tests/` vacío, `uv run pytest` (unitarios y escenarios deterministas), `uv run ruff check .` y `uv run mypy src tests` en verde.
- Las firmas públicas que los tests usan se mantienen: `todo.abrir_en_vault`, `todo.cerrar_en_vault`, `entry.add_al_vault`, `scope.crear_con_constancia`, `note.crear_con_constancia`, `scope.rutas`, `scope.nombres`, `scope.canonico`, entre otras.
- **El reloj no se inyecta en esta fase** (levantado en la fase 4). Los tests congelan `date` y `datetime` parchando el módulo donde se leen (`entry`, `todo`, `scope`, `note`, `cycle`, `context`, `init`, `cli.opciones`; ver [`tests/scripts/tiempo.py`](../tests/scripts/tiempo.py) y `test_cli_opciones.py`). Quitar esas lecturas, o moverlas a otro módulo, rompe esos tests. Por la misma razón, el código que lee el reloj se queda en el módulo donde está hoy.
- Dividir un módulo se hace sacando código a un módulo nuevo y reexportándolo desde el original, para que `scope.algo` siga existiendo.
- **El código Python nuevo va en inglés** (identificadores, docstrings, comentarios), sin mezclar castellano. Lo existente no se renombra por esta regla. Los mensajes que ve quien invoca `tuku` siguen en español.
- Otra sesión trabaja en la misma rama: antes de editar un archivo se vuelve a leer, y no se revierte lo que no es del refactor. Con dos sesiones, un `mypy` o un `pytest` pueden fallar por el trabajo a medias de la otra o por la caché compartida (`.mypy_cache`): se repite, y si persiste se prueba con `--cache-dir` propio antes de culpar al código.
- Las decisiones de diseño que surjan en la fase 2 las toma el agente con criterio de buenas prácticas (autorizado por el autor el 2026-10-18). En un refactor eso significa conservar el comportamiento y anotar aquí lo que parezca un defecto.

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

- **P1. Un solo punto que estampa en `AHORA.md`. Hecho, con menos alcance que el previsto.** Al leer los cinco casos de uso, lo común resultó ser menos de lo diagnosticado: el orden de las validaciones y la idempotencia difieren a propósito (`todo` compara por clave en todo el archivo, `entry.add` por día y sin links, `note` por texto literal). Unificarlas cambiaría comportamiento. Se unificó lo mecánico: [`entry.stamp`](../src/tuku/entry.py) (día a encabezado, `entry.add`, `ValueError` a rechazo) en los cinco sitios, y [`todo.is_registered`](../src/tuku/todo.py) en lugar de las dos copias de `ya_abierto` y `ya_cerrado`. Salen 3 imports locales de `ahora` y 2 de `entry.add`. Los 5 sitios siguen leyendo el reloj, por la restricción de arriba. Componer la línea (`componer`, `registro_de_constancia`) sigue distinto en cada caso.
- **P2. Leer el árbol de ámbitos una vez. Hecho.** [`scope.Tree`](../src/tuku/scope.py) (nombres y rutas, inmutable) la arma `read_tree(vault)` con un solo recorrido; `resolve_scope(tree, name) -> str | Resultado` reemplaza `canonico` más `rechazo_si_no_existe` en `entry.add_al_vault`, `entry.mover_en_vault`, `todo.abrir_en_vault`, `todo.cerrar_en_vault` (dos veces), `note.crear_con_constancia` y `scope.actualizar`. `nombres(vault)` y `rutas(vault)` son envoltorios de `read_tree`, así que la lógica de recorrido existe una vez y los tests siguen igual. Sin caché global: los tests llaman `main` muchas veces en un proceso. Quedan sin migrar `canonico` en `resolver_padre`, `renombrar_en_vault` y `mover_en_vault` de `scope`, donde el árbol cambia durante la operación, y `scope.leer`, que carga también las keywords.
  - **Inconsistencia encontrada, conservada:** `todo open --scope "  "` trata un ámbito en blanco como "sin ámbito" y abre el pendiente; `entry create`, `todo close` y `note create` lo rechazan con "no existe el ámbito ''". Se conservó el comportamiento por ser un refactor. Decisión de diseño pendiente, con recomendación: rechazar en todos (un valor dado y vacío es un error de uso, no una ausencia).
- **P3. Retirar los `lint_del_vault` sin llamador. Hecho.** `grep` sobre todo el repo (no solo `src` y `tests`) confirmó que solo `note.lint_del_vault` tiene llamador (`doctor`). Se borraron las cinco restantes y `ruff` quitó 6 imports sin uso en `style.py` y `cyclelint.py`. `style.formatear` y `cyclelint.formatear` se conservan porque `doctor` los usa.
- **P4. `doctor` como tabla. Hecho.** `_CHECKS` empareja los temas con su revisión (`cycle` y `entry` comparten una porque leen `AHORA.md`); `revisar_vault` es un filtro y un formato. Los mensajes no cambian.
- **P5. Romper el ciclo con capas explícitas. Hecho en parte.** Se sacó lo que no lee el reloj ni escribe: el árbol de ámbitos (`scope_tree`: nombres, rutas, keywords, `Tree`) y el núcleo de `todo` (`todo_core`: marcas, tabla, lint en texto). Los casos de uso que leen el reloj se quedan en `scope` y `todo`. `vocab.mostrar_del_vault` pasó a `context`, que era su único llamador, y `vocab` ya no importa `config`. Quedan en el ciclo `config`, `context`, `doctor`, `entry`, `note`, `regenerate`, `scope` y `todo`: es la capa de casos de uso, que llaman a `regenerate.rehacer`. Romperla pide separar planificar de ejecutar, y eso cambia las firmas que usan los tests. `config` importa `doctor` solo por `ARCHIVOS_REQUERIDOS`; moverla a `config` rompería otro tramo, pero otra sesión está editando `config.py` y se deja para cuando termine.
- **P6. Una sola capa para el ámbito por defecto. Revertido.** Se movió `args.scope or ambito_por_defecto(...)` de `cli/todo.py` y `cli/entry.py` a los casos de uso y falló el escenario [`005-01`](../tests/escenarios/005-01-las-dos-semanas-de-andrea.md): `tuku process cycle` abre «revisar la bitácora anterior» sin ámbito a propósito, y con el default dentro del caso de uso quedaba en `personal`. El default es una decisión de quien invoca desde la línea de comandos, no de la operación. La asimetría con `todo close` es intrínseca: cerrar consulta primero el ámbito de la fila.
- **P7. Corregir los docstrings desfasados** del punto 8. Hecho para `doctor`, `resultado` e `init`.

Diferido a la fase 3, porque obliga a editar tests: inyectar el reloj, renombrar los nombres duplicados del punto 7 y la separación completa entre planificar y ejecutar.

## Decisiones tomadas

1. P5 con reexport: sí. Mantiene `scope.algo` y `todo.algo` para los tests y para quien importa.
2. P3: se retiraron las cinco, sin llamador en ningún sitio.
3. P6: se descarta (arriba). El ámbito en blanco de `todo open --scope "  "` sigue tratándose como «sin ámbito» mientras `entry create`, `todo close` y `note create` lo rechazan; queda como decisión de diseño pendiente, con la recomendación de rechazar en todos.

## Análisis de la fase 3 (plan original)

Hoy hay 237 funciones de test unitario que se recogen como 286 casos. El análisis cruza dos fuentes: la lectura de nombres y cuerpos, y la cobertura de ramas de cada test por separado (solo `src/tuku/`). Con la cobertura, 106 de los 286 casos bastan para ejecutar los mismos arcos. Eso mide que las pruebas pasan por los mismos caminos, no que sobren: una fusión conserva cada aserción y solo une lo que afirma lo mismo sobre el mismo objeto con distinto dato.

### Firmes: leídos, 27 funciones menos

| Archivo | Hoy | Después | Qué se une |
|---|---|---|---|
| [`test_scope_keywords.py`](../tests/unitarios/test_scope_keywords.py) | 15 | 6 | Pedir keywords (sin, con y sobre ámbito existente) en 1. Que una keyword no toca lo escrito (suma, crear, pendiente con keyword) en 1. Normalizar keywords (otra grafía, nombre propio, coma y espacios) en 1. Aviso por keyword repetida o por nombre de otro ámbito en 1. `rename` conserva keywords pasa a un `assert` de `scope rename` en `test_cli_sobre_un_vault`. `scope keywords ya no existe` se borra |
| [`test_regenerate_vistas.py`](../tests/unitarios/test_regenerate_vistas.py) | 7 | 3 | Funciones puras de texto con la misma tabla `PENDIENTES`: región del día (con el registro sin hora), región de la semana (con `vistas_en_ahora` y su rehecho), documento de ámbitos (con el orden de fechados) |
| [`test_scope_constancia.py`](../tests/unitarios/test_scope_constancia.py) | 2 | 1 | Misma función con y sin padre |
| [`test_style.py`](../tests/unitarios/test_style.py) | 4 | 2 | El libro completo y el encabezado que falta en 1. El barrido «todo hallazgo lleva corrección» pasa a `test_cli_contrato`, donde se une con el suyo |
| [`test_entry.py`](../tests/unitarios/test_entry.py) | 7 | 6 | Los dos tests de «sin hora» ordenan igual |
| [`test_cli_opciones.py`](../tests/unitarios/test_cli_opciones.py) | 11 | 7 | Ámbito por defecto y «sin `--at` es hoy y ahora» en 1 parametrizado. `--vault` de la opción y `scope_default` inexistente en 1. `--due` y primer escalón en 1. Los errores de opciones pasan a `test_cli_contrato` |
| [`test_cierre_vault.py`](../tests/unitarios/test_cierre_vault.py) | 6 | 3 | Cierre con marca a la vista, link en uno solo y abrir o cerrar dos veces en 1. `corregir` con links distintos pasa a `test_entry_corregir`, que ya lo cubre |
| [`test_cli_contrato.py`](../tests/unitarios/test_cli_contrato.py) | 7 | 5 | Se borra `los_cuatro_codigos_son_distintos` (compara constantes escritas a mano) y `ningun_comando_escribe_una_propuesta` (negativo histórico, cubierto por `test_manual`). El uso incorrecto absorbe los errores de opciones y el barrido de correcciones absorbe el de `test_style` |
| [`test_manual.py`](../tests/unitarios/test_manual.py) | 3 | 2 | Recorren el mismo manual y afirman sobre el mismo árbol |

Las tres funciones que se borran caen bajo la regla de [`tests/AGENTS.md`](../tests/AGENTS.md): sin historia y sin tests de más.

### Probables: 22 funciones menos, hay que leer el cuerpo antes de fundir

Salen de los nombres y de la cobertura (pares con solape de arcos igual o mayor a 0,97). No se ha leído su cuerpo.

| Archivo | Hoy | Después | Indicio |
|---|---|---|---|
| [`test_todo.py`](../tests/unitarios/test_todo.py) | 19 | 13 | Tres tests sobre «con y sin link es el mismo pendiente»; `parsear` dos veces; `canonico` y escalera; `cerrar` y `el cierre deja la marca`; dos de lint sobre la fila huérfana |
| [`test_scope_arbol.py`](../tests/unitarios/test_scope_arbol.py) | 17 | 12 | Cuatro sobre `--parent` con ruta; seis sobre hijos y callouts, con pares de solape 0,97 |
| [`test_link.py`](../tests/unitarios/test_link.py) | 11 | 8 | Tres de `convertir` y dos de `reubicar` sobre la misma función |
| [`test_links_lectores.py`](../tests/unitarios/test_links_lectores.py) | 5 | 4 | `renombrar_cambia_texto_y_ruta` repite `test_rename` |
| [`test_entry_corregir.py`](../tests/unitarios/test_entry_corregir.py) | 9 | 7 | Los dos `update` de la marca; `ubica` con `lee los registros` |
| [`test_doctor.py`](../tests/unitarios/test_doctor.py) | 10 | 8 | `sin_verbose` está contenido en `el reporte nombra lo roto`; reporte de defectos repetido |
| [`test_scope_lint.py`](../tests/unitarios/test_scope_lint.py) | 4 | 3 | `normalizar` es una función pura mal ubicada, va con las de ámbitos |
| [`test_archivo.py`](../tests/unitarios/test_archivo.py) | 7 | 5 | Escribir y conservar fecha; los dos casos de archivo cambiado |

[`test_notas_enlazables.py`](../tests/unitarios/test_notas_enlazables.py) (11, unos 3 de sobra en los `context note`) se deja para el final porque otra sesión lo está cambiando.

### Resultado esperado

- De 237 a unas 188 funciones (menos 49, un 21 %) y de 286 a unos 235 casos.
- Si `test_ejemplos` (30 casos de una función) y `test_superficie` (22) pasan de parametrizados a un recorrido con el `argv` en el mensaje, bajan unos 50 casos más sin perder aserciones, a cambio de que un fallo se reporte como un caso y no como varios.
- Reducción estructural, que depende de la fase 2 y de separar planificar de ejecutar: 17 funciones con vault (en `test_cierre_vault`, `test_cli_opciones`, `test_cli_sobre_un_vault` y `test_archivo`) bajarían a 4 más unas 12 puras. Hoy 15 archivos siembran un vault y `test_scope_arbol` hace 43 llamadas a `main`, `test_scope_keywords` 23 y `test_cli_sobre_un_vault` 23.
- No se analizaron los escenarios de `tests/escenarios/`. Los de reglas deterministas que ya cubre un unitario son el siguiente candidato.

### Cómo se ejecuta

1. Un archivo a la vez, de menor a mayor riesgo, empezando por los firmes.
2. Antes y después de cada archivo se mide el conjunto de arcos que ejecuta toda la capa unitaria: tiene que ser el mismo, o mayor. Es la red que dice que no se perdió un camino.
3. Cada aserción de un test fundido sobrevive, salvo las de los tres tests que se borran.
4. `pytest`, `ruff` y `mypy` en verde por archivo; commit solo si el autor lo pide.
5. Si el análisis de cobertura debe repetirse, el plugin de `pytest` que registra los arcos de cada test es corto (un `hookwrapper` sobre `pytest_runtest_call` con `coverage.Coverage(include=["*/src/tuku/*"], config_file=False)`); no está versionado.

## Resultado de la fase 3

Medido con un plugin de `pytest` que registra los arcos de `src/tuku/` que ejecuta cada test. La unión de arcos de la capa unitaria es la misma antes y después (4572, ninguno perdido), y la suite no agéntica pasa entera (317 tests, escenarios incluidos).

| Archivo | Antes | Después | Qué se unió |
|---|---|---|---|
| `test_scope_keywords.py` | 15 | 6 | pedir keywords; que una keyword no toca lo escrito; normalizar y no repetir; aviso por keyword repetida. `scope keywords ya no existe` se borró |
| `test_todo.py` | 19 | 13 | `parsear`; `abrir`; horizonte y escalera; links y espacios al buscar un pendiente (tres tests); lint con comando |
| `test_scope_arbol.py` | 17 | 13 | `--parent` con ruta (cuatro tests); renombrar el padre dentro del rename anidado |
| `test_regenerate_vistas.py` | 7 | 3 | regiones; `vistas_en_ahora`; documento de ámbitos |
| `test_cli_contrato.py` | 7 | 4 | se borraron `los_cuatro_codigos_son_distintos` y `ningun_comando_escribe_una_propuesta`; el uso incorrecto pasó a `test_cli_opciones` |
| `test_cli_opciones.py` | 11 | 9 | recibió el uso incorrecto; salió `abrir_abreviado` (lo cubre `sin_day_ni_hour`); `scope_default` en 1 |
| `test_entry_corregir.py` | 9 | 7 | `registros` y `ubicar`; dos `update` |
| `test_link.py` | 11 | 9 | `convertir` (lo que deja intacto) y `reubicar` |
| `test_doctor.py` | 10 | 8 | `formatear` (dos); vault completo y vault con defectos |
| `test_cierre_vault.py` | 6 | 4 | cerrar y abrir con y sin link |
| `test_archivo.py` | 7 | 5 | `escribir` (permisos y fecha); cambio ajeno dentro y fuera de un intento |
| `test_style.py`, `test_scope_lint.py`, `test_cli_sobre_un_vault.py`, `test_links_lectores.py`, `test_manual.py`, `test_entry.py`, `test_scope_constancia.py` | 31 | 24 | una fusión cada uno; `normalizar` y los dos tests de nombre de ámbito pasaron a uno solo |
| `test_ejemplos.py`, `test_superficie.py` | 52 casos | 2 casos | de parametrizado a recorrido, con el ejemplo o la ruta en el mensaje de fallo |

La capa unitaria corre en unos 4 s (antes 4,5 s).

## Resultado de la fase 4

**Reloj.** `cli.main(argv, *, now=None)` lee `datetime.now()` una vez y lo deja en `args.now`; los handlers lo pasan como `now` a los casos de uso. Ningún otro módulo de `src/tuku/` llama a `date.today()` ni a `datetime.now()`. Las firmas cambian:

| Función | Antes | Ahora |
|---|---|---|
| `entry.add_al_vault`, `todo.abrir_en_vault`, `todo.cerrar_en_vault`, `note.crear_con_constancia`, `scope.crear_con_constancia` | leían el reloj | `now: datetime` obligatorio |
| `note.renombrar_en_vault` | `hoy: date \| None` | `now: datetime` |
| `context.del_vault` | `hoy: date \| None` | `now: datetime` |
| `cycle.abrir_en_vault` | `fecha` o hoy | `fecha` o la de `now`; `cycle.open_cycle` exige la `fecha` |
| `init.init` | `desde` o hoy | `desde: date` obligatorio; el CLI pasa `args.at.dia or args.now.date()` |
| `todo.avisos_de_plazo` | leía el reloj | recibe `now` |
| `cli.opciones` | las funciones `type=` de argparse leían el reloj | `momento_pasado` y `momento_futuro` solo parsean; `Momento.con_reloj(now)` completa la hora sola y el año que falta, y `main` lo aplica a `--at` y `--due` (`opciones.completar`) |

`tests/scripts/tiempo.py` ya no parchea módulos: `tiempo.instante("AAAA-MM-DD HH:MM")` devuelve el `datetime` que el arnés y el shim del agente pasan como `now`. Los tests unitarios usan la constante `AHORA` de [`conftest.py`](../tests/conftest.py) (miércoles 12 de agosto de 2026, 09:00).

**Planificar y ejecutar.** [`plan.py`](../src/tuku/plan.py) define `State` (lo que se lee: árbol de ámbitos, `AHORA.md`, `PENDIENTES.md`, horizontes y ámbito por defecto), `Change` (textos nuevos por ruta, mensaje, avisos, rutas a regenerar y páginas de ámbito a rehacer) y `apply`, el ejecutor único: escribe solo lo que difiere del disco, llama a `regenerate.rehacer` (con `skip=("todo",)` para `--no-regenerate`) y devuelve el `Resultado`. Cada caso de uso quedó en tres pasos: leer el estado, `plan_*` (puro) y `apply`.

| Planner | Caso de uso |
|---|---|
| `entry.plan_add` | `entry.add_al_vault` |
| `todo.plan_open` | `todo.abrir_en_vault` |
| `todo.plan_close` | `todo.cerrar_en_vault` |
| `note.plan_create` | `note.crear_con_constancia` (con `note.compose`, que reemplaza a `note.crear`) |

`scope_tree.Tree` suma `scopes` (los ámbitos con página) para que el rechazo de «no existe el ámbito» no vuelva a leer el disco.

**Tests.** Los de preparación (`test_context`, `test_entry_corregir`, `test_doctor`, `test_scope_create_since`, `test_notas_enlazables`, `test_opciones`, `test_cli_*`) pasan `now=AHORA` o `main(..., now=AHORA)`; los fixtures que sembraban con `date.today()` siembran con `AHORA.date()`. El nuevo [`test_plan.py`](../tests/unitarios/test_plan.py) prueba las reglas de rechazo, idempotencia, ámbito del cierre, horizonte y plazo sobre texto (12 funciones para `todo` y `entry`, 3 para `note`) y el ejecutor una vez sobre un vault. De las 17 funciones con vault de `test_cierre_vault`, `test_cli_opciones`, `test_cli_sobre_un_vault` y `test_archivo` quedan 5 (`entry update` con links distintos, que ahora vive en `test_entry_corregir`; el ámbito por defecto y el `now` de `main`; el rechazo sin dejar nada a medias; el nombre de un ámbito; `scope rename`) y `test_cierre_vault.py` desaparece. `test_archivo` ya no siembra un vault. `test_los_avisos_proceden_y_alertan_por_stderr` pasó a `traducir`, sin vault.

La unión de arcos de la capa unitaria es la de antes más 13 arcos nuevos, ninguno perdido. Los nuevos son rechazos que ningún unitario ejercía: un día fuera del ciclo en `plan_add` y `plan_open`, un ámbito inexistente en `plan_open` y `plan_close`, y un `AHORA.md` sin salto final en `entry.add`. La suite no agéntica falla en los mismos 30 escenarios que antes de empezar (`002-13` y la cadena `005`): usan `tuku process cycle --from`, que el código todavía no tiene. Como esos fallos cortan las cadenas en su primer paso, se corrieron los 65 escenarios en una copia con `--from` cambiado por `--at`: pasan los 65 antes y después de la fase. 196 funciones de test unitario (192 al cerrar la fase 3, más 16 de `test_plan` y menos 12 que dejaron de hacer falta).

**Decisiones.**

- `Momento` parsea sin reloj y se completa después: así el parser de argparse, que se construye una vez por proceso, no depende de hoy.
- `scope.actualizar_contenido_pagina` ya no cae a `date.today()` cuando `AHORA.md` no trae ciclo y nadie le pasa `hoy`: sin fecha de referencia omite el encabezado de mes de `## Actividad reciente`. Ningún test ejercía esa rama; `crear_con_constancia` sigue pasando la fecha de `now`.
- `init.init` y `cycle.open_cycle` piden la fecha en vez de un `now`: son funciones que no necesitan la hora.
- El orden de un rechazo cambia solo en un vault roto: el caso de uso lee `AHORA.md` y `PENDIENTES.md` antes de planear, así que un vault sin `PENDIENTES.md` falla con «no parece un vault» aun si la fecha del pedido también era futura.

## Lo que queda

- **`scope.crear_con_constancia` sigue entero en el caso de uso.** Su salida depende del disco después de escribir (carpetas del padre, callout de hijos, `parent:` de cada página, bitácoras cerradas y keywords de todos los ámbitos para el mensaje y los avisos), así que un planner puro pide un `State` mucho mayor y un `Change` con operaciones de carpeta. Queda para una fase propia, con `scope move` y `scope rename`, que comparten ese tramo.
- **`test_notas_enlazables.py`** (11, unos 3 de sobra en los `context note`): otra sesión lo está cambiando; esta fase solo le agregó `now=AHORA`.
- **`config` importa `doctor`** por `ARCHIVOS_REQUERIDOS`: mover la constante a `config` cuando `config.py` deje de estar en edición.
- **El ámbito en blanco** de `todo open --scope`: ver las decisiones tomadas.
- **Escenarios de `tests/escenarios/`:** no se analizaron para fusionar. Los 30 que fallan esperan `process cycle --from`.
- **`entry.actualizar_en_vault` y `entry.mover_en_vault`** siguen mezclando decisión y escritura; son los candidatos siguientes a un planner, después de `scope`.
