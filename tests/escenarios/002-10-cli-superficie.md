# Escenario · 002-10-cli-superficie

**Cubre:** epic 002. La convención "la ayuda del CLI se prueba en cada epic" de [`../../devel/epics.md`](../../devel/epics.md), la regla transversal de [`../../spec/cli.md`](../../spec/cli.md) de que toda salida de error nombre el defecto y la corrección, y el criterio transversal del campo "A mano": ningún comando entra sin declarar cómo se hace lo mismo sin él.

## Escenario: `tuku -h` nombra los nouns del epic

Cuando se corre

```bash
tuku -h
```

Entonces sale con 0 y el texto nombra `init`, `cycle`, `doctor`, `rebuild`, `vocab`, `style`, `entry`, `todo`, `scope`, `link` y `note`

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
tuku entry rename -h
```

Entonces todas salen con 0 y cada una nombra sus verbs: `entry` los suyos `add`, `rename` y `lint`, `vocab` su `show`, `cycle` su `open`, `style` su `lint`, `todo` sus `open`, `close` y `lint`, `scope` sus `create`, `rename` y `lint`, `link` su `backfill`, `note` sus `create`, `rename` y `lint`
Y `tuku entry add -h` nombra `--body`, `--scope`, `--day` y `--hour`, que son los campos de un registro
Y `tuku entry rename -h` nombra `--day`, `--hour` y `--body`: el registro se ubica por cuándo ocurrió, no por un identificador que el autor no tiene

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
tuku entry add --vault mi-vault --day 2026-08-11 --hour 12:05 --scope personal --body "**cachureo**: ordené los cables"
tuku entry lint --vault mi-vault
```

Cuando además se escribe la marca cerrada mal escrita, y se revisa

```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 13:00 --scope personal --body "**Pendiente**: comprar una maleta"
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

## Escenario: cada comando dice cómo se hace lo mismo a mano

Dado el conjunto de comandos que el CLI expone, cada hoja del árbol de `-h`
Cuando se lee la ayuda de cada uno
Entonces ninguna termina sin decir cómo se consigue el mismo resultado sin `tuku`
Y lo que dice nombra archivos y párrafos del vault, no funciones ni módulos: le habla a quien tiene un editor de texto abierto y nada más

El campo "A mano" es lo que sostiene el principio 1 ([`../../docs/principios.md`](../../docs/principios.md)): la automatización existe para absorber esfuerzo mecánico, nunca para volverlo obligatorio, y una que no declara su equivalente manual es una dependencia disfrazada. El horizonte del vault es veinte años y el de este programa no.

Va en la ayuda del propio comando y no en la spec por dónde se lee: quien lo necesita está en el terminal, quizás sin el repositorio a mano, y quizás no sea una persona. Una tabla en otro documento se desincroniza el día que entra un comando nuevo; el epílogo del comando entra con él o no entra.

Se afirma como barrido y no comando por comando por la misma razón que el escenario anterior: recorre lo que `-h` declara, así que un verb nuevo sin su campo rompe este escenario sin que nadie agregue una línea acá. Los tres `rename` entraron después de escribirse esta regla y son el primer caso que tuvo que cumplirla.

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
- Leer los campos "A mano" de corrido y seguir uno con un editor de texto y el vault delante, sin ejecutar nada. Que el campo exista lo verifica el barrido; que la instrucción alcance para hacer el trabajo solo se sabe haciéndolo. `tuku scope rename` es el que más cuesta y el que más conviene probar así.
