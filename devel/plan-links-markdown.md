# Plan · links Markdown y `tuku fix` (bloque B)

Plan para ejecutar en una sesión aparte. Describe el estado final; el cómo lo decide quien ejecuta. Antes de empezar, leer [`DEVEL.md`](../DEVEL.md), [`AGENTS.md`](../AGENTS.md) y la última iteración en [`iteraciones/`](iteraciones/).

## Decisiones del autor (2026-10-16)

1. **Links Markdown con ruta relativa al archivo:** `[texto](ruta/relativa.md)`. Nada de rutas desde la raíz del vault.
2. **La transclusión de Obsidian es parte del estándar de TUKU:** `![[archivo.md#^ancla]]` se queda, igual que los callouts `> [!todo]`. Es el único wikilink admitido, y se reconoce por el `!` inicial.
3. **`tuku doctor TEMA` y su par `tuku fix TEMA`:**
   - `tuku doctor` sin tema revisa todo, como hoy. Con tema, revisa solo ese.
   - Todo tema tiene su `fix`, y cada hallazgo del tema nombra `tuku fix TEMA` como corrección.
   - Si el arreglo es determinista, `fix` lo aplica.
   - Si no lo es, `fix` no escribe y sale con las decisiones de alto nivel que hay que tomar, porque quien corre TUKU es un agente y esas decisiones son del autor.
4. **Solo un tema por ahora, `link`.** Un tema existe cuando tiene un `fix` que hacer. Las demás revisiones del doctor siguen saliendo en `tuku doctor` sin tema, y su corrección sigue siendo el comando original o una tarea del autor. Un tema nuevo entra cuando un epic encuentra un caso real que lo pida.
5. **La conversión de wikilinks porta el script de mac-jpgil** (`/Users/jgil/Code/MaC/mac-jpgil/procesos/scripts/jntr.obsidian-links-to-markdown.py`), modificado para que no rompa las transclusiones. El código queda dentro de `src/tuku`: TUKU no depende de mac-jpgil en ejecución.
6. **Sin `.obsidian`:** el template no trae configuración de Obsidian. Obsidian, con su configuración por defecto, escribe wikilinks cuando el autor enlaza a mano, así que `doctor link` y `fix link` son un flujo recurrente, no una migración de una sola vez.
7. **Los lectores aceptan los dos formatos y los escritores solo producen Markdown.** Un vault con wikilinks sigue funcionando hasta que se corre `fix link`: `entry lint`, `scope lint`, `rename`, la propagación y el parser de `PENDIENTES.md` reconocen `[[x]]` y `[x](ruta)`.
8. **`fix link` alcanza todo el vault, incluidos los ciclos cerrados de `bitacoras/`.** Cambia el formato sin agregar enlaces, así que es una reparación y no un enriquecimiento del pasado ([spec/ambitos.md](../spec/ambitos.md), "El enlazado retroactivo").
9. **Un `fix` con hallazgos mixtos** aplica lo determinista, deja intacto lo que requiere decisión y sale con 1 (`RECHAZO`) listando esas decisiones. Cada cambio aplicado queda completo: nada a medias por archivo.
10. **Un `fix` que cambia solo la forma, y no el contenido, conserva la fecha de última modificación del archivo.** Convertir `[[x]]` a `[x](ruta)` no es una edición del autor, y la fecha de modificación es la que Obsidian y el sistema de archivos usan para ordenar lo reciente.
11. **Nombres en inglés:** los temas y las etiquetas internas de las revisiones del doctor (`Revision` en [`doctor.py`](../src/tuku/doctor.py)) van en inglés. Hoy `archivos`, `despacho` y `consecuencias` están en español; pasan a `files`, `dispatch` y `consequences`.
12. **`tuku link backfill` y el sustantivo `link` se eliminan.** `tuku scope create` ya hace ese enlazado ([scope.py:405](../src/tuku/scope.py)) y es idempotente. `link` sigue existiendo como tema del doctor, no como sustantivo del CLI.
13. **El escenario nuevo va como `002-10`.** El epic 002 está cerrado, pero el cambio afecta a todo lo que el 002 escribe a mano.
14. **Toda ayuda `tuku … -h` explica para qué existe el comando:** un párrafo en español, como `description` de argparse, en cada sustantivo y en cada verbo. La línea corta de `help=` y el `epilog` "A mano" se mantienen.

## Estado final

### Spec (primero, antes del código)

- [`spec/README.md`](../spec/README.md): la decisión abierta "Pasar de wikilinks de Obsidian a links Markdown" pasa a decisión tomada, con los puntos de arriba.
- [`spec/cli.md`](../spec/cli.md):
  - **La pareja `doctor`/`fix`.** Verificar y reparar siguen separados: ningún comando de verificación repara, y `tuku fix TEMA` es el verbo que repara.
  - **Lo no determinista se devuelve como decisiones, sin escribir.** La salida dice qué hay que decidir, entre qué opciones y qué comando correr una vez decidido.
  - **Los códigos de salida de `fix`:** 0 si el tema quedó sano, 1 si quedan decisiones.
  - **La fecha de modificación** se conserva cuando el cambio es solo de forma.
  - **Cuándo entra un tema nuevo** (decisión 4).
  - **La regla de la ayuda** (decisión 14).
- [`spec/bitacora.md`](../spec/bitacora.md): la línea canónica es `- HH:MM - [ambito](ruta) **marca**: cuerpo`. La ruta es relativa al archivo que contiene la línea, y la calcula `tuku` a partir del árbol (un ámbito anidado lleva su ruta completa). Se actualizan los ejemplos.
- [`spec/ambitos.md`](../spec/ambitos.md):
  - la transclusión queda declarada como extensión de Obsidian aceptada;
  - "A mano" escribe links Markdown;
  - `link backfill` sale de la lista de `## El nombre de un ámbito`;
  - el renombrado actualiza el texto y la ruta de cada link.
- [`spec/notas.md`](../spec/notas.md) y [`spec/pendientes.md`](../spec/pendientes.md): los links a notas y a ámbitos, en Markdown.
- [`spec/despacho.md`](../spec/despacho.md) y [`spec/flujo-informacion.md:103`](../spec/flujo-informacion.md): sin `link backfill`, y con `fix` donde hoy se dice que el doctor solo informa.
- El archivado a `bitacoras/` (epic 006) queda especificado como responsable de recalcular las rutas relativas. No se implementa ahora.

### Código

- **Un solo módulo de núcleo puro para los links:** componer un link relativo entre dos rutas, reconocer los dos formatos y distinguir un embed (`![[...]]`) de un wikilink. Ningún otro módulo arma ni parsea links por su cuenta.
- **El port del script de mac-jpgil** va en ese núcleo, con estos cambios:
  - **Respetar los embeds:** su regex `\[\[([^\]]+)\]\]` captura también los `![[...]]` y los convertiría en `![texto](ruta)`, que es una imagen. Un `[[` precedido de `!` no se toca.
  - **Respetar el código:** se ignoran el código inline, como ya hace, y los bloques de código, si el script no lo hace.
  - **Sin disco en el núcleo:** el núcleo recibe texto y el índice de archivos del vault. El recorrido del disco va en el caso de uso.
- **Escritores, todos en Markdown:**
  - [`entry.py:113`](../src/tuku/entry.py)
  - [`note.py`](../src/tuku/note.py) (líneas 78 y 104-105)
  - [`todo.py:98`](../src/tuku/todo.py)
  - [`propagate.py`](../src/tuku/propagate.py) (líneas 66 y 73)
  - la página y el lint de [`scope.py`](../src/tuku/scope.py) (líneas 148-158 y 306)
  - el enlazado que `scope create` hace hoy con [`link.py`](../src/tuku/link.py)
  - [`rename.py`](../src/tuku/rename.py), donde renombrar cambia texto y ruta
  - los textos de ayuda y los `epilog` "A mano" de `cli/*.py`
- **`tuku doctor [TEMA]`:**
  - sin tema, se comporta como hoy, más la revisión `link`;
  - con tema, corre solo esa revisión;
  - un tema desconocido es error de uso y sale con 2 (argparse, con `choices`);
  - cada hallazgo de `link` nombra `tuku fix link`.
- **Revisión `link`:** reporta como `archivo:línea` cada wikilink sin `!` y cada link Markdown cuya ruta no existe, sin contar el código.
- **`tuku fix link`:**
  - convierte `[[nombre]]`, `[[nombre|alias]]` y `[[nombre#ancla]]` en `[texto](ruta.md#ancla)`, resolviendo el nombre contra los archivos del vault;
  - un nombre que no resuelve, o que resuelve a más de un archivo, se deja como está y sale como decisión: qué archivo es, o si se crea;
  - un link Markdown roto también sale como decisión;
  - conserva la fecha de modificación de cada archivo que toca;
  - una segunda corrida no cambia nada.
- **Sin el sustantivo `link`:** se quitan `link backfill` y su handler. La función de enlazado retroactivo sigue en el núcleo para `scope create`.
- **Las etiquetas de las revisiones del doctor, en inglés** (decisión 11).
- **Un párrafo de `description` en cada parser** de sustantivo y de verbo (decisión 14). Hoy ninguno lo tiene: solo el parser raíz.

### Template

- [`template/vanilla/`](../template/vanilla/) ya no tiene wikilinks salvo las transclusiones. Archivos con `[[` hoy:
  - `LIBRO-DE-ESTILO.md`
  - `reglas/bitacora.tuku.md`
  - `notas/AGENTS.md`
  - `ambitos/AGENTS.md`
  - `ambitos/CADENCIAS.md`
  - `ambitos/PENDIENTES-AMBITOS.md`
  - `ambitos/personal/personal.md`
- [`template/vanilla/AGENTS.md`](../template/vanilla/AGENTS.md) dice en una línea que, ante un hallazgo del doctor que nombre `tuku fix`, se corre, y que si `fix` devuelve decisiones, se le plantean al autor y se espera su respuesta. Es producto, se edita sin pedir permiso. Mantener el recorte del 2026-10-15: una línea, sin justificar.

### Docs

- [`docs/tutorial/02-el-primer-dia.md`](../docs/tutorial/02-el-primer-dia.md) le enseña al lector a buscar wikilinks: "entre corchetes dobles al inicio de cada línea" (sección "Un frente nuevo"), "lo enlazan como `[[colegio-los-robles]]`" y "no queda ni un `[[colegio-los-robles]]`" (sección "Cuando quedó mal dicho"). Pasan a describir links Markdown.
- [`docs/glosario.md`](../docs/glosario.md): **Transclusión** sigue con `![[archivo#^ancla]]`, y declara que es el único wikilink admitido.
- El texto de los escenarios [`003-08`](../tests/escenarios/003-08-el-mismo-vault-otro-arnes.md) y [`003-09`](../tests/escenarios/003-09-el-mismo-vault-tercer-arnes.md) dice "un registro a las 09:12 en `[[personal]]`"; pasa a Markdown junto con sus afirmaciones.

### Tests

- **Unitarios:**
  - del núcleo de links: nominal, vacío y malformado; embed intacto; código inline y bloque intactos; alias; ancla; nombre que no resuelve; nombre ambiguo; idempotencia;
  - uno que recorre el árbol de argparse y exige un `description` no vacío en cada sustantivo y cada verbo.
- **Escenarios:** se actualizan las afirmaciones con `[[` (18 archivos en `tests/escenarios/` y `tests/unitarios/`). El escenario nuevo `002-10` cubre:
  - un vault sembrado no tiene wikilinks salvo embeds;
  - `tuku doctor link` reporta un wikilink escrito a mano y nombra `tuku fix link`;
  - `tuku fix link` lo convierte, conserva la fecha de modificación del archivo, y la segunda corrida da un delta vacío;
  - un wikilink ambiguo hace que `fix link` salga con 1, sin escribir ese link, y nombre la decisión.
- **Agénticos:** `uv run pytest -m agentic -k 003` en verde con `agy`. El agente no escribe links (los compone `tuku`), pero conviene confirmarlo.

## Verificación

- `uv run pytest`, `ruff check .` y `mypy src tests` limpios.
- Agénticos del 003 en verde.
- Aceptación humana en Obsidian sobre el vault de `playground/002-10-…`:
  - el link del ámbito en `AHORA.md` abre su página;
  - la transclusión de pendientes se ve;
  - un link creado a mano en Obsidian lo detecta `tuku doctor link` y lo convierte `tuku fix link`, sin que el archivo suba en "modificados recientemente".

## Cierre

- La iteración del día en `devel/iteraciones/AAAA-MM-DD.md`.
- Commit con solo los archivos de este plan. Sin push salvo que el autor lo pida.
- Este archivo se borra cuando el plan está ejecutado.
