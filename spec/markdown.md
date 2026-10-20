# spec · markdown

> Cómo se escribe todo archivo del vault: el dialecto, dónde van los datos que lee una máquina y cómo se enlaza. Qué archivos hay y qué declara cada uno está en [vault.md](vault.md). Se justifica por los principios 1, 7 y 9 de [`../docs/principios.md`](../docs/principios.md).

## El dialecto

TUKU escribe CommonMark con dos extensiones de GFM, las tablas y el tachado (`~~`), y tres de Obsidian:

| Extensión | Forma | Para qué |
| --- | --- | --- |
| Callout | `> [!todo] Título` y sus líneas `> ` | Agrupar lo que una vista muestra: los pendientes del día, de la semana y de cada ámbito (`[!todo]`), los hijos de un ámbito (`[!abstract]`) |
| Transclusión | `![[archivo.md#^ancla]]` | Mostrar un bloque de otro archivo sin copiarlo |
| Ancla de bloque | `^ancla` al final del bloque | El destino de una transclusión |

El dialecto termina ahí. Los enlaces son links Markdown o transclusiones, los datos van en Markdown visible y las vistas las genera `tuku`. Un `|` dentro de una celda se escribe `\|`.

## Quién lo lee

El dialecto se elige para tres lectores:

- **Un editor básico.** Un callout se lee como una cita y un ancla como una palabra al final de la línea. La transclusión muestra la ruta en vez del texto, y la ruta se sigue a mano. Por eso solo trae vistas de algo que vive en otro archivo, y la del plan se aplana al cerrar el ciclo ([ciclo.md](ciclo.md)).
- **Obsidian.** Muestra el dialecto completo y es la referencia: TUKU escribe solo lo que Obsidian muestra.
- **Un agente.** Un modelo de 2026 entiende callouts y transclusiones aunque estén fuera de CommonMark: lee `> [!todo]` como un bloque de pendientes y `![[...#^ancla]]` como una referencia que puede abrir. Para un agente, el dialecto completo es Markdown corriente.

Una extensión nueva entra cuando Obsidian y un agente la leen, y un editor básico la degrada a algo legible.

## Obsidian muestra, `tuku` calcula

**Toda vista que importe es texto que genera `tuku`.** El vault funciona en Obsidian sin plugins: una vista hecha con Dataview o Bases desaparece al abrir el vault con otro editor (principio 1) y queda fuera de lo que se regenera y compara como texto (principio 9). Obsidian sirve para mirar y editar; lo que se calcula, lo calcula `tuku`.

El template siembra `.obsidian/app.json` con tres ajustes, para que Obsidian escriba lo mismo que `tuku`:

| Ajuste | Efecto |
| --- | --- |
| `"useMarkdownLinks": true` | Links Markdown |
| `"newLinkFormat": "relative"` | Ruta relativa al archivo |
| `"alwaysUpdateLinks": true` | Mover o renombrar un archivo en Obsidian actualiza los links que lo apuntan |

Con el tercero, Obsidian reescribe archivos sin pasar por `tuku`. Es la familia "a mano" de [flujo-informacion.md](flujo-informacion.md): el autor actúa con su editor y `tuku doctor` revisa el resultado como revisa cualquier edición.

## Datos de máquina en estructura visible

Lo que una automatización lee de un archivo está a la vista: un campo `**Campo:** valor`, una tabla o un encabezado. El `**Cuándo:**` de una cadencia ([cadencias.md](cadencias.md)), la tabla de `PENDIENTES.md` ([pendientes.md](pendientes.md)) y la tabla de `reglas/clasificaciones.user.md` ([bitacora.md](bitacora.md)) son de esa clase. El nombre del campo o del encabezado es contrato: renombrarlo rompe al comando, y que falte es un error ruidoso.

**Toda marca es visible.** Un comentario HTML o una marca invisible se rompe al editar el archivo sin que nadie lo note. Donde hace falta una frontera, la pone la estructura: la región propagada de un día termina donde empieza el primer `- HH:MM - ` ([pendientes.md](pendientes.md)).

El frontmatter es el otro lugar de datos de máquina, y está en [vault.md](vault.md).

## Enlaces

**Un enlace es `[texto](ruta/relativa.md)`, relativa al archivo que lo contiene.** En `AHORA.md`, que vive en la raíz, el ámbito `personal` es `[personal](ambitos/personal/personal.md)`; desde una página de ámbito hermana, `[personal](../personal/personal.md)`. La ruta la calcula `tuku` desde el árbol de `ambitos/`: quien dicta pasa el nombre y `tuku` escribe la ruta ([bitacora.md](bitacora.md)).

**La transclusión es el único wikilink admitido** y se reconoce por el `!` inicial. Cuándo se transcluye y cuándo se propaga lo decide [pendientes.md](pendientes.md).

**Los lectores aceptan los dos formatos y los escritores solo producen Markdown.** Si un wikilink entra igual (Obsidian sin la semilla, otro editor, un vault anterior), el vault sigue funcionando hasta que se corre `tuku fix link`.

### Quién recalcula las rutas

Una ruta relativa deja de resolver cuando la línea cambia de archivo o el destino cambia de lugar. En los dos casos la recalcula quien hace el cambio:

| Cambio | Quién |
| --- | --- |
| Una línea de `AHORA.md` se copia a la página de su ámbito | `tuku regenerate todo`, `tuku regenerate scope` |
| Un ámbito cambia de lugar o de nombre | `tuku scope move`, `tuku scope rename` ([ambitos.md](ambitos.md)) |
| Un ciclo o una rama se archivan | el archivado (epic 006) |
| El autor mueve un archivo en Obsidian | Obsidian, con `alwaysUpdateLinks` |

Recalcular alcanza todo el vault, también las bitácoras cerradas: el principio 1 exige que todo link resuelva.

### Enlazar es deliberado

Crear un ámbito o sumarle keywords deja intacto el cuerpo de lo que el autor ya escribió; cambiar el ámbito de un registro es otra operación ([ambitos.md](ambitos.md), "Lo escrito antes de abrir un ámbito"). Un registro lleva los links que se le escribieron al registrarlo, y el cuerpo queda como lo dijo el autor. Una mención se enlaza hacia atrás cuando el autor lo hace a mano o lo pide como operación deliberada.

Un comando **repara** lo que ya estaba enlazado, y reparar conserva el pasado tal como se escribió.

### `doctor link` y `fix link`

`tuku doctor link` encuentra los wikilinks que no son transclusión y `tuku fix link` los convierte. Alcanza todo el vault, incluidos los ciclos cerrados: cambia el formato sin agregar enlaces. Conserva la fecha de modificación, porque el cambio es solo de forma. Con la semilla de `.obsidian` queda como red de seguridad. El contrato de la pareja `doctor` / `fix` está en [cli.md](cli.md).

## No entra

- El formato de cada archivo. Lo especifica la spec de su primitiva.
- Cómo se empareja un cierre con su pendiente cuando uno lleva links y el otro no. Eso es [bitacora.md](bitacora.md).
- La sección `## Ver además` de las notas. Eso es [notas.md](notas.md).
