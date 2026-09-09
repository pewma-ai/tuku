# Escenario · 002-11-renombrar

**Cubre:** epic 002, corregir lo que ya se escribió: `tuku entry rename`, `tuku scope rename` y `tuku note rename`.

Los tres existen por la misma razón, y no es comodidad. Un agente sabe renombrar sin ellos: abre los archivos, busca las menciones y las edita una por una. Le sale bien, le cuesta caro, y cada corrida puede olvidar un lugar distinto. Con el comando es una llamada, siempre la misma, y lo que el vault promete deja de depender de cuánto esfuerzo le quedaba al modelo.

Lo que este escenario verifica no es que el archivo cambie de nombre. Es que **no quede nada apuntando al nombre viejo**, que es la parte que se hace a medias.

## Estado inicial

El que dejó [`002-09-crear-nota`](002-09-crear-nota.md): el ámbito `depto-centro`, un pendiente abierto y una nota enlazada desde la bitácora.

```bash
cp -r ../../002-09-crear-nota/la-nota-se-escribe-donde/mi-vault .
```

## Escenario: renombrar un ámbito arrastra todo lo que lo nombraba

Dado un vault con el ámbito `depto-centro`, un pendiente suyo y una nota

Cuando el autor le cambia el nombre al ámbito

```bash
cd mi-vault && tuku scope rename depto-centro depto-playa
```

Entonces la carpeta, la página y los archivos obligatorios llevan el nombre nuevo
Y cada `[[depto-centro]]` de `AHORA.md` y de `PENDIENTES.md` pasó a `[[depto-playa]]`
Y el ancla que transcluye sus pendientes apunta al bloque que existe
Y `tuku scope lint` no encuentra nada

```bash
cd mi-vault && tuku scope lint
```

El lint de ámbitos es la afirmación fuerte, y es el que corresponde: un renombrado a medias deja registros apuntando a algo que ya no está, y eso es lo que sabe ver. `tuku doctor` no sirve acá porque el vault heredado trae hallazgos a propósito, los que el [`002-03`](002-03-lint-de-registro.md) puso para su propio escenario.

## Escenario: renombrar sobre un nombre ocupado no toca nada

Dado un vault con dos ámbitos

Cuando el autor pide un nombre que ya existe

```bash
cd mi-vault && tuku scope rename depto-centro personal
```

Entonces el comando rechaza y nombra la corrección
Y los dos ámbitos siguen como estaban

El rechazo se compone antes de mover nada. Un renombrado a medias es peor que uno que no ocurrió: deja al autor con dos ámbitos incompletos y sin saber cuál es el bueno.

## Escenario: corregir un registro corrige también su pendiente

Dado un registro con `**pendiente**` y su fila en la tabla

Cuando el autor corrige cómo quedó dicho

```bash
cd mi-vault && tuku entry rename --day 2026-08-12 --hour 09:00 --body "**pendiente**: pagar la sesión de terapia"
```

Entonces el registro de las 09:00 dice el cuerpo nuevo
Y la fila de `PENDIENTES.md` dice lo mismo, carácter por carácter
Y la hora y el ámbito no cambiaron

Que las dos digan lo mismo no es cosmético: cerrar un pendiente es repetir su texto, así que un registro corregido y una fila sin corregir dejan un pendiente que ya no se puede cerrar. Es el modo de falla que hace falta el comando para evitar, porque a mano la línea está a la vista y la fila no.

## Qué hace fallar y qué solo se reporta

**Falla:** que quede un `[[depto-centro]]` en cualquier archivo, que el ancla apunte a un bloque inexistente, que el `doctor` encuentre algo, que la fila y el registro difieran, o que un rechazo haya alcanzado a mover algo.

**Se reporta:** cuántos enlaces dice haber actualizado cada comando.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_11 -m "not red and not pendiente"
```
