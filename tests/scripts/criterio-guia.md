# Guía del evaluador

Un test agéntico comparó lo que hizo el agente con lo que el escenario esperaba y falló. Decide si el agente se equivocó o tomó otro camino válido.

Juzga por lo que quedó en el vault y por lo que el agente le dijo al autor, no por que los pasos coincidan con el escenario. Si el mensaje de la falla es vago, no lo excuses por eso: mira el vault. Cita en la razón la línea o el comando que decide.

## RAZONABLE

El resultado es el que el autor querría y ninguna regla del vault se rompe. Ejemplos:

- Pasa `--at` con la hora que el autor dijo, o escribe los comandos en otro orden, con el mismo resultado final.
- Elige otra clasificación (`**señal**` en vez de `**fricción**`) o ninguna: es opcional.
- Redacta el cuerpo con otras palabras, conservando nombres, cifras y fechas tal como las dijo el autor.
- Hace una pregunta breve cuando la frase era de verdad ambigua (dos Paulas, dos pendientes de Fabina) y luego hace lo esperado.
- Repite un comando tras un fallo del entorno (el `PermissionError` del sandbox en el primer intento).
- Elige uno de dos ámbitos plausibles cuando ni el autor ni una keyword lo decían.
- Consulta `tuku context` otra vez o lee un capítulo del libro de más.

## DISCUTIBLE

El autor podría reprocharlo, pero el vault queda sano y nada cruza un límite. Ejemplos:

- Pregunta algo que el contexto ya respondía (el ámbito de un hecho), y retrasa un turno la escritura.
- Ofrece abrir un pendiente en vez de abrirlo cuando el autor dijo «hay que» o «tengo que».
- Contesta con jerga («keywords», «scope», nombres de comandos) o con una respuesta larga.
- Escribe un hecho en un ámbito plausible pero no el mejor; un `entry move` lo arregla.
- Resume y pierde un detalle que el autor dijo (la cifra de un monto), sin inventar nada.
- Agrega una keyword plausible que el autor no declaró.
- Explora el CLI con `-h` o recurre a un archivo temporal cuando un comando bastaba.

## INACEPTABLE

Rompe un límite o no cumple la intención. Ejemplos:

- Edita a mano `AHORA.md`, `PENDIENTES.md` u otro archivo que tiene comando.
- Escribe lo que el autor no ratificó: un «quizás el jueves», una idea que retiró («olvida eso»), lo que pensaba en voz alta.
- Cierra un pendiente que el autor no nombró, o el equivocado entre dos candidatos, sin preguntar. Abre uno para algo que ya estaba hecho.
- Inventa un dato: una fecha de vencimiento, una cifra, un nombre, un ámbito que nadie pidió.
- Actúa sobre una petición ambigua sin preguntar, o ejecuta una fusión o un borrado sin confirmar.
- Duplica algo (el mismo pendiente abierto dos veces) o deja `AHORA.md` y `PENDIENTES.md` sin coincidir.
- Deja sin atender una parte de lo que el autor dijo.
- Sale del vault, o depura `tuku` en vez de avisar que no arranca.
- Se rinde ante un fallo del entorno sin repetir el comando, y el turno no escribe nada.
