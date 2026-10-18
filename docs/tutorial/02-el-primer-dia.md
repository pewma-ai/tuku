# 2. El primer día

> Tu primer día de trabajo dictado al agente. Pasas de una bitácora en blanco a frentes, pendientes, notas y revisión sin tocar la estructura a mano.

---

## El primer registro

> [!tip] Dile a tu agente
> Partí revisando la bodega como todos los lunes.

### Mira `AHORA.md`

¿Bajo qué día quedó? ¿De dónde salió la hora, si no dijiste ninguna?

Pregúntale al agente qué corrió para escribir eso. La respuesta es un comando `tuku`: el agente le pidió el registro al comando y el archivo lo escribió el comando. Todo lo que viene después depende de eso ([principio 4](../principios.md)).

> [!tip] Una segunda frase
> Estamos abajo en cuadernos universitarios de cien hojas y en témperas de doce colores.

### Mira `AHORA.md` otra vez

Hay dos líneas con dos horas, bajo el mismo día.

Cada línea lleva una palabra entre asteriscos. Son distintas y tú no dijiste ninguna. Esa palabra es lo único que tu agente decidió; el resto de la línea lo arma el comando.

---

## Lo que queda por hacer

> [!tip] Dile a tu agente
> Me llamó don Rodolfo del Colegio Los Robles, quieren cotización para el segundo semestre: doscientos cuadernos, cincuenta resmas y material de arte. Se la mando mañana.

### Mira `AHORA.md` y después `PENDIENTES.md`

Una frase dejó dos cosas en `AHORA.md`: el hecho ocurrido y el compromiso contraído.

El compromiso tiene además una fila en `PENDIENTES.md`, con el mismo texto palabra por palabra. La columna `Vence` trae la fecha de mañana, porque dijiste "mañana". Un hecho, un comando: el comando que asienta el registro abre la fila por [consecuencia](../glosario.md#lo-que-se-escribe).

> [!tip] Ahora un pendiente con día y hora
> Recuérdame que la Emilia tiene reunión de apoderados el jueves a las siete.

### Mira `AHORA.md`

Busca la palabra "recuérdame". Falta en el registro: quedó el compromiso, sin la instrucción dirigida al agente. En `PENDIENTES.md`, la columna `Vence` trae el jueves con su hora, y `AHORA.md` lo muestra bajo ese día.

---

## Lo que ya está hecho

> [!tip] Dile a tu agente
> Ya le mandé la cotización a Los Robles, quedó en un millón ochocientos más IVA.

### Mira `PENDIENTES.md` y `AHORA.md`

La fila desapareció de `PENDIENTES.md`.

`AHORA.md` conserva la constancia del cierre, con `(Hecho)` y la hora en que lo informaste. El mismo comando que asienta el hecho retira el compromiso de la tabla, y cada cierre deja su constancia en la bitácora.

### Trata de romperlo

> [!tip] Dile a tu agente
> Pagué las cotizaciones de la Katia en Previred, alcancé justo.

Eso ya está hecho y nunca fue un pendiente. Mira `PENDIENTES.md`: no tiene filas nuevas y las existentes siguen iguales. El registro quedó directo en `AHORA.md`. Inventar pendientes para poder cerrarlos falsearía tu historial.

---

## Un frente nuevo

Abre `AHORA.md` y mira el link al inicio de cada línea, `[personal](ambitos/personal/personal.md)`. Todo cayó en `personal`, el único frente de un vault recién instalado.

> [!tip] Dile a tu agente
> Colegio Los Robles es un cliente, ábrelo como un frente aparte.

### Mira la carpeta `ambitos/`

Apareció `ambitos/colegio-los-robles/` con su página `colegio-los-robles.md`.

Tu agente te preguntó qué palabras, al mencionarlas, indican que algo es de ese frente: «Rodolfo», «Cifuentes», el nombre de un colegio hermano. Respóndele. Quedan en la línea `keywords` de la página, y el capítulo 4 las usa para elegir el frente sin que lo nombres.

### Vuelve a `AHORA.md`

Los registros de esta mañana sobre el colegio ahora empiezan con `[colegio-los-robles](ambitos/colegio-los-robles/colegio-los-robles.md)`: cambiaron de ámbito y el texto quedó como lo dictaste. Si alguno era dudoso, tu agente te preguntó. Abre `colegio-los-robles.md`: ahí está la historia del cliente desde el primer registro.

Así [la organización emerge del uso](../principios.md): registras primero, ordenas cuando el patrón madura, y el ciclo en curso se actualiza solo.

---

## Algo que no es de hoy

Parte de lo que sabes no ocurrió a una hora de hoy.

> [!tip] Dile a tu agente
> Guárdame una ficha de Los Robles: don Rodolfo Cifuentes es el administrador, compran para el segundo semestre, y les importa más el plazo de entrega que el precio.

### Mira `notas/` y `AHORA.md`

En `notas/` apareció la ficha, enlazada al cliente. En `AHORA.md` quedó la constancia de haberla creado hoy.

El día guarda lo que pasó y la nota guarda lo que sabes. Con los dos ejes separados ([principio 6](../principios.md)), consultas la ficha en marzo sin releer agosto completo.

---

## Cuando quedó mal dicho

Dictaste rápido y quedó escrito algo equivocado. Corregirlo también se dicta.

> [!tip] Dile a tu agente
> La reunión de apoderados de la Emilia no era a las siete, es a las seis y media. Y al frente ponle Liceo Los Robles, que cambiaron de categoría.

Comprueba que el registro y el pendiente digan lo mismo. Si uno cambia y el otro no, el pendiente ya no se puede cerrar, porque cerrarlo es repetir su texto. Por eso corregir es un solo comando.

El [ámbito](../glosario.md#el-árbol-de-ámbitos) se corrige en varios sitios: la carpeta, su página y cada mención en tu bitácora. Míralo en `ambitos/` y en `AHORA.md`: ningún link conserva el nombre viejo.

> [!tip] Pídele algo que ningún comando hace
> Fusiona Liceo Los Robles y personal en un solo frente.

Tu agente puede resolverlo a mano. Antes, debe **decirte en una frase qué entendió**, en tus palabras y sin jerga, y esperar tu confirmación. Si empieza a trabajar sin avisar, o contesta con tecnicismos, ahí hay algo que arreglar.

---

## Revisar con el doctor

Es el segundo y último comando que corres tú:

```bash
tuku doctor
```

Muestra los hallazgos y los avisos. Con `tuku doctor --verbose` ves también cada revisión que salió bien. Una salida con "pregunta" junto a una palabra tuya indica un término nuevo que el sistema aceptó. Cuando corresponda, te consultará si lo formalizas en el libro de estilo. El vocabulario lo defines tú.

> [!tip] Hazlo enojar
> Abre `PENDIENTES.md` en tu editor y borra una fila a mano.

Ejecuta `tuku doctor` otra vez. Cruza `AHORA.md` con `PENDIENTES.md` y reporta la inconsistencia. Deshaz el cambio antes de seguir.

---

## El día completo

Dicta ahora seguido, como al final de una jornada:

> [!tip] Dile a tu agente, todo junto
> Le mandé todas las facturas y boletas del mes a la Ximena Rojas para el F29. Me dijo que este mes sale IVA a pagar, como ciento ochenta mil.
>
> Llamé a la señora Patricia Lillo del Liceo Andes, que no me compra desde abril. Me contestó de buena: resulta que cambiaron de proveedor por precio pero no quedaron contentos con los plazos. Me pidió que le cotizara de nuevo.
>
> Fui al banco a ver la línea de capital de trabajo para la compra de marzo. Me atendió Felipe Correa, me pidió los últimos tres F29 y el balance del año pasado.
>
> Y el Vicente amaneció con fiebre, lo tuve que ir a buscar al colegio a las once. Perdí toda la mañana.

### Mira `AHORA.md` y `PENDIENTES.md`

Las cuatro frases se separaron en hechos independientes, cada uno con su ámbito, su hora y, cuando corresponde, su compromiso abierto.

---

Siguiente: [3. Conversar](03-conversar.md).
