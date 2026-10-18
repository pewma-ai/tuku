# 9. Cerrar la semana

> Cambiar de ciclo sin perder nada, y lo que vuelve solo.

Un **ciclo** es el período que cubre `AHORA.md`: por defecto la semana, de lunes a domingo. Al terminar, se archiva en `bitacoras/` y empieza el siguiente. TUKU no cierra nada por su cuenta: cerrar es una consecuencia grande y la decides tú.

## Una regla que se repite

> [!tip] Dile a tu agente
> Todos los viernes tengo que cuadrar la caja.

> [!check] Qué debería pasar
> - Existe una **cadencia** en un `CADENCIAS.md` del vault, con `Cuándo: viernes, semanal`, `Emite: pendiente con fecha` y `Texto: cuadrar la caja`.
> - `PENDIENTES.md` ya tiene la fila «cuadrar la caja» con `Vence` este viernes. Declarar la cadencia emite lo que falta de la semana en curso.

Una cadencia es una regla que emite pendientes con regularidad. Vive en el ámbito donde aplica, y a ti te sirve para no tener que acordarte.

## Cambiar de ciclo

Llega el lunes y no cierras nada: dictas.

> [!tip] Dile a tu agente, el lunes
> Partí revisando la bodega, llegó el pedido de resmas.

> [!check] Qué debería pasar
> - El registro se rechaza al primer intento, porque `AHORA.md` termina el domingo y no tiene el día de hoy.
> - El agente te avisa de que el ciclo cambió, cierra el anterior, abre el siguiente y recién entonces escribe tu registro.
> - Si tu ciclo no es la semana, por ejemplo un turno de 8 o 14 días, el agente te pregunta hasta qué día va el nuevo. El rango lo decides tú.

También puedes pedirlo sin esperar al lunes:

> [!tip] O dile a tu agente
> Cierra la semana y ábreme la siguiente.

## Qué apareció y qué se fue

> [!check] Qué debería pasar
> - En `bitacoras/` hay un archivo con el ciclo previo congelado, con el rango y el nombre del ciclo en su nombre, por ejemplo `bitacora-2026-08-17-2026-08-23-semana.md`.
> - `AHORA.md` tiene un día por cada fecha del ciclo nuevo, sin huecos con el anterior.
> - Los compromisos sin resolver pasaron al ciclo nuevo, cada uno una sola vez.
> - Hay un pendiente «revisar la bitácora anterior» con vencimiento el primer día.
> - El viernes del ciclo nuevo trae «cuadrar la caja», que la cadencia emitió sola.

Esa es la promesa de TUKU ([*tukulpan*](../brief.md)): lo que entró vuelve solo cuando corresponde.

## Comprobar la idempotencia

> [!tip] Dile a tu agente
> Abre el ciclo de esta semana otra vez.

> [!check] Qué debería pasar
> - Todo queda igual: pedir el ciclo que ya está abierto solo lo verifica ([principio 9](../principios.md)).

Siguiente: [10. Lo que nadie pidió](10-lo-que-nadie-pidio.md).
