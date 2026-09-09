# 3. Conversar

> [!warning] Todavía no funciona
> Puedes probarlo igual: lo que salga mal ahora es lo que está pendiente de resolver.

Hasta aquí dictaste: dijiste algo que ya había pasado y se escribió. Conversar es distinto: ocurre cuando todavía no sabes con certeza qué decidir, cuando cambias de opinión en el camino o cuando una urgencia interrumpe lo que estabas pensando.

---

## Pensar en voz alta

> [!tip] Dile a tu agente
> Tengo que decidir si le confirmo a la Importadora Andina el pedido de marzo. Es mucha plata y la línea de crédito del banco todavía no está lista. ¿Qué tengo pendiente para hoy antes de meterme en eso?

El agente debe contestar tu duda operativa revisando `PENDIENTES.md` y ayudarte a evaluar el escenario sin escribir una sola línea en el vault.

### Mira el vault mientras hablas

Mantén `AHORA.md` y `PENDIENTES.md` abiertos al lado.

Lo que buscas: **diff cero**. Ni la mención de Andina, ni el crédito del banco, ni la consulta de pendientes deben crear registros. Consultar y deliberar no son hechos ([principio 3](../principios.md)).

---

## La marcha atrás

> [!tip] Continúa la conversación
> Ya, dile que preparemos la mitad del pedido no más.
> 
> No, espérate. Mala idea: si pido la mitad pierdo el descuento por volumen y no me dan los números. Olvida eso. Primero tengo que hablar con el banco.

El agente debe acusar recibo del cambio de rumbo sin registrar la primera opción descartada. Si un secretario archivara tus borradores mentales, mañana leerías compromisos ficticios que nunca ratificaste.

---

## Desambiguación con opciones claras

> [!tip] Ahora dale una instrucción imprecisa
> Ah, y ya le transferí el anticipo a la profe.

En tu histórico hay dos profesoras: Marcela y Patricia.

El agente no debe adivinar ni asumir la más reciente en silencio. Debe detenerse y preguntar directamente: *"¿A la profesora Marcela o a la profesora Patricia?"*.

> [!tip] Respóndele
> A la Marcela, lo de los talleres de arte.

### Mira `PENDIENTES.md` y `AHORA.md`

Ahora sí:
1. En `PENDIENTES.md` se cerró únicamente el compromiso de Marcela; el de Patricia sigue intacto.
2. En `AHORA.md` quedó la constancia con `~~(Hecho)~~` repitiendo el cuerpo exacto del pendiente cerrado.

---

## La interrupción intercalada

En medio de una conversación larga, la realidad interrumpe.

> [!tip] Dile a tu agente
> Espérate, me acaba de timbrar el flete con las cajas de témperas. Llegaron tres cajas rotas y manchadas, voy a tener que reclamar.

Esto sí es un hecho consumado que acaba de ocurrir.

### Mira `AHORA.md`

El agente debe registrar de inmediato el incidente en `AHORA.md` (con su hora y marca de pendiente para el reclamo), pero **sin perder el hilo** de la conversación sobre la Importadora Andina y el crédito bancario.

---

## Propuesta con rechazo limpio

> [!tip] Retoma el tema de Andina
> Bueno, volviendo a lo de Andina: el pedido grande va a tomar varias semanas de negociación.

El agente puede sugerir proactivamente: *"Como esto va a tomar varias semanas, ¿abrimos un ámbito nuevo para `importadora-andina`?"*.

> [!tip] Rechaza la sugerencia
> No, son solo un proveedor de insumos, déjalo dentro de compras.

### Mira la carpeta `ambitos/`

No se creó la carpeta `importadora-andina`. Y en ningún archivo del vault quedó una marca como "propuesta rechazada" ni registros de fricción. Una propuesta que el autor rechaza simplemente no ocurrió ([principio 3](../principios.md)).

---

## Ratificación final

Cierra la sesión resumiendo la resolución:

> [!tip] Dale el cierre definitivo
> Ya, en resumen: anota que el viernes a las diez voy al banco a firmar la ampliación de la línea, y que después de eso llamo a Andina para cerrar el pedido.

### Mira el vault al final de la sesión

Compara el vault antes y después de toda la conversación:
- No existen registros de "pedir la mitad" ni rastros de las dudas.
- Quedó registrado el hecho urgente de las témperas dañadas.
- Quedó cerrado el pendiente de la profesora Marcela.
- Quedó el compromiso en firme para el viernes con el banco y con Andina.

Toda la deliberación intermedia se decantó en las acciones que efectivamente se ratificaron.

---

Siguiente: [4. Una semana después](04-una-semana-despues.md).
