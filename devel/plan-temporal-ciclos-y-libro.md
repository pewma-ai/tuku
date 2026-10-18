# Plan temporal: del CLI nuevo a los ciclos con nombre y el libro de estilo

> Archivo temporal del 2026-10-18. Existe para que una sesión nueva retome el trabajo sin el historial de esta conversación. Cuando los pasos estén hechos o movidos a su lugar definitivo, se borra. Lo que debe sobrevivir ya vive en [`../TODO.md`](../TODO.md), [`../spec/`](../spec/) y [`iteraciones/`](iteraciones/).

## Para qué sirve

El autor trabaja por turnos (turno en Paranal de martes a martes, descanso de miércoles a lunes, con variaciones de 10 o 14 días) y el CLI de `tuku` asume la semana de lunes a domingo. La sesión anterior dejó escritas las specs de un ciclo con nombre y rango, de los horizontes que usan `$cycle_name[N]`, de un libro de estilo estático, y de las cadencias por comando. El código todavía no lo hace. Este plan ordena lo que falta.

## Reglas de trabajo

Estas reglas son del autor y valen para toda la sesión.

- **Si algo difiere de este plan, se consulta al autor antes de cambiarlo.** Las decisiones de diseño son suyas.
- **Responder en español neutro, sin voseo, conciso.** Markdown sin saltos manuales en párrafos y sin raya (—). Frases afirmativas en los tests.
- **No tocar ningún `AGENTS.md`**, ni el del repo ni el del template. Son el resultado de un comando, no se editan.
- **Lo que pueda ser determinista lo hace un comando de `tuku`**, no el autor a mano ni el `AGENTS.md`.
- **No hay retrocompatibilidad.** Se cambia el nombre y se cambian todos los usos.
- **No correr tests agénticos.** Solo `uv run pytest tests/unitarios -q` y `uv run pytest tests/escenarios -m "not agentic" -q --no-header`.
- **El agente de esta sesión tiene el control de git**, y el autor edita archivos chicos desde Obsidian. Antes de editar, `git status --short`. Nunca `git stash` ni `git checkout --` sobre archivos con cambios ajenos. Se commitea y se pushea por paso terminado, y el mensaje cierra con `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- **`spec/tuku.md` es lo correcto**: el CLI debe representarlo, salvo lo marcado como pendiente (gris). Lo edita el otro agente del autor, que trabaja en otra ventana: se le pide el cambio antes de tocarlo, salvo que el autor diga lo contrario.
- **Las iteraciones son un resumen del estado final**, no una bitácora de pasos: [`iteraciones/2026-10-18.md`](iteraciones/2026-10-18.md) se reescribe, no se apila.
- **Los hooks de pre-commit** corren ruff, mypy y los unitarios, y regeneran `src/tuku/_home`. No se saltan.
- **`ruff format` sobre `src` reformatea archivos ajenos.** Formatear solo los archivos propios.

## Estado de partida

Medido el 2026-10-18 al cierre de la sesión anterior:

| Suite | Resultado |
| --- | --- |
| `tests/unitarios` | 271 verdes |
| `tests/escenarios`, no agénticos | 8 rojos: B1 ×2 (`005-04`), B2 ×4 (`005-05`) y A6 ×2 (`002-14`); el resto verde |

Hecho en la sesión anterior, commiteado y pusheado:

- Specs: [`ciclo.md`](../spec/ciclo.md) (nombre y rango del ciclo, "Abrir el siguiente ciclo"), [`pendientes.md`](../spec/pendientes.md) (horizontes con `$cycle_name[N]`), [`vault.md`](../spec/vault.md) (libro estático, `cycle_name`), [`cadencias.md`](../spec/cadencias.md) y [`bitacora.md`](../spec/bitacora.md).
- [`spec/tuku.md`](../spec/tuku.md): firma `tuku process cycle [--from] [--to] [--name] [--force]` marcada como pendiente, con `--at` en "Lo que se retira".
- Dos tests en rojo a propósito en [`002-14`](../tests/escenarios/002-14-casos-borde.md), registrados como A6 en [`005-00`](../tests/escenarios/005-00-el-dia-ciento-cincuenta.md).
- La sección "Ciclos con nombre, config y libro de estilo" de [`TODO.md`](../TODO.md).

## Los pasos, en el orden decidido

El autor decidió este orden. Los pasos 5 a 9 no se empiezan sin una conversación previa sobre la configuración, que el autor tiene con el agente. Los pasos 3 y 4 están hechos: la sesión que los hizo se detuvo aquí.

| # | Paso | Estado |
| --- | --- | --- |
| 1 | Spec de ciclos, libro, horizontes y cadencias | Hecho |
| 2 | Refactor del CLI del autor, que coincide con `spec/tuku.md` | Hecho |
| 3 | Reconciliar `005-00` con el CLI nuevo | Hecho el 2026-10-18 |
| 4 | El resto de los pendientes de `005-00` | Hecho salvo B4 (falta el nombre del verbo de postergar), D1 y D2 (los reserva el autor) y E2 (espera al paso 7); C1 espera medirse con `005-06` |
| | **Detenerse aquí.** El autor conversa con el agente sobre `reglas/config.tuku.md` | |
| 5 | Conversación sobre `config.tuku` | Del autor con el agente |
| 6 | Ciclo con nombre en código | Depende del 5 |
| 7 | Horizontes por posición y con `$cycle_name[N]` | Depende del 6 |
| 8 | Libro de estilo estático y archivos del autor | Depende del 5 y el 7 |
| 9 | Comando de cadencias | Lo escribe el autor, después del 8 |

### Paso 3. Reconciliar 005-00 con el CLI nuevo

La sección "Pendientes del epic" de [`005-00`](../tests/escenarios/005-00-el-dia-ciento-cincuenta.md) se escribió con el CLI anterior. El autor rediseñó la superficie el 2026-10-18 y varios pendientes quedaron resueltos o cambiaron de nombre. Cada pendiente resuelto se tacha con `~~así~~` y se deja una línea con la resolución, sin borrarlo (qué hacer con la lista al cerrar el epic se decide después).

Qué verificar contra [`spec/tuku.md`](../spec/tuku.md) y [`spec/cli.md`](../spec/cli.md), pendiente por pendiente:

- **S5** (`--at` significa tres cosas): resuelto en `cli.md` ("`--at`: cuándo ocurrió, nunca ubica qué corregir"). `entry rename --at` pasó a `entry update`/`entry move` con `--match`. Falta `process cycle`, que pasa a `--from`/`--to` (paso 6).
- **S6** (sin comandos de lectura): `tuku context`. Confirmar si cubre `todo list`, `scope tree` y `note list`.
- **S7** (destino de los lint): `tuku doctor TEMA [ARCHIVO]`. Los `lint` se retiraron.
- **S8**: `init DIR` posicional y `tuku_template` frente a `--variant` queda para la conversación del paso 5.
- **S9** (escenario de superficie): `tests/unitarios/test_superficie.py` compara firmas con argparse. Decidir con el autor si eso basta o falta un escenario con `tuku -h`.
- **A2**: resuelto por el refactor (`note.lint_del_vault` ya no cuenta `notas/AGENTS.md`).
- **A6** (nuevo): `entry update` sobre un pendiente. Ya está en la tabla.

Además, los escenarios y tests que invocan comandos retirados (`cycle open`, `entry rename`, `*lint`) deben usar los nuevos. El refactor ya cambió `001-07`, `002-13` y `005-01`: comprobar que no quede ningún uso con `rg -n "(entry|todo|scope|cycle|note|style) lint|cycle open|entry rename|vocab show" tests devel/epics.md docs spec template`.

Se termina cuando: la suite no agéntica tiene los mismos rojos que al partir (8) y ningún pendiente resuelto queda sin tachar.

### Paso 4. El resto de los pendientes de 005-00

Orden acordado, de lo independiente a lo que depende de decisiones:

1. **A3**: `doctor note` no mira los enlaces del cuerpo; `spec/notas.md` pide que la nota cierre con la lista de sus enlaces salientes, cada uno con motivo.
2. **A6 (corrección)**: `entry update` sobre un pendiente debe conservar `**pendiente**:`, actualizar la fila y `doctor todo` debe nombrar una fila sin registro pendiente. Los dos tests ya están escritos en `002-14`.
3. **B2** (nota tipada, `--subtype persona`, `reglas/tipos/persona.md`): depende de confirmar X2 con el autor.
4. **B3**: keywords repetidas entre ámbitos pasan sin aviso.
5. **B5**: el mensaje de rechazo de `process cycle` con un ciclo con registros dice «mueve AHORA.md a bitacoras/…» y, seguido al pie de la letra, deja links rotos en la bitácora (bajan un nivel).
6. **B1** (atrasados) y **B4** (postergar): dependen de X1 y de cómo ruede un horizonte, que depende del paso 7. B1 se puede hacer primero por fecha (`Vence`); el atraso por horizonte expirado (E2) espera al paso 7.
7. **C1/X4** (el agente elige entre dos Paulas sin preguntar), **D1 a D6** (documentos que se contradicen; D1 y D2 son de `devel/epics.md` y el autor los reserva) y **E1 a E3** (tests): al final.
8. **Decisiones X1 a X5**: confirmarlas con el autor una por una antes de implementar lo que usan.

Cada pendiente terminado: test en verde, tachado en `005-00`, una línea en la iteración, commit y push.

### Paso 5. La conversación sobre `reglas/config.tuku.md`

No es trabajo de código. Temas que ya están sobre la mesa (ver [`TODO.md`](../TODO.md), "La conversación sobre `reglas/config.tuku.md`"):

- `cycle_name` y su lista: hoy la tabla de la config solo tiene campos de un valor.
- Qué comandos pasan a leer los archivos de datos del autor en vez de las tablas del libro de estilo (`vocab.py`, `context.py`, `todo.py`).
- `tuku_template` frente a `--variant` (S8).
- Qué escalón es el del ciclo en curso cuando la escalera lista varios `este …` (propuesta: el que tiene el índice del ciclo en curso).

### Paso 6. Ciclo con nombre en código

Decidido (detalle en [`spec/ciclo.md`](../spec/ciclo.md), "Abrir el siguiente ciclo", y en `TODO.md`):

- `cycle_name` reemplaza a `cycle_type`; lista, `semana` por defecto.
- El frontmatter de `AHORA.md` y de la bitácora lleva `cycle: turno`. El siguiente ciclo es el siguiente de la lista y vuelve al primero.
- `tuku process cycle [--from] [--to] [--name] [--force]`. `--at` se retira. Con `semana`, `--from` es un día cualquiera de la semana y `--to` se deduce; con otro nombre `--to` es obligatorio. Sin `--from`, el ciclo empieza el día siguiente al `to` del anterior.
- Un `from` distinto del día siguiente al `to` anterior se rechaza, salvo repetir el ciclo abierto con su mismo `from`, que solo verifica y, sin registros, lo regenera.
- `--name` fija el nombre. Fuera de `cycle_name` se rechaza sin escribir, y se repite con `--force` tras confirmarlo con el autor (caso real: "Viaje a Praga").
- La bitácora cerrada se llama `bitacora-<desde>-<hasta>-<ciclo>.md`.
- La plantilla genera un encabezado por cada fecha del rango, no siete fijos.

Cambios al implementar: `src/tuku/cycle.py`, `process.py`, `config.py`, `doctor.py` (campo requerido), `cyclelint.py`, el template (`reglas/config.tuku.md`, `reglas/plantilla/AHORA.md`, `ambitos/CADENCIAS.md`), `tests/unitarios/test_cycle_open.py` y los escenarios `002-13` y `005-01`. Al terminar, quitar `--at` de "Lo que se retira" de `spec/tuku.md` y los `# pendiente` de la firma.

### Paso 7. Horizontes por posición y con `$cycle_name[N]`

- **Defecto a corregir primero:** [`regenerate.py`](../src/tuku/regenerate.py) selecciona los pendientes del callout del ciclo por el texto literal `esta semana` (`todo.ESTA_SEMANA`), y `todo open` usa esa constante de valor por defecto. Renombrar el primer horizonte deja el callout vacío sin aviso.
- Después, `$cycle_name[N]` con cualquier índice. `este X` solo vale si el ciclo en curso se llama X; fuera de eso es un error del autor: rechazo sin escribir que nombra la corrección, y el agente desambigua. `próximo X` es el siguiente ciclo con ese nombre, pasando por los demás. `fin de mes` es el último día menos uno.
- El callout se titula con el horizonte (`Pendientes de este turno`).

### Paso 8. Libro de estilo estático y archivos del autor

[`LIBRO-DE-ESTILO.md`](../template/vanilla/LIBRO-DE-ESTILO.md) pasa a ser prosa de TUKU, estática y regenerada con `tuku regenerate`, que vive en el vault. Los datos del autor viven en `reglas/` (`autor.md`, `clasificaciones.md`, `horizontes.md`, `types.md`, reglas de escritura propias) y el libro los transcluye. Detalle en [`spec/vault.md`](../spec/vault.md), "El libro de estilo". Riesgos: un editor básico ve enlaces en vez de tablas (lo cubre `tuku context style`), y quien edite el libro a mano pierde el cambio (una revisión de `doctor` debe avisar).

### Paso 9. Comando de cadencias

Lo escribe el autor. Combina todos los `CADENCIAS.md` del árbol en cascada y los devuelve en un solo texto, cada cadencia con el archivo de origen. Candidato de nombre: `tuku context cadence`. El libro dice el mecanismo y manda a buscar en `ambitos/`.

## Archivos que la sesión nueva debe leer antes de empezar

Leer completos, en este orden:

1. [`../AGENTS.md`](../AGENTS.md) y [`../DEVEL.md`](../DEVEL.md): reglas del repo y cómo se desarrolla.
2. [`../tests/AGENTS.md`](../tests/AGENTS.md) y [`../tests/README.md`](../tests/README.md): capas de tests y lenguaje.
3. Este archivo.
4. [`../TODO.md`](../TODO.md), secciones "Superficie del CLI" y "Ciclos con nombre, config y libro de estilo".
5. [`../spec/tuku.md`](../spec/tuku.md) y [`../spec/cli.md`](../spec/cli.md): la superficie correcta y su gramática.
6. [`../tests/escenarios/005-00-el-dia-ciento-cincuenta.md`](../tests/escenarios/005-00-el-dia-ciento-cincuenta.md), sección "Pendientes del epic" y "Decisiones por confirmar".
7. [`iteraciones/2026-10-18.md`](iteraciones/2026-10-18.md): lo que hizo el refactor del CLI.

Leer cuando el paso lo pida:

- Pasos 6 y 7: [`../spec/ciclo.md`](../spec/ciclo.md), [`../spec/pendientes.md`](../spec/pendientes.md), [`../spec/vault.md`](../spec/vault.md) ("La configuración"), `src/tuku/cycle.py`, `process.py`, `config.py`, `regenerate.py`, `todo.py`, `doctor.py`, `cyclelint.py`.
- Paso 8: [`../spec/vault.md`](../spec/vault.md) ("El libro de estilo"), [`../spec/bitacora.md`](../spec/bitacora.md) (vocabularios), `src/tuku/vocab.py`, `style.py`, `context.py`.
- Paso 9: [`../spec/cadencias.md`](../spec/cadencias.md), [`../spec/ambitos.md`](../spec/ambitos.md).
- Para entender el caso real del autor: `/Users/jgil/Code/MaC/mac-jpgil/estrategia/Capacidad.md` (turnos Mar-Mar, descanso Mié-Lun).

Memoria que la sesión carga sola y conviene tener presente: `ciclos-por-turnos-del-autor`, `lo-determinista-lo-hace-tuku`, `iteracion-es-resumen`, `lenguaje-de-tests-afirmativo`, `commit-y-push-por-test`, `unit-tests-para-lo-determinista`, `markdown-sin-em-dash-ni-wrap`.

## Cómo se verifica

```bash
uv run pytest tests/unitarios -q
uv run pytest tests/escenarios -m "not agentic" -q --no-header
uv run ruff check src tests
uv run mypy src tests
```

La suite de escenarios tarda unos 50 segundos. `tests/unitarios/test_superficie.py` compara cada firma de `spec/tuku.md` con el árbol de argparse y dice qué línea cambiar.

## Preguntas abiertas para el autor

- Cuál de dos escalones `este …` es el del ciclo en curso (propuesta: el de índice igual al del ciclo actual).
- Si basta `test_superficie.py` como escenario de superficie (S9) o se escribe uno con `tuku -h`.
- Las decisiones X1 a X5 de `005-00`.
- Qué es archivar una nota, y la spec de archivar ramas de ámbito (epic 006): [`../spec/README.md`](../spec/README.md).
- Dos categorías con el mismo nombre en ámbitos distintos (`negocio/clientes` y `casa/clientes`) no las detecta ningún lint.

## Al terminar

Mover lo que siga vigente a [`../TODO.md`](../TODO.md) o a la iteración del día y borrar este archivo.
