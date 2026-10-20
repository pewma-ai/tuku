# 7. Conversar

> Deliberar con el agente sin que se escriba nada hasta que ratifiques.

Hasta aquí dictaste hechos que ya habían pasado. Conversar es cuando todavía no sabes qué decidir, cambias de opinión o una urgencia te interrumpe. El agente es un secretario, no un dueño: escribe lo que ratificas y nada de lo que piensas en voz alta ([principio 3](../principios.md)).

Deja `AHORA.md` y `PENDIENTES.md` abiertos al lado mientras hablas.

## Pensar en voz alta

> [!tip] Dile a tu agente
> Tengo que decidir si le confirmo a la Importadora Andina el pedido de marzo. Es mucha plata y la línea de crédito del banco todavía no está lista. ¿Qué tengo pendiente para hoy antes de meterme en eso?

> [!check] Qué debería pasar
> - El agente te lista tus pendientes abiertos, empezando por los que vencen hoy, y te ayuda a pensar.
> - Ningún archivo cambió.

Consultar y deliberar no son hechos.

## La marcha atrás

> [!tip] Continúa la conversación
> Ya, dile que preparemos la mitad del pedido no más.
>
> No, espérate. Mala idea: si pido la mitad pierdo el descuento por volumen. Olvida eso. Primero tengo que hablar con el banco.

> [!check] Qué debería pasar
> - El agente acusa recibo del cambio de rumbo.
> - Ningún archivo cambió. La mitad del pedido no quedó escrita en ninguna parte.

Un borrador mental guardado se leería mañana como un compromiso que nunca ratificaste.

## Una frase que puede ser dos cosas

> [!tip] Ahora dale una frase ambigua
> Quedamos al día con la Patricia.

> [!check] Qué debería pasar
> - El agente se detiene y pregunta si es solo un registro o si cierra uno de sus dos pendientes (cotizarle de nuevo, mandarle las muestras), y cuál.
> - Nada se escribe mientras no contestes.

> [!tip] Respóndele
> Le mandé las muestras.

> [!check] Qué debería pasar
> - La fila «mandarle las muestras» desapareció de `PENDIENTES.md`.
> - «Cotizarle de nuevo» sigue abierta.
> - `AHORA.md` tiene el cierre `(Hecho): ~~…~~` con el texto exacto del pendiente.

Cuando escribir tiene consecuencias, el agente pregunta antes de decidir por ti.

## La interrupción

En medio de una conversación larga, la realidad interrumpe.

> [!tip] Dile a tu agente
> Espérate, me acaba de llegar el flete con las cajas de témperas. Llegaron tres cajas rotas y manchadas, hay que reclamar.

> [!check] Qué debería pasar
> - `AHORA.md` tiene el registro del incidente, con su hora, y `PENDIENTES.md` una fila nueva: reclamar las cajas rotas.

Es un hecho consumado y se registra al momento, aunque estés en medio de otra cosa. El agente puede volver después al hilo de la Importadora Andina.

## Una propuesta que rechazas

> [!tip] Retoma el tema
> Lo de Andina va a tomar varias semanas de negociación.

El agente puede sugerir abrir un frente `importadora-andina`.

> [!tip] Rechaza la sugerencia
> No, son solo un proveedor, déjalo en personal.

> [!check] Qué debería pasar
> - No existe `ambitos/importadora-andina/`.
> - Ningún archivo guarda una marca de «propuesta rechazada».

Una propuesta rechazada queda como si nunca se hubiera hecho. Un asistente que registra cada rechazo termina condicionándote.

## Ratificar

> [!tip] Cierra con la resolución
> En resumen: el viernes a las diez voy al banco a firmar la ampliación de la línea, y después de eso llamo a Andina para cerrar el pedido.

> [!check] Qué debería pasar
> - `PENDIENTES.md` tiene dos filas nuevas: ir al banco el viernes a las 10:00, y llamar a Andina para cerrar el pedido.
> - Del resto de la conversación quedó solo lo que ya estaba escrito: el incidente de las témperas y el cierre de las muestras.

De toda la deliberación quedan las acciones que ratificaste.

Siguiente: [8. Una semana después](08-una-semana-despues.md).
