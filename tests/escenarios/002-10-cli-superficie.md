# Escenario · 002-10-cli-superficie

**Cubre:** epic 002. La convención "la ayuda del CLI se prueba en cada epic" de [`../../devel/epics.md`](../../devel/epics.md), y la regla transversal de [`../../spec/cli.md`](../../spec/cli.md) de que toda salida de error nombre el defecto y la corrección.

## Escenario: `tuku -h` nombra los nouns del epic

Cuando se llama a `main(["-h"])`
Entonces sale con 0 y el texto nombra `init`, `entry`, `vocab`, `cycle` y `style`

## Escenario: cada noun lista sus verbs

Cuando se llama a `main(["entry", "-h"])`, `main(["vocab", "-h"])`, `main(["cycle", "-h"])` y `main(["style", "-h"])`
Entonces salen con 0, el primero nombra `add` y `lint`, el segundo `show`, el tercero `open`, el cuarto `lint`
Y `main(["entry", "add", "-h"])` nombra `line`, `--vault` y `--day`

## Escenario: un noun sin verb es error de uso

Cuando se llama a `main(["entry"])`
Entonces sale con el código de uso (2), no con el de rechazo

## Escenario: el lint sale con rechazo cuando encuentra un error

Dado un vault con un registro que lleva `**Pendiente**` mal escrito
Cuando se llama a `main(["entry", "lint", "--vault", <vault>])`
Entonces sale con el código de rechazo (1), distinto del de uso
Y con solo una pregunta abierta, y ningún error, sale con 0

Un tipo desconocido no es un fallo: la ontología abierta es permisiva ([`../../spec/bitacora.md`](../../spec/bitacora.md)). Solo la cerrada mueve el código de salida.

## Escenario: un directorio que no es un vault se rechaza diciendo qué hacer

Dado un directorio cualquiera sin `AHORA.md`
Cuando se llama a cualquier comando que opere sobre un vault
Entonces sale con el código de rechazo (1) y el mensaje nombra el archivo que falta y sugiere `tuku init`

## Escenario: toda salida de error nombra la corrección

Dado el conjunto de hallazgos que el lint sabe producir
Entonces ninguno tiene la corrección vacía

Es la regla de [`../../spec/cli.md`](../../spec/cli.md) convertida en barrido: se afirma una vez para todos los hallazgos en vez de repetirla en cada escenario, y crece sola cuando el epic agrega comandos.

## Por qué existe

La ayuda y los códigos son superficie pública, y son la mitad del entregable del epic que los escenarios de la cadena no miran: la cadena verifica el vault, este verifica el comando.

Corre en proceso sobre `tuku.cli.main`, sin red. El vault que necesita para ejercer los códigos de salida vive en un tempdir, no en `playground/`: no es un estado que herede nadie ni que valga la pena revisar a mano.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_10
```

## Qué se mira a mano

- Correr `uv run tuku entry lint` sobre un vault con errores y leer el reporte: que se distinga de un vistazo cuál hallazgo exige acción y cuál es una pregunta.
- Que el mensaje del tipo desconocido no suene a reto, sino a pregunta sobre vocabulario del autor.
