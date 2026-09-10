# spec · despacho

> A dónde va lo que el autor acaba de decir. Es la primera decisión de cualquier sesión y la toma el `AGENTS.md` de la raíz del vault. Qué ocurre después de esa decisión lo especifica cada primitiva; cómo se comporta el ejecutor una vez despachado está en [agente.md](agente.md).

## El `AGENTS.md` de la raíz enruta, no explica

Es el único documento que se lee entero en toda sesión, así que es el más caro del vault y el que más se degrada al crecer. Su trabajo es decidir el destino y nada más.

Todo lo que dice **cómo** se hace algo vive donde se hace y se carga al llegar ahí: el `AGENTS.md` del directorio de destino, o el archivo de reglas de la consecuencia. Una regla que solo aplica a las notas escrita en la raíz se paga en cada sesión que no toca notas.

De ahí la prueba para saber si una línea pertenece a la raíz: si la respuesta cambia el destino, va en la raíz; si solo cambia la ejecución una vez elegido el destino, va abajo.

## Las tres vías

No hay taxonomía nueva. [`../devel/epics.md`](../devel/epics.md) fija que el vault se cambia por la vía bitácora o por comando directo y que no existe una tercera, y el despacho decide entre esas dos, más el caso que no escribe:

1. **Vía bitácora.** El autor cuenta algo que ocurrió. Se escribe el registro con `tuku entry add` y las consecuencias las deriva el sistema releyendo lo escrito ([flujo-informacion.md](flujo-informacion.md)). Es el caso por defecto y el más frecuente.
2. **Vía comando directo.** El autor pide una operación de sistema o toma una decisión explícita que ningún hecho justifica: abrir o cerrar un pendiente, moverlo de escalón, crear un ámbito, abrir una nota o el ciclo. Toda operación mutadora por esta vía estampa automáticamente constancia cronológica en `AHORA.md` (con fallback de fecha a **HOY** y hora a **AHORA** en `TZ`), de modo que no existan decisiones sin registro temporal.
3. **Sin despacho.** Deliberar, consultar el estado, investigar, redactar un borrador. No toca ningún archivo del conjunto canónico. Termina en respuesta, no en escritura.

Que la primera vía cubra casi todo es lo que mantiene corta la tabla: el despacho fino es la excepción.

## La tabla de despacho

Vive en el `AGENTS.md` de la raíz y es lo que el ejecutor consulta antes de actuar. Mapea señal del autor a destino y a comando, en ese orden:

| El autor... | Vía | Lee antes | Comando |
| --- | --- | --- | --- |
| cuenta algo que ocurrió | bitácora | `reglas/bitacora.tuku.md` | `tuku entry add` |
| dice que algo quedó por hacer | bitácora, marca `**pendiente**` | `reglas/bitacora.tuku.md` | `tuku entry add` |
| da por hecho algo que estaba pendiente | bitácora, marca `~~(Hecho)~~` | `reglas/bitacora.tuku.md` | `tuku entry add` |
| abre un pendiente sin dictado | comando directo | nada | `tuku todo open` |
| cierra un pendiente sin dictado | comando directo | nada | `tuku todo close` |
| nombra un frente que todavía no existe | comando directo | `ambitos/AGENTS.md` | `tuku scope create` |
| pide guardar una idea que no es de un día | comando directo | `reglas/notas.tuku.md` | `tuku note create` |
| abre el ciclo | comando directo | nada | `tuku cycle open` |
| corrige algo que ya quedó escrito | comando directo | nada | `tuku entry rename` / `scope rename` / `note rename` |
| nombra un proceso del vault | escape, ver abajo | el proceso | el que el proceso indique |
| pide algo que ninguna fila cubre | a mano | nada | ninguno: reformular y confirmar |
| pregunta, delibera o pide investigar | sin despacho | nada | ninguno |

La columna **Lee antes** es la que hace que la cascada funcione sin explorar. Dice qué archivo se abre antes de ejecutar esa fila, y es un nombre, no una pista: sin él la regla que vive abajo depende de que el ejecutor decida ir a buscarla, y esa decisión es el punto donde una cascada se rompe en silencio. Con ella, lo que no se usa sigue sin cargarse, que es todo lo que la cascada quería.

Una fila que dice `nada` no es una fila sin reglas: es una cuyo comando se explica solo con su `-h`. Cuando deje de bastar, aparece el archivo y se nombra acá.

**La tabla nombra solo comandos que existen.** Cerrar el ciclo y cambiar un pendiente de horizonte están en el diseño y todavía no tienen comando, así que no tienen fila: el vault sembrado no promete lo que no puede hacer, y `tuku doctor` lo comprueba (ver abajo). Entran acá el día que el comando entre a la superficie del CLI.

Las tres primeras filas son el mismo comando y difieren solo en la marca, que es juicio. Esa es la forma que se busca: pocas entradas, y la diferencia entre ellas en los campos, no en el comando.

La tabla nombra comandos y no reglas. Quien la lee no necesita saber cómo se arma una línea ni cómo se propaga un pendiente, solo qué comando lo hace ([agente.md](agente.md)). Es también lo que la hace servir a una persona sin ningún agente instalado, que la lee como el índice de comandos que es.

Los disparadores se escriben en el habla del autor y no en el vocabulario del sistema. Una fila que dice "cuando el autor requiera dar de alta una entidad de ámbito" no la activa nadie hablando.

## La cascada

La raíz elige el destino. El `AGENTS.md` del destino manda sobre cómo se escribe ahí, y ante dos reglas que aplican gana la más cercana ([ambitos.md](ambitos.md)).

Nada de eso viaja en el contexto base, y hay dos formas de cargarlo tarde que no compiten:

- **`AGENTS.md` por directorio** cuando la regla se define por dónde se escribe: `ambitos/`, `notas/`, una rama concreta del árbol. Se carga al entrar ahí.
- **`reglas/<consecuencia>.tuku.md`** cuando la consecuencia no tiene directorio propio, como las propuestas o las cadencias. Se abre solo cuando el paso 3 del flujo detectó que esa consecuencia aplica ([flujo-informacion.md](flujo-informacion.md)), así que un registro sin consecuencias no carga ninguna.

Es lo que permite que la lista de reglas crezca sin encarecer cada sesión: se paga solo por la que se usa. Un directorio sin regla propia deja su `AGENTS.md` vacío, para que quien escriba una regla sepa dónde ponerla sin preguntar.

## Lo que ninguna fila cubre

Una petición que no calza en ninguna fila no se rechaza ni se despacha a ciegas: se hace a mano. Un agente sabe hacerla, le cuesta más caro y le sale menos seguro que un comando, y ese costo es la razón de que exista la vía y de que tenga condiciones.

Antes de tocar nada, el ejecutor dice en una frase qué va a hacer, en palabras del autor y no en las suyas, y espera el sí. Reformular no es devolverle la pregunta: es decir qué entendió, para que el autor corrija antes de que esté escrito y no después. Una vez con el sí, se hace entero, porque a medias deja el vault diciendo dos cosas a la vez.

De acá salen comandos. Una petición sin fila que se repite es un comando que falta, y esa es la vía por la que el diseño se entera ([`../devel/epics.md`](../devel/epics.md), "los epics mueven el diseño").

## El escape: un proceso nombrado

Cuando el autor nombra el proceso que quiere, no hay nada que inferir: se lee ese archivo y se ejecuta lo que dice. El despacho se salta entero.

Es la salida prevista para lo que hoy no existe y va a existir: informes, mantenciones y automatizaciones que el autor invoca por su nombre. Viven en `procesos/`, que no se siembra el día uno y aparece cuando haya el primero, igual que `bitacoras/`.

## Los límites, en una tabla de dos niveles

El `AGENTS.md` de la raíz cierra con lo que no se despacha nunca, en dos niveles y sin prosa: **pregunta primero** y **nunca**. Editar a mano un archivo que tiene comando, actuar sobre una petición ambigua y tocar cualquier `AGENTS.md` están en la lista desde el primer día.

La forma importa porque es lo que la vuelve verificable: un límite escrito así es una afirmación sobre el vault después de la sesión. Se pide algo que cae en **nunca** y se comprueba que el diff quedó vacío.

## Cómo se verifica que la tabla no miente

La tabla es texto en un archivo del vault y el CLI evoluciona aparte, así que envejece. `tuku doctor` revisa que cada comando nombrado en la tabla exista en la superficie real del CLI, del mismo modo que revisa los `type` contra [`reglas/types.md`](../template/vanilla/reglas/types.md).

Ante un hallazgo informa y no corrige: el `AGENTS.md` de un vault en uso lleva las reglas que el autor le agregó, y sobreescribirlo es consecuencia mayor.

## El segundo eje, anotado y fuera

`mac-jpgil` tiene un eje más: todo lo que modifica archivos corre en un subproceso aislado y solo la bitácora queda inline, para que el chat conteste de inmediato. Lo agregó el autor tres meses después de la primera versión y por presión de latencia, no de diseño ([`../devel/lecciones-macjpgil.md`](../devel/lecciones-macjpgil.md)).

Queda anotado como la respuesta conocida cuando el problema aparezca. No entra ahora, porque partir el despacho por aislamiento obliga a diseñar contra un arnés concreto, que es justo lo que esta spec evita.

Sí entra desde el primer día su cláusula de recursión: una sesión lanzada por otro agente para ejecutar algo nombrado **es** ese ejecutor, y no vuelve a despachar. Sin ella el despacho se llama a sí mismo.

## No entra

- Qué hace cada comando y qué escribe. Eso es la spec de la primitiva que toca, y el contrato común es [cli.md](cli.md).
- Cómo el ejecutor decide los campos de un registro. Eso es [agente.md](agente.md).
- Cómo se conduce una sesión de agente para verificarlo. Es material de pruebas y lo construye el epic 004 ([`../devel/epics.md`](../devel/epics.md)).
