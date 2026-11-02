# 9. Pasar de semana

> `AHORA.md` se archiva solo: lo reciente queda a la vista y lo viejo pasa a `bitacoras/`.

No hay nada que abrir ni cerrar. `AHORA.md` conserva la semana anterior completa y la actual hasta hoy (`archive_weeks` en `reglas/config.tuku.md`). El primer comando que escribe después de esa ventana mueve lo más viejo a una bitácora de lunes a domingo, `bitacoras/bitacora-AAAAMMDD-AAAAMMDD.md`. Un comando que solo lee no archiva.

## Tu foco

> [!warning] Edita a mano
> Abre `AHORA.md` y escribe en el recuadro del foco en qué quieres concentrarte esta semana.
>
> ```edit
> AHORA.md: reemplaza "Escribe aquí en qué concentrarte estos días." por "Cerrar la cotización de Los Robles."
> ```

> [!check] Qué debería pasar
> - `tuku doctor` sigue sano.
> - El foco es lo primero de `AHORA.md`, con tu texto.

El foco es tuyo: el agente no lo escribe ni lo cambia, y TUKU lo conserva al archivar.

## Un lunes cualquiera

> [!tip] Dile a tu agente, el lunes
> Partí revisando la bodega, llegó el pedido de resmas.

> [!check] Qué debería pasar
> - `AHORA.md` tiene el día de hoy arriba de todos, con el registro. El agente no avisó de nada ni pidió abrir una semana.
> - Los días del 17 al 21 siguen en `AHORA.md`, debajo.
> - `bitacoras/` sigue sin archivos: la semana del 17 todavía cabe en la ventana.

## Cuando una semana sale de la ventana

> [!tip] Dile a tu agente, el lunes siguiente
> Recibí las resmas que faltaban, quedó todo en la bodega.

> [!check] Qué debería pasar
> - `bitacoras/` tiene `bitacora-20260817-20260823.md`, con los registros del lunes 17 al domingo 23 y `from: 2026-08-17` y `to: 2026-08-23` en su encabezado.
> - `AHORA.md` ya no tiene los días del 17 al 23. Trae primero tu registro de hoy, y debajo la semana del 24.
> - El foco que escribiste sigue arriba de `AHORA.md` y no pasó a la bitácora.
> - Los links de la bitácora abren las páginas de sus ámbitos.
> - `PENDIENTES.md` conserva las filas abiertas, cada una una sola vez.
> - El recuadro «Pendientes de los próximos 7 días» marca como atrasados los que pasaron de plazo.

Nada se perdió ni se movió por tu mano. Lo que archivó TUKU es lo que escribiste, con sus links recalculados, y los pendientes siguen donde estaban porque no pertenecen a una semana.

## Leer lo archivado

> [!tip] Dile a tu agente
> ¿Qué pasó con la cotización de Los Robles?

> [!check] Qué debería pasar
> - El agente cuenta la llamada de don Rodolfo y el envío de la cotización, aunque ya estén en `bitacoras/`.
> - Ningún archivo cambió.

La página de cada frente lista su actividad de los últimos doce meses, también la archivada, y enlaza a la bitácora donde está.

Siguiente: [10. Lo que nadie pidió](10-lo-que-nadie-pidio.md).
