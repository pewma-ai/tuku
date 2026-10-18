# spec · despacho

> A dónde va lo que el autor acaba de decir. Es la primera decisión de cada sesión y la toma el `AGENTS.md` de la raíz del vault. Las familias de entrada vienen de [flujo-informacion.md](flujo-informacion.md); la conducta del ejecutor, de [agente.md](agente.md).

## Dos modos

La raíz empieza diciendo cómo te invocan, porque cambia todo lo demás, y lo dice por el primer prompt de la sesión y no por quién lo lanzó:

| El primer prompt... | Modo | El agente |
| --- | --- | --- |
| empieza con `MAINTENANCE MODE`, en mayúsculas | Mantenimiento | No carga nada más: ni `tuku context` ni otro archivo. Sigue las instrucciones del prompt tal como están, sin despachar y sin preguntar. Lo que pide una decisión del autor queda sin escribir y va en su respuesta final, hasta que se decida por dónde se comunican el autor y las entidades ([README.md](README.md), Decisiones abiertas). |
| empieza con cualquier otra cosa | Natural | Es una interacción con el autor: parte con `tuku context` y despacha con la tabla. |

La marca es literal: `maintenance mode` en minúsculas, o la frase en medio del texto, no activa nada. Quien lanza al agente desde un cron, un proceso o con otro agente (`tuku doctor`, `tuku regenerate`, un proceso de `procesos/`) pone la marca al comienzo de su prompt; si falta, el agente trata la sesión como una conversación con el autor y pregunta. **Los límites valen en los dos modos** (ver "Los límites"): el modo de mantenimiento ahorra la carga, no los permisos.

## La raíz enruta

El `AGENTS.md` de la raíz se lee entero en cada sesión: es el archivo más caro del vault. Una línea va en la raíz si cambia el destino; si cambia la ejecución una vez elegido el destino, va abajo. Las reglas de interpretación de [flujo-informacion.md](flujo-informacion.md) deciden si algo se escribe y con qué comando, así que van en la raíz, una sola vez y en el idioma del autor.

También va en la raíz lo que el agente necesita en casi toda sesión para no abrir otros archivos: las reglas de ejecución (un pedido, un comando), los campos de cada comando y un ejemplo de cada uno. Cada archivo que abre antes de escribir es una llamada más al modelo.

## La tabla de despacho

La tabla vive en la sección "A dónde va lo que el autor dice" del [`AGENTS.md` del template](../template/vanilla/AGENTS.md). Esta spec fija su contrato:

| Columna | Qué lleva |
| --- | --- |
| **El autor...** | Lo que hace el autor, en su habla y con frases de ejemplo («ya pagué», «ábrelo aparte»), porque así es como se dispara |
| **Lee antes** | El único archivo que se abre antes de ejecutar, o `nada` cuando la salida del comando basta |
| **Comando** | Un comando `tuku` que existe, o qué hacer sin comando: responder, o reformular y confirmar |

- **Cada familia del flujo tiene fila.** Los hechos tienen tres (contar, dejar por hacer, dar por hecho), con los mismos campos y distinto comando, que es el que fija la marca. "A mano" y "desde las entidades" van sin fila: el autor edita con su editor, y su respuesta a una entidad cae en otra fila.
- **Solo comandos que existen.** Las cadencias y el cierre del ciclo tendrán fila cuando su comando entre al CLI: el vault sembrado promete lo que puede hacer.
- **Comandos, no reglas.** Cómo se arma una línea lo sabe el comando, y lo que puede decir su salida (el rechazo con la corrección, el pedido de lo que falta) va ahí. Por eso la tabla le sirve también a una persona sin agente: es el índice de comandos.

## Qué se carga y cuándo

El `AGENTS.md` del destino manda sobre cómo se escribe ahí, y entre dos reglas gana la más cercana ([ambitos.md](ambitos.md)). Lo de abajo se carga cuando la fila lo nombra en "Lee antes":

- **`AGENTS.md` por directorio**, cuando la regla depende de dónde se escribe: `ambitos/`, `notas/`, una rama del árbol.
- **`reglas/<consecuencia>.tuku.md`**, cuando la consecuencia es transversal, como las propuestas o las cadencias.

Que la fila nombre el archivo es lo que sostiene la cascada: si el ejecutor tuviera que decidir ir a buscar la regla, ahí se rompería en silencio. Así cada sesión paga solo las reglas que usa. Un directorio sin regla propia no tiene `AGENTS.md`: ausente significa vacío ([ambitos.md](ambitos.md)).

## Sin fila, y el proceso nombrado

Una petición sin fila se hace a mano, con dos condiciones: el ejecutor dice en una frase qué va a hacer, en palabras del autor, y espera el sí; con el sí, la hace entera, porque a medias el vault queda diciendo dos cosas a la vez. Una petición sin fila que se repite es un comando que falta.

Un proceso es una rutina con nombre, y hay dos clases: los de `tuku`, deterministas (`tuku process cycle`), y los que el autor escribe en `procesos/`, que el agente ejecuta leyendo su archivo («corre el cierre de mes»). `tuku process` sin nombre lista los dos. Un proceso nombrado se ejecuta sin pasar por la tabla. Un proceso lanzado en modo de mantenimiento, igual que una entidad subordinada, ejecuta directo lo nombrado: esa cláusula corta la recursión del despacho.

## Los límites

La raíz cierra con una tabla de dos niveles, **pregunta primero** y **nunca**. Desde el primer día lleva editar a mano un archivo que tiene comando, actuar sobre una petición ambigua y tocar cualquier `AGENTS.md`. Valen también en modo de mantenimiento. Cada límite es verificable: se pide algo que cae en **nunca** y el diff queda vacío. Una petición ambigua se consulta antes de escribir; lo prohibido es decidir por el autor.

## Verificación

`tuku doctor` revisa que cada comando de la tabla exista en el CLI. Ante un hallazgo informa y deja el `AGENTS.md` como está: en un vault en uso lleva reglas del autor ([cli.md](cli.md)).

## No entra

- Qué hace cada comando y qué escribe. Eso es la spec de la primitiva que toca, y el contrato común es [cli.md](cli.md).
- Cómo decide el ejecutor los campos de un registro. Eso es [agente.md](agente.md).
- Las familias de entrada y qué es una entidad subordinada. Eso es [flujo-informacion.md](flujo-informacion.md).
