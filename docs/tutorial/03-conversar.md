# 3. Conversar

> [!warning] Todavía no funciona
> Puedes probarlo igual: lo que salga mal ahora queda pendiente de resolver.

Hasta aquí dictaste hechos que ya habían pasado y se escribieron. Conversar ocurre cuando todavía no sabes qué decidir, cambias de opinión en el camino o una urgencia interrumpe lo que pensabas.

---

## Pensar en voz alta

> [!tip] Dile a tu agente
> Tengo que decidir si le confirmo a la Importadora Andina el pedido de marzo. Es mucha plata y la línea de crédito del banco todavía no está lista. ¿Qué tengo pendiente para hoy antes de meterme en eso?

El agente responde tu duda operativa revisando `PENDIENTES.md` y te ayuda a evaluar el escenario. En el vault no escribe nada.

### Mira el vault mientras hablas

Mantén `AHORA.md` y `PENDIENTES.md` abiertos al lado.

Lo esperado es **diff cero**. La mención de Andina, el crédito del banco y la consulta de pendientes quedan sin registro, porque consultar y deliberar no son hechos ([principio 3](../principios.md)).

---

## La marcha atrás

> [!tip] Continúa la conversación
> Ya, dile que preparemos la mitad del pedido no más.
>
> No, espérate. Mala idea: si pido la mitad pierdo el descuento por volumen y no me dan los números. Olvida eso. Primero tengo que hablar con el banco.

El agente acusa recibo del cambio de rumbo y la primera opción descartada queda sin registro. Los borradores mentales archivados se leerían mañana como compromisos que nunca ratificaste.

---

## Desambiguación con opciones claras

> [!tip] Ahora dale una instrucción imprecisa
> Ah, y ya le transferí el anticipo a la profe.

En tu histórico hay dos profesoras: Marcela y Patricia.

El agente se detiene y pregunta: *"¿A la profesora Marcela o a la profesora Patricia?"*.

> [!tip] Respóndele
> A la Marcela, lo de los talleres de arte.

### Mira `PENDIENTES.md` y `AHORA.md`

1. En `PENDIENTES.md` se cerró el compromiso de Marcela y el de Patricia sigue abierto.
2. En `AHORA.md` quedó la constancia con `(Hecho)`, con el cuerpo exacto del pendiente cerrado.

---

## La interrupción intercalada

En medio de una conversación larga, la realidad interrumpe.

> [!tip] Dile a tu agente
> Espérate, me acaba de timbrar el flete con las cajas de témperas. Llegaron tres cajas rotas y manchadas, voy a tener que reclamar.

Es un hecho consumado que acaba de ocurrir.

### Mira `AHORA.md`

El agente registra el incidente de inmediato en `AHORA.md`, con su hora y la marca de pendiente para el reclamo, y **retoma el hilo** de la conversación sobre la Importadora Andina y el crédito bancario.

---

## Propuesta con rechazo limpio

> [!tip] Retoma el tema de Andina
> Bueno, volviendo a lo de Andina: el pedido grande va a tomar varias semanas de negociación.

El agente puede sugerir: *"Como esto va a tomar varias semanas, ¿abrimos un ámbito nuevo para `importadora-andina`?"*.

> [!tip] Rechaza la sugerencia
> No, son solo un proveedor de insumos, déjalo dentro de compras.

### Mira la carpeta `ambitos/`

La carpeta `importadora-andina` no existe. Ningún archivo del vault guarda una marca de "propuesta rechazada" ni un registro de fricción. Una propuesta rechazada queda como si nunca se hubiera hecho ([principio 3](../principios.md)).

---

## Ratificación final

Cierra la sesión con la resolución:

> [!tip] Dale el cierre definitivo
> Ya, en resumen: anota que el viernes a las diez voy al banco a firmar la ampliación de la línea, y que después de eso llamo a Andina para cerrar el pedido.

### Mira el vault al final de la sesión

Compara el vault antes y después de toda la conversación:
- "Pedir la mitad" y las dudas quedaron sin rastro.
- Está registrado el hecho urgente de las témperas dañadas.
- Está cerrado el pendiente de la profesora Marcela.
- Están los compromisos en firme del viernes con el banco y con Andina, con su día y hora en `Vence`.

De toda la deliberación quedaron las acciones que ratificaste.

---

Siguiente: [4. Una semana después](04-una-semana-despues.md).
