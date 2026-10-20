# spec · despacho

> A dónde va lo que el autor acaba de decir. Es la primera decisión de cada sesión y la toma el `AGENTS.md` de la raíz del vault, que carga la skill del asistente. Las familias de entrada vienen de [flujo-informacion.md](flujo-informacion.md); la conducta del ejecutor, de [agente.md](agente.md).

## Dos modos

La raíz empieza diciendo cómo te invocan, porque cambia todo lo demás, y lo dice por el primer prompt de la sesión y no por quién lo lanzó:

| El primer prompt... | Modo | El agente |
| --- | --- | --- |
| empieza con `MAINTENANCE MODE`, en mayúsculas | Mantenimiento | No carga nada más: ni `tuku context` ni otro archivo. Sigue las instrucciones del prompt tal como están, sin despachar y sin preguntar. Lo que pide una decisión del autor queda sin escribir y va en su respuesta final, hasta que se decida por dónde se comunican el autor y las entidades ([README.md](README.md), Decisiones abiertas). |
| empieza con cualquier otra cosa | Natural | Es una interacción con el autor: carga la skill del asistente, parte con `tuku context` y despacha con sus ejemplos. |

La marca es literal: `maintenance mode` en minúsculas, o la frase en medio del texto, no activa nada. Quien lanza al agente desde un cron, un proceso o con otro agente (`tuku doctor`, `tuku regenerate`, un proceso de `procesos/`) pone la marca al comienzo de su prompt; si falta, el agente trata la sesión como una conversación con el autor y pregunta. **Los límites valen en los dos modos** (ver "Los límites"): el modo de mantenimiento ahorra la carga, no los permisos.

## La raíz invoca, la skill despacha

El `AGENTS.md` de la raíz se lee entero en cada sesión, así que lleva solo lo que cambia todo lo demás: los dos modos, la skill que se carga en el modo natural y los límites. Las reglas de trabajo viven en [`reglas/skills/asistente/SKILL.md`](../template/vanilla/reglas/skills/asistente/SKILL.md), que se carga cuando hay un autor al que atender y no en el modo de mantenimiento. Una skill y no un archivo plano porque ese es el formato que un arnés sabe cargar por su descripción.

La skill lleva lo que el agente necesita en casi toda sesión para no abrir otros archivos, y lo agrupa por momento: al empezar (`tuku context` y la lectura del capítulo), qué comando corre (cierre o registro, lo tentativo, la duda), un dictado con varias cosas (un comando por hecho, en el orden dicho), los campos de cada comando, y al ejecutar y terminar. Las reglas de interpretación de [flujo-informacion.md](flujo-informacion.md) deciden si algo se escribe y con qué comando, así que van ahí, una sola vez y en el idioma del autor. Cómo se redacta cada cosa no va en la skill: es del [libro de estilo](vault.md).

## Los ejemplos de despacho

Esta spec fija su contrato. La skill despacha con ejemplos y no con una tabla: cada uno es una petición del autor en un bloque `>`, seguida de un bloque `bash` con el comando que dice qué capítulo del libro se lee y qué comando se ejecuta.

```
> Ya pagué el arriendo.

tuku context style --chapter Pendiente
tuku todo close "pagar el arriendo"
```

- **Cada familia del flujo tiene ejemplo.** Los hechos tienen tres (contar, dejar por hacer, dar por hecho), con los mismos campos y distinto comando, que es el que fija la marca. "A mano" y "desde las entidades" van sin ejemplo: el autor edita con su editor, y su respuesta a una entidad cae en otro ejemplo.
- **Lo que no tiene comando se dice sin bloque:** responder, o reformular y confirmar.
- **Solo comandos que existen.** Las cadencias y el cierre del ciclo tendrán ejemplo cuando su comando entre al CLI: el vault sembrado promete lo que puede hacer.
- **Comandos, no reglas.** Cómo se arma una línea lo sabe el comando, y lo que puede decir su salida (el rechazo con la corrección, el pedido de lo que falta) va ahí. Por eso los ejemplos le sirven también a una persona sin agente: son el índice de comandos.

## Qué se carga y cuándo

El `AGENTS.md` del destino manda sobre cómo se escribe ahí, y entre dos reglas gana la más cercana ([ambitos.md](ambitos.md)). Se carga solo lo que la petición necesita:

- **Un capítulo del libro**, con `tuku context style --chapter NOMBRE`, antes del primer comando de su tipo y una vez por sesión. Cada capítulo se basta solo y dice su «Lee también».
- **`AGENTS.md` por directorio**, cuando la regla depende de dónde se escribe: `ambitos/`, `notas/`, una rama del árbol.

La lectura una vez por sesión es una regla de la skill y no una compuerta del comando; si se mide que un agente se la salta, la salida es un estado local `.tuku/leidos`. Un directorio sin regla propia no tiene `AGENTS.md`: ausente significa vacío ([ambitos.md](ambitos.md)).

## Sin ejemplo, y el proceso nombrado

Una petición sin ejemplo se hace a mano, con dos condiciones: el ejecutor dice en una frase qué va a hacer, en palabras del autor, y espera el sí; con el sí, la hace entera, porque a medias el vault queda diciendo dos cosas a la vez. Una petición sin ejemplo que se repite es un comando que falta.

Un proceso es una rutina con nombre, y hay dos clases: los de `tuku`, deterministas (`tuku process cycle`), y los que el autor escribe en `procesos/`, que el agente ejecuta leyendo su archivo («corre el cierre de mes»). `tuku process` sin nombre lista los dos. Un proceso nombrado se ejecuta sin pasar por los ejemplos. Un proceso lanzado en modo de mantenimiento, igual que una entidad subordinada, ejecuta directo lo nombrado: esa cláusula corta la recursión del despacho.

## Los límites

La raíz cierra con una tabla de dos niveles, **pregunta primero** y **nunca**. Desde el primer día lleva editar a mano un archivo que tiene comando, actuar sobre una petición ambigua y tocar cualquier `AGENTS.md` o `reglas/`, salvo un `*.user.md` cuando el autor declara una preferencia. Valen también en modo de mantenimiento. Cada límite es verificable: se pide algo que cae en **nunca** y el diff queda vacío. Una petición ambigua se consulta antes de escribir; lo prohibido es decidir por el autor.

## Verificación

`tuku doctor` revisa que cada comando que nombran el `AGENTS.md` y la skill exista en el CLI. Ante un hallazgo informa y deja el archivo como está: en un vault en uso lleva reglas del autor ([cli.md](cli.md)).

## No entra

- Qué hace cada comando y qué escribe. Eso es la spec de la primitiva que toca, y el contrato común es [cli.md](cli.md).
- Cómo decide el ejecutor los campos de un registro. Eso es [agente.md](agente.md).
- Las familias de entrada y qué es una entidad subordinada. Eso es [flujo-informacion.md](flujo-informacion.md).
