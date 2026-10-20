# Tutorial

> Una semana de trabajo de Andrea, dictada a un agente. Cada paso dice qué decirle, qué debería pasar y por qué.

Vas a instalar TUKU, abrir un agente sobre una carpeta y hablarle como le hablarías a un secretario. Tú hablas. El agente decide qué comando `tuku` corresponde. El comando escribe los archivos.

Toma menos de una hora. Puedes pausar en cualquier capítulo: lo que lleves escrito queda utilizable.

## Cómo se lee cada capítulo

Cada paso tiene tres partes:

> [!tip] Dile a tu agente
> Lo que dices, tal cual. Si prefieres tu propio día, cambia los nombres y deja la forma.

> [!check] Qué debería pasar
> Lo que vas a encontrar en los archivos. Ábrelos y compruébalo.

Y debajo, una o dos líneas con el porqué.

Cuando te pido tocar un archivo tú, lo ves así. El bloque `edit` dice la edición exacta, para que sea repetible:

> [!warning] Edita a mano
> Lo que haces, en palabras.
>
> ```edit
> ARCHIVO: reemplaza "viejo" por "nuevo"
> ARCHIVO: borra la fila 1
> ARCHIVO: anota " (revisado)" en el primer registro
> deshacer
> ```

`deshacer` devuelve el archivo a como estaba cuando termina el paso.

**Este tutorial describe cómo debe funcionar TUKU.** Si algo de un `check` no pasa, es un defecto del sistema o del tutorial: anótalo. Por eso sirve también de prueba.

## Sobre el comando `tuku`

Tu agente lo usa por debajo y tú casi nunca lo escribes. Tú corres solo dos: instalar (`tuku init`) y revisar (`tuku doctor`).

## Quién es Andrea

Vende insumos escolares a colegios y trabaja sola. Sus clientes son Los Robles y el Liceo Andes, compra a la Importadora Andina y tiene una hija, la Emilia. Su lunes te da las frases para dictar, y cada capítulo sigue en el vault del anterior.

## Capítulos

| | Capítulo | Qué aprendes |
|---|---|---|
| 1 | [Instalar](01-instalar.md) | Qué quedó en disco, qué es tuyo y qué es de TUKU |
| 2 | [Registrar](02-registrar.md) | Dictar lo que pasó: el comando pone la hora, el ámbito y el formato |
| 3 | [Pendientes](03-pendientes.md) | Abrir, fechar, posponer y cerrar un compromiso |
| 4 | [Frentes y notas](04-frentes-y-notas.md) | Separar tu vida en frentes y guardar lo que sabes de una persona |
| 5 | [Corregir y revisar](05-corregir-y-revisar.md) | Arreglar lo mal dicho, y qué revisa `tuku doctor` |
| 6 | [El día completo](06-el-dia-completo.md) | Una jornada dictada de corrido |
| 7 | [Conversar](07-conversar.md) | Deliberar sin que se escriba nada hasta que ratifiques |
| 8 | [Una semana después](08-una-semana-despues.md) | El agente entiende de qué hablas con el historial |
| 9 | [Cerrar la semana](09-cerrar-la-semana.md) | Cambiar de ciclo sin perder nada, y lo que vuelve solo |
| 10 | [Lo que nadie pidió](10-lo-que-nadie-pidio.md) | Propuestas del agente y rechazos sin rastro |
| | [Conclusión](99-conclusion.md) | Lo que hiciste y por qué funciona |

Qué capítulos se cumplen hoy y cuáles faltan construir lo dice el [epic 010](../../devel/epics.md), que corre este tutorial entero como prueba.
