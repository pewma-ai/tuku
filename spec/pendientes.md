# spec · pendientes

> `PENDIENTES.md` es fuente de verdad, nunca derivado. Se justifica por el principio 9 de `../docs/principios.md`, con la excepción declarada más abajo.

Ningún pendiente vive fuera de este archivo. Todo lo demás que los muestre (`AHORA.md`, páginas de ámbito, `reportes/`) se genera desde aquí por transclusión o por janitor.

A cambio exige disciplina, y esa disciplina la sostiene el janitor, no la memoria del autor.

## La bitácora es el disparador, no el origen de los datos

- Dictado: *"Recuérdame avisar de los GGCC al arrendatario"*
  - Bitácora: `- 09:12 - [[arriendo-depto-centro]] **pendiente**: avisar de los GGCC al arrendatario`
  - El janitor escribe en `^sin-fecha`: `- [[arriendo-depto-centro]] - avisar de los GGCC al arrendatario`
- Dictado: *"Ya le recordé los GGCC al arrendatario"*
  - Bitácora: `- 18:40 - [[arriendo-depto-centro]] ~~(Hecho)~~: avisar de los GGCC al arrendatario`
  - El janitor borra el ítem de `^sin-fecha`

Los dos ganchos son deterministas: `**pendiente**` abre, `~~(Hecho)~~` cierra (ver `bitacora.md`). El cuerpo es el mismo en los tres lugares: la entrada que abre, el ítem en `PENDIENTES.md` y la entrada que cierra. Abrir es copiarlo, cerrar es encontrarlo y borrarlo. Ninguna de las dos operaciones interpreta nada.

El archivo contiene solo lo abierto. El historial de lo cerrado vive en las bitácoras.

## Formato

Un archivo, callouts con ancla. El título del callout es la fuente: el janitor lo parsea e infiere el horizonte. Si termina en fecha ISO es bucket de fecha; si no, es un horizonte con nombre tomado de `### Horizontes` en el libro de estilo.

```text
> [!TODO] pendientes atrasados ^atrasados
> - [[ambito]] - cuerpo (vencía 2026-04-02)

> [!TODO] pendientes sin fecha ^sin-fecha
> - [[ambito]] - cuerpo

> [!TODO] pendientes de esta semana ^esta-semana
> - [[ambito]] - cuerpo

> [!TODO] pendientes de la proxima semana ^proxima-semana
> - [[ambito]] - cuerpo

> [!TODO] pendientes del 2026-04-02 ^2026-04-02
> - [[ambito]] - cuerpo
```

Los nombres de los tres horizontes del medio son del autor, no de TUKU: salen de `### Horizontes` en el libro de estilo, y el estado cero los siembra en semanas (`esta-semana`, `proxima-semana`, `fin-de-mes`) porque es el ritmo de casi todo el mundo. Un autor que trabaja por turnos los renombra ahí y en los anclas de `PENDIENTES.md`. `atrasados` y `sin-fecha` sí son de TUKU: no dependen de ningún ritmo.

Los cinco callouts de horizonte son **permanentes**: existen siempre, aunque estén vacíos, y así la escalera se lee completa. Los callouts de fecha son **efímeros**: nacen cuando un pendiente recibe esa fecha y mueren cuando se va el último.

El ítem es siempre `- [[ambito]] - cuerpo`. Toda la información temporal vive en el título del callout, nunca duplicada en el ítem.

`^atrasados` es la única excepción: sus ítems vienen de fechas distintas, así que al moverlos ahí el vencimiento se perdería. El janitor lo estampa entre paréntesis porque es el único lugar donde esa fecha ya no se puede inferir.

## Escalera de horizontes

Cada pendiente está en exactamente un callout y baja de escalón a medida que se concreta:

`sin-fecha` → `esta-semana` / `proxima-semana` / `fin-de-mes` → fecha exacta → cerrado

Con fecha exacta aparece bajo el día correspondiente de `AHORA.md` por transclusión del ancla, sin copiar.

El movimiento de escalón **no se registra en la bitácora**: mover un pendiente no es un hecho de la vida del autor, es un hecho del sistema. El janitor lo hace por sí mismo (segunda vía, ver `flujo-informacion.md`).

## Sincronía de transclusiones

Solo las anclas de fecha pueden romperse. Las de horizonte son permanentes, así que sus transclusiones nunca quedan huérfanas y no necesitan vigilancia. Eso acota el problema a los callouts fechados, que aparecen y desaparecen con el uso.

El janitor corre en cada escritura a `PENDIENTES.md` y arregla las dos direcciones:

| Falla | Síntoma | Corrección |
| --- | --- | --- |
| Transclusión sin callout | Caja de error en el día | Quitar la línea de transclusión |
| Callout sin transclusión | El pendiente no aparece en su día | Agregar la línea bajo el día |

La segunda es la peligrosa. La primera se ve: hay una caja rota y alguien la arregla. La segunda es silenciosa, el pendiente simplemente no aparece en la agenda, y el autor se entera cuando ya venció.

## Reglas

1. Un pendiente está en un solo callout, siempre.
2. Todo pendiente con fecha anterior a HOY se mueve a `^atrasados`, estampando su vencimiento.
3. Al cerrar ciclo, lo que quede en el horizonte del ciclo en curso sin fecha rueda al mismo horizonte del ciclo nuevo. Solo lo fechado cae en `^atrasados`.
4. El ítem **no lleva fecha**. El horizonte lo da el callout y la fecha de origen ya está en la bitácora. La antigüedad se saca del historial de git de `PENDIENTES.md`, que se versiona como fuente. Única excepción: `^atrasados`, ver arriba.
5. HOY se evalúa en la zona horaria del autor. La VM hereda el TZ del laptop, así que no hay que convertir, pero sí declararlo en `reglas/` para que ningún janitor asuma UTC.
6. **Ninguna transclusión apunta a un ancla que no existe.** Cada vez que un pendiente se crea, se mueve de escalón o se borra, un janitor revisa las transclusiones y las sincroniza. Una caja de error en `AHORA.md` es un defecto, no un estado válido.
7. `PENDIENTES.md` se versiona como fuente. La reconstrucción desde bitácoras no lo regenera ni lo verifica. El conjunto canónico es `AHORA.md` + `bitacoras/` + `PENDIENTES.md` + `ambitos/` + `notas/`, y el principio 9 aplica solo a lo que queda fuera de esa lista.

## No entra

- **Las reglas de tratamiento** de pendientes (prioridad, tipos, encadenamiento, criterios de vencimiento más allá de la fecha) van en un documento propio, aún por escribir. Esto cubre solo el modelo.
- **Promover pendientes entre ciclos** en el detalle de apertura/cierre. La mecánica general está aquí (regla 3); la secuencia completa de abrir y cerrar un ciclo está en `ciclo.md`.
