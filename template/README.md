# template

> Estructuras iniciales en Markdown. Un directorio por variante. Esto no es documentación ni código: es el producto que recibe el autor, tal cual se copia.

Lo que hay dentro de una variante se copia tal cual. Nada de lo que está en este `README.md` viaja al vault del autor.

El mecanismo que copia una variante y resuelve sus fechas es código, no template: vive en [`../src/tuku/init.py`](../src/tuku/init.py) y se ejecuta con `tuku init`.

## Variantes

| Variante | Para quién |
| --- | --- |
| [`vanilla/`](vanilla/) | Cualquiera. El mínimo operable a mano desde el primer día, y el más adaptable porque casi no supone nada sobre la vida de quien lo usa. |

Las variantes futuras se agregan como hermanas de `vanilla/`, nunca como capas encima. Si dos variantes comparten un archivo, se duplica: un template que hay que componer deja de ser copiable a mano y rompe el principio 1.

## El estado cero

Lo que trae `vanilla/` y nada más. Es la definición operativa del principio 2: infraestructura mínima, sin un solo dato sobre la vida de quien lo instala.

| Archivo | Qué trae |
| --- | --- |
| `AGENTS.md` | Reglas de todo el repositorio |
| `LIBRO-DE-ESTILO.md` | Cómo opera TUKU con cada entidad; lo del autor está en `reglas/` |
| `AHORA.md` | Los días del primer ciclo sembrados, sin registros |
| `PENDIENTES.md` | Los callouts de horizonte, vacíos |
| `ambitos/AGENTS.md`, `ambitos/CADENCIAS.md` | Reglas y cadencias de toda la rama |
| `ambitos/personal/` | La única rama inicial: `CAPACIDAD.md`, `personal.md` |
| `notas/AGENTS.md` | Reglas del zettelkasten |
| `reglas/*.user.md` | Lo que decide el autor sobre cada entidad, por declarar; el libro de estilo los transcluye |
| `reglas/config.tuku.md` | `TZ`, `cycle_name`, `tuku_template`, `tuku_version` y `origen`, en una tabla |
| `.obsidian/app.json`, `.gitignore` | Que Obsidian escriba links Markdown con ruta relativa, y que de `.obsidian/` solo se versione eso ([`../spec/markdown.md`](../spec/markdown.md)) |

La tabla es la referencia, no un inventario cerrado: lo que importa es que cualquier cosa que se agregue supone algo sobre el autor y hay que justificarlo.

`CAPACIDAD.md` de `personal/` se siembra **sin un solo dato**, diciendo que todavía no se ha declarado nada y por qué conviene hacerlo. Es opcional y deseable, no un requisito (ver [`../spec/ambitos.md`](../spec/ambitos.md)): el vault opera sin él. El `AGENTS.md` y el `CADENCIAS.md` de un ámbito se crean cuando el autor declara su primera regla o cadencia. Existen en el estado cero porque un archivo que se explica solo es la forma barata de que el autor sepa que puede escribirlo, y no rompe el principio 2 mientras no le pida declarar nada para empezar.

## Instalar a mano

Copiar el contenido de la variante a un directorio vacío y hacer tres cosas:

1. En `reglas/config.tuku.md`, poner la zona horaria.
2. En `AHORA.md`, escribir `desde` y `hasta` con las fechas del primer ciclo. Por defecto es `semana`, que es el ritmo menos sorprendente para quien nunca ha usado esto.
3. En `AHORA.md`, reemplazar los encabezados de día por los días reales de ese rango.
4. Opcional: en `reglas/autor.user.md` poner el nombre del autor. Dejarlo en blanco no impide escribir; el autor lo completa cuando quiera.

Después de los tres primeros ya se puede escribir. Todo lo demás emerge del uso.

## Por qué se instala a mano

Porque tiene que poder hacerse sin TUKU. Un vault que solo se puede crear ejecutando un programa es un vault que dentro de veinte años no se puede crear. `tuku init` hace exactamente estos pasos y ninguno más, con `--author` para el paso 4.
