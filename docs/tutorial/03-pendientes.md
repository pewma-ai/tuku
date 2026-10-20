# 3. Pendientes

> Abrir, fechar, posponer y cerrar un compromiso.

Un **pendiente** es un compromiso abierto. Vive en una fila de `PENDIENTES.md`, la única fuente de lo que está por hacer, y deja además un registro `**pendiente**` en `AHORA.md`. La fila y el registro dicen lo mismo, palabra por palabra.

## Con fecha relativa

> [!tip] Dile a tu agente
> Me llamó don Rodolfo del Colegio Los Robles, quieren cotización para el segundo semestre: doscientos cuadernos, cincuenta resmas y material de arte. Se la mando mañana.

> [!check] Qué debería pasar
> - `AHORA.md` tiene dos registros: la llamada, y el compromiso de mandar la cotización marcado `**pendiente**`.
> - `PENDIENTES.md` tiene una fila nueva con el mismo texto del compromiso.
> - La columna `Vence` trae la fecha de mañana.

Una frase puede traer dos cosas, un hecho y un compromiso, y el agente las separa. Que el texto de la fila sea idéntico al del registro importa: cerrar un pendiente es repetir su texto.

## Con día y hora

> [!tip] Dile a tu agente
> Recuérdame que la Emilia tiene reunión de apoderados el jueves a las siete.

> [!check] Qué debería pasar
> - La palabra «recuérdame» no está en ningún registro: es una instrucción para el agente, no un hecho.
> - `Vence` trae el jueves con la hora 19:00.
> - `AHORA.md` muestra el pendiente bajo el encabezado del jueves.

## Sin fecha

> [!tip] Dile a tu agente
> Recuérdame a fin de mes renovar el seguro del auto.

> [!check] Qué debería pasar
> - La fila tiene el horizonte `fin de mes` y la columna `Vence` vacía.
> - Nadie inventó un «31 de agosto».

Un pendiente sin fecha cuelga de un **horizonte**, un escalón de la escalera que defines en `reglas/pendientes.user.md`: `esta semana`, `próxima semana`, `fin de mes`. Si no dices nada, nace en `esta semana` y aparece en el recuadro «Pendientes de esta semana» al inicio de `AHORA.md`. Postergar es mover la fila a un escalón más lejano, y lo decides tú.

## Cerrar

> [!tip] Dile a tu agente
> Ya le mandé la cotización a Los Robles, quedó en un millón ochocientos más IVA.

> [!check] Qué debería pasar
> - La fila de la cotización desapareció de `PENDIENTES.md`.
> - `AHORA.md` tiene el cierre `(Hecho): ~~…~~` con la hora de ahora y el texto tachado.
> - El registro que abrió el compromiso, escrito hoy, se retiró: el día no lo cuenta dos veces.
> - El monto, un millón ochocientos más IVA, quedó en un registro propio.

Un mismo comando retira la fila y escribe la constancia. Si el texto no coincide con ninguna fila, el comando avisa y deja solo el registro.

## Lo que ya estaba hecho

> [!tip] Dile a tu agente
> Pagué las cotizaciones de la Katia en Previred, alcancé justo.

> [!check] Qué debería pasar
> - `PENDIENTES.md` no tiene filas nuevas y las que había siguen iguales.
> - `AHORA.md` tiene un registro directo, sin `**pendiente**` ni `(Hecho)`.

Eso nunca fue un pendiente. Inventar uno para poder cerrarlo falsearía tu historial.

## Lo que no es firme

> [!tip] Dile a tu agente
> Quizás el jueves le escribo a la Viana.

> [!check] Qué debería pasar
> - Ningún archivo cambió.

Solo un hecho firme escribe. Un «quizás» se contesta y se queda en la conversación.

Siguiente: [4. Frentes y notas](04-frentes-y-notas.md).
