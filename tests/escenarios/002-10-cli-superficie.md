# Escenario · 002-10-cli-superficie

**Cubre:** epic 002. La convención "la ayuda del CLI se prueba en cada epic" de [`../../devel/epics.md`](../../devel/epics.md), y la regla transversal de [`../../spec/cli.md`](../../spec/cli.md) de que toda salida de error nombre el defecto y la corrección.

## Escenario: `tuku -h` nombra los nouns del epic

Cuando se corre

```bash
tuku -h
```

Entonces sale con 0 y el texto nombra `init`, `entry`, `vocab`, `cycle`, `style`, `todo`, `scope`, `link` y `note`

## Escenario: cada noun lista sus verbs

Cuando se corre la ayuda de cada uno

```bash
tuku entry -h
tuku vocab -h
tuku cycle -h
tuku style -h
tuku todo -h
tuku scope -h
tuku link -h
tuku note -h
tuku entry add -h
```

Entonces todas salen con 0 y cada una nombra sus verbs: `entry` los suyos `add` y `lint`, `vocab` su `show`, `cycle` su `open`, `style` su `lint`, `todo` sus `open`, `close` y `lint`, `scope` sus `create` y `lint`, `link` su `backfill`, `note` sus `create` y `lint`
Y `tuku entry add -h` nombra `line`, `--vault` y `--day`

## Escenario: un noun sin verb es error de uso

Cuando se corre

```bash
tuku entry
```

Entonces sale con el código de uso (2), no con el de rechazo

## Escenario: el lint sale con rechazo cuando encuentra un error

Dado un vault donde primero se escribe solo un tipo abierto desconocido

```bash
tuku init mi-vault --date 2026-08-11
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 12:05 - [[personal]] **cachureo**: ordené los cables"
tuku entry lint --vault mi-vault
```

Cuando además se escribe la marca cerrada mal escrita, y se revisa

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 13:00 - [[personal]] **Pendiente**: comprar una maleta"
tuku entry lint --vault mi-vault
```

Entonces sale con el código de rechazo (1), distinto del de uso
Y con solo una pregunta abierta, y ningún error, sale con 0

Un tipo desconocido no es un fallo: la ontología abierta es permisiva ([`../../spec/bitacora.md`](../../spec/bitacora.md)). Solo la cerrada mueve el código de salida.

## Escenario: un directorio que no es un vault se rechaza diciendo qué hacer

Dado un directorio cualquiera sin `AHORA.md`

```bash
mkdir no-es-un-vault
```

Cuando se corre cualquier comando que opere sobre un vault

```bash
tuku entry lint --vault no-es-un-vault
```

Entonces sale con el código de rechazo (1) y el mensaje nombra el archivo que falta y sugiere `tuku init`

## Escenario: toda salida de error nombra la corrección

Dado el conjunto de hallazgos que el lint sabe producir
Entonces ninguno tiene la corrección vacía

Es la regla de [`../../spec/cli.md`](../../spec/cli.md) convertida en barrido: se afirma una vez para todos los hallazgos en vez de repetirla en cada escenario, y crece sola cuando el epic agrega comandos.

## Por qué existe

La ayuda y los códigos son superficie pública, y son la mitad del entregable del epic que los escenarios de la cadena no miran: la cadena verifica el vault, este verifica el comando.

Corre en proceso sobre `tuku.cli.main`, sin red. Está fuera de la cadena: no hereda de ningún paso ni deja estado para el siguiente, y siembra su propio vault cuando necesita ejercer los códigos de salida.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_10
```

Cada escenario deja lo suyo en `playground/002-10-cli-superficie/<escenario>/`.

## Qué se mira a mano

- Correr `uv run tuku entry lint` sobre un vault con errores y leer el reporte: que se distinga de un vistazo cuál hallazgo exige acción y cuál es una pregunta.
- Que el mensaje del tipo desconocido no suene a reto, sino a pregunta sobre vocabulario del autor.
