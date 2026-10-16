# spec · cli

> El contrato del comando `tuku`: qué garantiza, cómo informa y con qué códigos sale. Es independiente de quién invoque, persona o agente. Lo que cambia cuando el invocador es un agente está en [agente.md](agente.md).

## Qué es dueño el comando

`tuku` es la capa determinista del sistema. Es dueño de la **forma**: dónde va cada cosa, con qué estructura, en qué orden, y qué invariantes no se pueden romper. No es dueño del **juicio**: qué se registra, con qué palabras, bajo qué clasificación y a qué ámbito pertenece.

El corte no pasa entre estructura y lenguaje, pasa por los **campos**. Quien invoca llena los campos; `tuku` construye la línea canónica de [bitacora.md](bitacora.md), la sitúa en el día que corresponde y mantiene el orden cronológico. Llenar los campos es exactamente el trabajo de inferencia: de qué ámbito es, qué clasificación le cabe, si un dictado da uno o varios registros.

Ese reparto sostiene el principio 1 de [`../docs/principios.md`](../docs/principios.md). Un autor disciplinado hace lo mismo a mano con un editor básico: el comando le ahorra el esfuerzo, no habilita nada que sin él sea imposible. Si un comando empieza a decidir cosas que una persona no podría reproducir a mano, el defecto está en el comando.

**Ningún comando infiere un campo que quien invoca no dio**, salvo donde una spec declare un valor por defecto. Los que hay hoy: el día (la fecha actual, **HOY**) y la hora (la hora actual, **AHORA**) de un registro o de la huella en bitácora dejada por un comando mutador (`todo`, `scope`, `note`), evaluados en la zona horaria `TZ` del vault ([bitacora.md](bitacora.md)); y la fecha de un pendiente escrito bajo un día posterior a HOY, que es ese día ([pendientes.md](pendientes.md)).

## Los códigos de salida

Son contrato. Quien invoca decide qué hacer según el código, sin leer el mensaje.

| Código | Significa | Qué hacer |
| --- | --- | --- |
| 0 | Éxito | Seguir |
| 1 | Rechazo: el comando entendió y se negó por el estado del vault | Corregir el estado, o pasar el flag que la salida indica |
| 2 | Error de uso: la invocación está mal formada | Corregir la invocación |
| 3 | Entorno: la instalación de TUKU no está donde debería | No reintentar; se arregla la instalación, no el comando |

El **2 está reservado**: lo emite argparse ante una invocación mal formada y ningún comando puede devolverlo por otra causa. Un rechazo y un comando mal escrito son cosas distintas, y quien invoca tiene que poder distinguirlas sin leer prosa. Es un choque real y ya ocurrió: `TukuHomeInvalido` devolvía 2, igual que argparse, y desde fuera no había forma de saber si corregir el comando o la instalación.

Códigos nuevos se agregan a esta tabla antes que al código. Fijados en `tuku/cli/` como constantes con nombre, nunca como literales.

## La salida es una sola, para persona y para agente

Un solo mensaje en prosa, que sirve a los dos. **Sin `--json`.** Hoy no lo consume nadie, obligaría a mantener y probar dos caminos de salida, y sobre todo le daría una salida de escape a la prosa: en cuanto el agente lee otra cosa, el mensaje humano deja de importar y se degrada. Los códigos de salida ya son el canal legible por máquina y no necesitan formato estructurado.

**Toda salida de error nombra el defecto y la corrección.** Decir qué pasó no basta; hay que decir qué hacer. `tuku init` sobre un directorio con contenido no dice solo que está ocupado, dice que `--force` lo reemplaza. La regla vale igual para la persona que escribió rápido y para el agente que tiene que decidir el paso siguiente, y por eso el mensaje es uno solo.

Que se cumpla es verificable: la ayuda y los códigos de cada epic se fijan en un escenario, según la convención de [`../devel/epics.md`](../devel/epics.md).

## Fuera de un vault, ningún comando opera

Todo comando que recibe `--vault` (por defecto, el directorio actual) rechaza con código 1 si ese directorio no tiene ninguno de los archivos requeridos de un vault, y no lee ni escribe nada. Sin la regla, `tuku doctor` invocado desde `~` recorría el disco entero. Basta con que exista uno: un vault al que le falta un archivo sigue siendo un vault y es justo lo que `tuku doctor` debe diagnosticar. `tuku note lint <archivo>` queda fuera porque revisa un archivo suelto. `tuku init` tampoco opera sobre un vault, pero tiene su propia regla: **rechaza con código 1 el home del usuario y todo directorio que lo contenga**, incluida la raíz del disco, aun con `--force`, que borra el destino antes de sembrar. Vale igual en Mac, Linux y Windows.

## Ante la duda, informar y no escribir

Un comando que no puede determinar algo **no lo adivina y no escribe a medias**. Sale con el código que corresponde y dice qué le falta. Es el principio 3 de [`../docs/principios.md`](../docs/principios.md) aplicado a la capa determinista, y es lo que hace que la salida sirva como advertencia en vez de como registro de un daño ya hecho.

De ahí la asimetría de `tuku entry lint` ([bitacora.md](bitacora.md)): informa y nunca escribe. Verificar y corregir son operaciones distintas, y mezclarlas quita la oportunidad de revisar.

**Ningún comando de verificación repara.** Vale para los `lint` y para `tuku doctor`, que los agrega y revisa además lo que ninguno cubre. Ante un hallazgo, el doctor o linter nombra el defecto y la acción correctiva, pero no modifica archivos.

**El comando que repara es el comando original, y es idempotente.** Cuando un linter detecta un estado desincronizado (por ejemplo, una marca de bitácora sin su fila en la tabla de pendientes), no la repara por su cuenta: nombra como corrección el comando que debió haberse ejecutado originalmente (`tuku todo open`, etc.). Todos los comandos mutadores del CLI son estrictamente idempotentes: ejecutarlos repetidas veces asegura el estado completo sin duplicar líneas en `AHORA.md` ni filas en los derivados.

## La pareja `doctor` / `fix`

`tuku doctor` verifica y `tuku fix TEMA` repara. Se separan por la misma razón que verificar y corregir son operaciones distintas: quien revisa antes de reparar conserva la oportunidad de no hacerlo.

- **`tuku doctor [TEMA]`.** Sin tema revisa todo el vault; con tema, solo esa revisión. Un tema desconocido es error de uso (código 2).
- **Sin `--verbose`, solo lo que hay que leer.** El reporte trae las revisiones con hallazgos y las que dejan un aviso (una pregunta del lint, un vault sembrado con otra versión), más el cierre `doctor: el vault está sano.` o la cuenta de hallazgos. Con `--verbose` (`-v`), todas las revisiones. El código de salida no depende de la opción, y un aviso no hace fallar.
- **`tuku fix TEMA`.** Todo tema tiene su `fix`, y cada hallazgo del tema nombra `tuku fix TEMA` como corrección.
- **Lo determinista se aplica.** Cuando el arreglo no requiere juicio, `fix` lo hace entero: cada cambio queda completo, nunca a medias por archivo.
- **Lo no determinista se devuelve como decisiones, sin escribir.** La salida dice qué hay que decidir, entre qué opciones y qué comando correr una vez decidido. Quien corre TUKU suele ser un agente, y esas decisiones son del autor.
- **Hallazgos mixtos.** `fix` aplica lo determinista, deja intacto lo que requiere decisión y lista esas decisiones.
- **Códigos de salida.** 0 si el tema quedó sano; 1 si quedan decisiones. Es idempotente: una segunda corrida no cambia nada.
- **La fecha de modificación se conserva cuando el cambio es solo de forma.** Convertir `[[x]]` en `[x](ruta)` no es una edición del autor, y esa fecha es la que Obsidian y el sistema de archivos usan para ordenar lo reciente.
- **Cuándo entra un tema nuevo.** Un tema existe cuando tiene un `fix` que hacer. Las demás revisiones de `tuku doctor` salen sin tema y su corrección sigue siendo el comando original o una tarea del autor. Un tema nuevo entra cuando un epic encuentra un caso real que lo pida. Hoy: `link` y `todo`.

## La ayuda explica para qué existe cada comando

Todo sustantivo y todo verbo lleva en `tuku … -h`, antes de las opciones, un párrafo en español (la `description` de argparse). En un comando invocable ese párrafo dice qué archivos del vault lee o escribe y cómo, con precisión suficiente para hacerlo con un editor: es su equivalente manual, el que pide el principio 1, y no va en un campo aparte. Un test recorre el árbol de argparse y exige que ninguno quede sin descripción y que todo comando invocable nombre archivos del vault.

Ese párrafo, el de cada sustantivo con sus verbos anidados debajo, es también el que `tuku init` copia en `reglas/comandos.tuku.md`, para que el vault diga qué hace cada comando aunque `tuku` no esté instalado ([README.md](README.md), "Dónde viven los comandos").

## No entra

- Qué comandos existen y qué hace cada uno. Eso lo especifica la spec de la primitiva que el comando toca: el registro en [bitacora.md](bitacora.md), los pendientes en [pendientes.md](pendientes.md), el ciclo en [ciclo.md](ciclo.md).
- Cómo se instala `tuku` y dónde vive su árbol. Eso es [`../devel/epics.md`](../devel/epics.md), epic 001.
- Cómo un agente decide qué comandos emitir. Eso es [agente.md](agente.md).
