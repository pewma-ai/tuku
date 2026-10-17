# spec · despacho

> A dónde va lo que el autor acaba de decir. Es la primera decisión de cualquier sesión y la toma el `AGENTS.md` de la raíz del vault. Las familias de entrada vienen de [flujo-informacion.md](flujo-informacion.md); acá se bajan a filas con comando. Qué ocurre después lo especifica cada primitiva, y cómo se comporta el ejecutor una vez despachado está en [agente.md](agente.md).

## El `AGENTS.md` de la raíz enruta, no explica

Es el único documento que se lee entero en toda sesión, así que es el más caro del vault y el que más se degrada al crecer. Su trabajo es decidir el destino y nada más.

Todo lo que dice **cómo** se hace algo vive donde se hace y se carga al llegar ahí: el `AGENTS.md` del directorio de destino, el archivo de reglas de la consecuencia o la salida del propio comando. Una regla que solo aplica a las notas, escrita en la raíz, se paga en cada sesión que no toca notas.

**Medido, la raíz lleva además lo que evita abrir otros archivos.** Cada archivo que el agente abre antes de escribir cuesta una llamada al modelo (3 a 4 s con un modelo barato). Con "Lee antes" para todo, un turno que escribe promediaba 9,7 llamadas y 53 s. Con las reglas de ejecución (un pedido, un comando; no leer ni verificar de más), los campos de los comandos y un ejemplo de cada uno en la raíz, promedia 3,6 llamadas y 22 s. Lo que entra a la raíz es lo que el agente necesita en casi toda sesión.

La prueba para saber si una línea pertenece a la raíz: si la respuesta cambia el destino, va en la raíz. Si solo cambia la ejecución una vez elegido el destino, va abajo.

## De la familia a la fila

El flujo clasifica las entradas en familias. El despacho las concreta en filas: cada familia tiene al menos una, o queda anotada como familia sin comando.

| Familia | Fila |
| --- | --- |
| Hechos | una por cada forma de decirlo: contar, dejar por hacer, dar por hecho |
| Decisiones del autor | una por comando: crear un frente, anidarlo, nombrarlo, guardar una nota, abrir el ciclo, corregir |
| Conversación | una fila sin comando |
| Sin camino | dos filas sin comando: reformular y confirmar, y el proceso nombrado |
| A mano | sin fila: el autor no necesita agente |
| Desde las entidades | sin fila propia: la respuesta del autor cae en una de las anteriores |

Dos filas no existen aunque su familia las pide, porque la tabla **nombra solo comandos que existen**: las cadencias y el cierre del ciclo. El vault sembrado no promete lo que no puede hacer, y entran el día que el comando entre al CLI.

## La tabla de despacho

Vive en el `AGENTS.md` de la raíz y es lo que el ejecutor consulta antes de actuar. Mapea la señal del autor a un comando. Esta es la forma que tiene, con el habla del autor en la primera columna:

| El autor... | Ejemplo | Comando |
| --- | --- | --- |
| cuenta algo que pasó | «a las once me reuní con Rodrigo Álvarez por la versión 2» | `tuku entry add` |
| deja algo por hacer | «recuérdame renovar el seguro», «para el lunes» | `tuku todo open` |
| da por hecho algo que estaba pendiente | «ya pagué el arriendo» | `tuku todo close` |
| nombra un frente que todavía no existe | «abre faena» | `tuku scope create` |
| dice que un frente es parte de otro | «faena-ai va dentro de faena» | `tuku scope move` |
| dice qué palabras delatan un frente | «si te hablo de la planta o de FNA, es de faena» | `tuku scope keywords` |
| pide guardar una idea que no es de un día | «guárdame esto: cómo se prorroga un arriendo» | `tuku note create` |
| empieza el ciclo | «empecemos la semana» | `tuku cycle open` |
| corrige algo ya escrito | «no era eso, cámbiale el nombre» | `tuku entry rename`, `scope rename`, `note rename` |
| nombra un proceso del vault | «corre el cierre de mes» | el que el proceso diga |
| pide algo que ninguna fila cubre | «junta estos tres ámbitos en uno» | ninguno: reformula y confirma |
| pregunta, delibera o pide investigar | «¿qué me quedaba abierto hoy?» | ninguno: se responde, no se escribe |

Las tres primeras filas son la familia de hechos. Comparten reglas y campos y difieren en el comando, que fija la marca: abrir y cerrar un pendiente es solo de `tuku todo`. `tuku entry add` rechaza `**pendiente**` y `(Hecho)` y nombra el comando correcto, así que equivocarse de fila se corrige con la salida y no deja nada escrito.

La tabla nombra comandos y no reglas. Quien la lee no necesita saber cómo se arma una línea ni cómo se propaga un pendiente, solo qué comando lo hace ([agente.md](agente.md)). Es también lo que la hace servir a una persona sin ningún agente instalado, que la lee como el índice de comandos que es.

Los disparadores se escriben en el habla del autor. Una fila que dice "cuando el autor requiera dar de alta una entidad de ámbito" no la activa nadie hablando.

La ambigüedad no es una fila: la resuelve quien interpreta, o la deja escrita tal cual la dijo el autor, según [flujo-informacion.md](flujo-informacion.md).

## Qué agrega el `AGENTS.md` a la tabla

La tabla del `AGENTS.md` lleva una columna más que esta spec no necesita: **Lee antes**. Dice qué archivo se abre antes de ejecutar esa fila, y es un nombre, no una pista. Sin él la regla que vive abajo depende de que el ejecutor decida ir a buscarla, y esa decisión es el punto donde una cascada se rompe en silencio. Con ella, lo que no se usa sigue sin cargarse.

Una fila que dice `nada` no es una fila sin reglas: es una cuyo comando se explica solo con su salida. Cuando deje de bastar, aparece el archivo.

## La cascada

La raíz elige el destino. El `AGENTS.md` del destino manda sobre cómo se escribe ahí, y ante dos reglas que aplican gana la más cercana ([ambitos.md](ambitos.md)).

Nada de eso viaja en el contexto base, y hay dos formas de cargarlo tarde que no compiten:

- **`AGENTS.md` por directorio** cuando la regla se define por dónde se escribe: `ambitos/`, `notas/`, una rama concreta del árbol. Se carga al entrar ahí.
- **`reglas/<consecuencia>.tuku.md`** cuando la consecuencia no tiene directorio propio, como las propuestas o las cadencias. Se abre solo cuando lo escrito dispara esa consecuencia, así que un registro sin consecuencias no carga ninguna.

La lista de reglas puede crecer sin encarecer cada sesión: se paga solo por la que se usa. Un directorio sin regla propia deja su `AGENTS.md` vacío, para que quien escriba una regla sepa dónde ponerla sin preguntar.

## Lo que ninguna fila cubre

Una petición que no calza en ninguna fila no se rechaza ni se despacha a ciegas: se hace a mano. Un agente sabe hacerla, le cuesta más caro y le sale menos seguro que un comando, y ese costo es la razón de que exista la vía y de que tenga condiciones.

Antes de tocar nada, el ejecutor dice en una frase qué va a hacer, en palabras del autor y no en las suyas, y espera el sí. Reformular no es devolverle la pregunta: es decir qué entendió, para que el autor corrija antes de que esté escrito y no después. Con el sí, se hace entero, porque a medias deja el vault diciendo dos cosas a la vez.

De acá salen comandos. Una petición sin fila que se repite es un comando que falta, y esa es la vía por la que el diseño se entera.

## El escape: un proceso nombrado

Cuando el autor nombra el proceso que quiere, no hay nada que inferir: se lee ese archivo y se ejecuta lo que dice. El despacho se salta entero. Es la salida para lo que hoy no existe y va a existir: informes, mantenciones y automatizaciones que el autor invoca por su nombre. Viven en `procesos/`, que no se siembra el día uno y aparece cuando haya el primero, igual que `bitacoras/`.

Un proceso lanzado por otro agente para ejecutar algo nombrado **es** ese ejecutor y no vuelve a despachar. Sin esa cláusula el despacho se llama a sí mismo. Vale igual para las entidades subordinadas del flujo.

## Los límites, en una tabla de dos niveles

El `AGENTS.md` de la raíz cierra con lo que no se despacha nunca, en dos niveles y sin prosa: **pregunta primero** y **nunca**. Editar a mano un archivo que tiene comando, actuar sobre una petición ambigua y tocar cualquier `AGENTS.md` están en la lista desde el primer día.

Un límite escrito así es una afirmación sobre el vault después de la sesión: se pide algo que cae en **nunca** y se comprueba que el diff quedó vacío. Actuar sobre una petición ambigua no incluye escribirla tal cual la dijo el autor: lo que se prohíbe es decidir por él.

## Cómo se verifica que la tabla no miente

La tabla es texto en un archivo del vault y el CLI evoluciona aparte, así que envejece. `tuku doctor` revisa que cada comando nombrado en la tabla exista en la superficie real del CLI, y que cada familia del flujo tenga su fila o esté anotada sin comando. Lo mismo hace con los `type` y [`reglas/types.md`](../template/vanilla/reglas/types.md).

Ante un hallazgo informa y no corrige: el `AGENTS.md` de un vault en uso lleva las reglas que el autor le agregó, y sobreescribirlo es consecuencia mayor. Los temas con reparación determinista (hoy `link`) nombran `tuku fix TEMA`, y si `fix` devuelve decisiones se le plantean al autor ([cli.md](cli.md)).

## No entra

- Qué hace cada comando y qué escribe. Eso es la spec de la primitiva que toca, y el contrato común es [cli.md](cli.md).
- Cómo el ejecutor decide los campos de un registro. Eso es [agente.md](agente.md).
- Las familias de entrada y qué es una entidad subordinada. Eso es [flujo-informacion.md](flujo-informacion.md).
