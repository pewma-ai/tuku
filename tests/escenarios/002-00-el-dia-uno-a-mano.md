# Epic 002 · El día uno, a mano

> Alguien instala TUKU y empieza a usarlo el mismo día. Todo lo que hace, lo hace sobre un vault que está vacío: cada cosa que necesita, la crea al escribirla.

Los ejemplos corresponden al primer día (martes 11 de agosto de 2026): el inicio de ciclo que un vault recién instalado recibe sin inventar ámbitos previos.

El fixture cubre los registros esenciales del día para ejercitar marcas y consecuencias. La revisión de resultados se apoya en el `diff -r` entre carpetas consecutivas de `playground/`.

## Qué tiene que funcionar

1. **El ciclo se abre desde la plantilla.** Si no existe `AHORA.md` para la fecha, se crea a partir de `reglas/plantilla/AHORA.md` con la semana completa (lunes a domingo). Si ya existe, no se sobreescribe.
2. **El registro queda bien puesto.** Dados los campos de un hecho (hora, ámbito, marca de la ontología cerrada, clasificación, cuerpo), lo que queda escrito cumple las reglas de `docs/` y `spec/`, en el día correcto y en orden cronológico.
3. **Los pendientes se abren y se cierran con huella en la bitácora.** Un registro `**pendiente**` abre el pendiente en `PENDIENTES.md` de forma atómica e idempotente, y `~~(Hecho)~~` lo cierra. Un cierre sin pendiente abierto correspondiente escribe el registro igual, informa que no había pareja y no inventa ninguna.
4. **Escribir en un día futuro fecha el pendiente.** El pendiente toma la fecha de ese día y queda propagado al inicio del día.
5. **Crear un ámbito lo deja bien guardado y enlaza hacia atrás.** El árbol queda correcto y las menciones sueltas del ciclo en curso se convierten en enlaces, de forma retroactiva.
6. **Crear una nota a petición.** El autor la pide, la nota se escribe, queda el registro en la bitácora que deja constancia, y si lo pidió así, queda enlazada a su ámbito.

Cubre la fase 1 completa, la fase 2 completa, y la versión mínima de las fases 3 y 5.

## Dónde queda cada corrida

Cada escenario escribe en `playground/002-<escenario>/` y limpia esa carpeta antes de usarla. Solo esa.

Hasta el 2026-09-09 esto era un `rm -rf 002-*` al empezar el epic, y eso borraba también el resultado de los escenarios que la corrida no iba a regenerar. En un epic determinista da igual, porque todo se rehace en dos segundos; en uno agéntico se lleva por delante turnos que costaron tokens y que no se repiten. Una carpeta tuya que empiece con `002-` sobrevive salvo que le pongas el nombre exacto de un escenario.

## Qué se verifica

Dos superficies:
- **El vault:** qué quedó escrito, dónde, y que el diff no toque lo que no debía. Cada paso de la cadena afirma:
  - Diff exacto sin efectos colaterales.
  - Idempotencia: el segundo pase da diff vacío.
  - Todo cambio proviene de una invocación de `tuku`.
- **El comando:** ayuda, códigos de salida, mensajes de corrección, y que los de lectura no escriban.

## Decisiones y movimientos de diseño

- **La consecuencia "nota":** se agregó a la tabla de [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md) con su regla [`template/vanilla/reglas/notas.tuku.md`](../../template/vanilla/reglas/notas.tuku.md).
- **`~~(Hecho)~~` sin preexistente:** el comando informa y no rechaza ni inventa el pendiente.
- **El día de hoy no fecha:** escribir bajo hoy entra al horizonte del ciclo en curso (`esta semana`); solo un día futuro fecha (`con fecha`).
- **`cycle open`:** calcula semana de lunes a domingo e instancia plantilla.

## Criterio de salida

Una persona instala, escribe durante un día invocando `tuku` y termina con pendientes abiertos, un ámbito nuevo y una nota enlazada, con las vistas derivadas y las páginas de ámbito sincronizadas. Del lado del comando: `tuku -h` describe todo lo agregado, cada error dice cómo corregirse, los comandos de lectura no escriben, y ningún cambio del vault llegó por una vía que no fuera una invocación de `tuku`.

## No entra

Nada que dependa de un LLM (Epic 003). Tampoco ciclos, cadencias, inferencia, ni las versiones completas de ámbitos y notas.

## Escenarios del epic

### Cadena determinista (herencia de estado en `playground/`)

- [`002-01-abrir-ciclo.md`](002-01-abrir-ciclo.md) — Abre el ciclo semanal desde plantilla si no existe.
- [`002-02-registro-en-su-dia.md`](002-02-registro-en-su-dia.md) — Escribe registros en el día de hoy ordenados por hora.
- [`002-03-lint-de-registro.md`](002-03-lint-de-registro.md) — Validación del formato de bitácora contra ontologías.
- [`002-04-abrir-pendiente.md`](002-04-abrir-pendiente.md) — Apertura automática de pendiente en `PENDIENTES.md`.
- [`002-05-cerrar-pendiente.md`](002-05-cerrar-pendiente.md) — Cierre automático con `~~(Hecho)~~` y reporte de no emparejados.
- [`002-06-escribir-en-un-dia-fecha.md`](002-06-escribir-en-un-dia-fecha.md) — Fechado automático al escribir en día específico.
- [`002-08-crear-ambito.md`](002-08-crear-ambito.md) — Creación de ámbito y enlazado retroactivo.
- [`002-09-crear-nota.md`](002-09-crear-nota.md) — Creación de nota enlazada a ámbito y bitácora.
- [`002-11-renombrar.md`](002-11-renombrar.md) — Corregir lo ya escrito sin dejar nada apuntando al nombre viejo.
- [`002-12-reconstruir-lo-derivado.md`](002-12-reconstruir-lo-derivado.md) — Borrar lo derivado y regenerarlo devuelve lo mismo (principio 9).

### Fuera de la cadena

- [`002-10-cli-superficie.md`](002-10-cli-superficie.md) — Superficie completa del CLI (`-h`, códigos, correcciones y el campo "A mano").
