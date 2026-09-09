# Escenario · 002-12-reconstruir-lo-derivado

**Cubre:** epic 002, el principio 9 de [`../../docs/principios.md`](../../docs/principios.md), que se llama a sí mismo "el test fundamental de arquitectura" y hasta hoy no tenía test.

Si se borra todo lo derivado y se regenera desde el conjunto canónico, tiene que salir lo mismo: idéntico byte a byte cuando lo produjo un proceso determinista. Todo lo del epic 002 lo es, así que acá la exigencia es la fuerte y no la de equivalencia.

Lo que ya se prueba no es esto. Los escenarios de la cadena verifican que correr una operación dos veces no duplique, que es idempotencia **por operación**. Un derivado puede pasar esa prueba y aun así no poder reconstruirse: basta que se haya ido actualizando de a poco y que ningún paso solo sepa producirlo entero. Ese es el defecto que este escenario existe para cazar, y solo aparece borrando.

## Estado inicial

El que dejó [`002-11-renombrar`](002-11-renombrar.md), que es el vault más poblado que produce el epic: dos ámbitos, un pendiente abierto, una nota enlazada desde la bitácora, y un renombrado encima de todo eso.

```bash
cp -r ../../002-11-renombrar/corregir-un-registro-corrige/mi-vault .
```

El renombrado importa para el caso: es la operación que más derivados toca a la vez, y la que tendría más lugares donde dejar un derivado bien por acumulación y mal por reconstrucción.

## Escenario: borrar lo derivado y regenerarlo devuelve lo mismo

Dado un vault sano, con copia de lo derivado guardada aparte para comparar

```bash
cp -r mi-vault referencia
```

Cuando se borra todo lo derivado y se reconstruye

```bash
cd mi-vault && tuku rebuild
```

Entonces cada archivo derivado vuelve idéntico, byte a byte

```bash
diff -r referencia mi-vault
```

Y ningún archivo del conjunto canónico cambió: reconstruir lee de ahí y no escribe ahí
Y el vault queda sano

```bash
cd mi-vault && tuku scope lint
```

Hoy lo derivado es `ambitos/PENDIENTES-AMBITOS.md` y las secciones propagadas de cada página de ámbito. La lista crece con el sistema (`log.md`, `index.md` y `reportes/` están en [`../../spec/README.md`](../../spec/README.md) y todavía no existen), y por eso el escenario no la escribe a mano: lo derivado se declara en un solo lugar del código y tanto el borrado como la comparación salen de ahí. Una lista copiada acá se queda corta el día que aparezca el primer derivado nuevo, y un test que no mira algo pasa igual.

## Escenario: reconstruir dos veces seguidas no mueve nada

Cuando se reconstruye otra vez, sin tocar nada en medio

```bash
cd mi-vault && tuku rebuild
```

Entonces el vault no cambió en absoluto

La primera reconstrucción parte de la ausencia y la segunda de un derivado ya escrito. Que las dos lleguen al mismo texto es lo que hace que reconstruir sea seguro de correr en cualquier momento, y no una operación que haya que elegir cuándo hacer.

## Escenario: un derivado editado a mano se corrige al reconstruir

Dado que el autor editó a mano un archivo derivado, creyendo que era fuente

```bash
cd mi-vault && echo "- una fila que nadie escribió" >> ambitos/PENDIENTES-AMBITOS.md
```

Cuando se reconstruye

```bash
cd mi-vault && tuku rebuild
```

Entonces la línea agregada a mano desapareció y el archivo volvió a lo que dice el canónico

Este es el caso que le da sentido al principio en el uso diario y no solo en la teoría: el vault se opera con un editor de texto abierto, así que tarde o temprano alguien escribe en el archivo equivocado. Lo derivado tiene que ser el lugar donde eso se pierde sin drama, y esa es exactamente la razón por la que el canónico nunca se regenera.

## Escenario: reconstruir sobre un canónico roto informa y no escribe

Dado un vault cuyo canónico tiene un defecto que lo derivado no puede representar

```bash
echo "sin tabla" > mi-vault/PENDIENTES.md
```

Cuando se reconstruye

```bash
cd mi-vault && tuku rebuild
```

Entonces sale con el código de rechazo (1), nombra el defecto y dónde está, y no dejó ningún derivado a medio escribir

La regla de [`../../spec/cli.md`](../../spec/cli.md), "ante la duda informar sin escribir", pesa más acá que en cualquier otro comando: es el único que empieza borrando. Un `rebuild` que aborta a mitad de camino deja el vault peor que antes de correrlo, y esa es la falla que haría que nadie se atreva a usarlo.

## Qué hace fallar y qué solo se reporta

**Falla:** que `diff -r` encuentre cualquier diferencia tras reconstruir, que un archivo canónico haya cambiado, que la segunda reconstrucción mueva algo, o que un rechazo haya alcanzado a borrar un derivado.

**Se reporta:** qué archivos regeneró y cuántos, que es lo que el autor lee para saber qué alcance tuvo.

## Por qué existe

El principio 9 tiene un recíproco que es el que ordena el resto del diseño: si algo que debía ser idéntico tras reconstruir solo resulta equivalente, hay juicio de un agente donde correspondía una regla. Ese recíproco no se puede usar como criterio mientras no haya forma de reconstruir, así que este escenario no verifica una funcionalidad más: habilita el instrumento con que se mide el principio 4 de acá en adelante.

Va al final del epic 002 y no antes porque necesita el vault más rico que el epic produce, y va en el 002 y no en un epic posterior porque todo lo que reconstruye hoy es determinista. Cuando el 006 y el 007 agreguen derivados que redacta un agente, la exigencia de esos será la de equivalencia y no la de byte, y eso será un escenario suyo, no una excepción dentro de este.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_12 -m "not red and not pendiente"
```

## Qué se mira a mano

- Borrar los derivados con `rm`, reconstruir y leer las páginas de ámbito completas: que se lean bien, no solo que coincidan. Un derivado puede reconstruirse idéntico y ser ilegible, y eso este escenario no lo ve.
- Que el reporte de `tuku rebuild` deje claro qué se tocó, para que correrlo no dé la sensación de haber hecho algo irreversible.
