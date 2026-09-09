# 2. El primer día

> Tu primer día de trabajo dictado al agente. Pasas de una bitácora en blanco a frentes, pendientes, notas y revisión sin tocar la estructura a mano.

Corresponde a lo que entrega el [Epic 003: El día uno, dictado](../../devel/epics.md#epic-003-el-dia-uno-dictado).

---

## El primer registro

> [!tip] Dile a tu agente
> Partí revisando la bodega como todos los lunes.

### Mira `AHORA.md`

¿Bajo qué día quedó? ¿De dónde salió la hora, si no dijiste ninguna?

Ahora pregúntale al agente qué corrió para escribir eso. La respuesta importa: **no editó el archivo a mano**, le pidió al comando `tuku` que lo escribiera. Todo lo que viene después depende de esa diferencia ([principio 4](../principios.md)).

> [!tip] Y una segunda frase
> Estamos abajo en cuadernos universitarios de cien hojas y en témperas de doce colores.

### Mira `AHORA.md` otra vez

Dos líneas, dos horas, el mismo día.

Fíjate en la palabra entre asteriscos de cada una. No es la misma, y ninguna de las dos la dijiste tú. Esa palabra es lo único que tu agente tuvo que decidir; todo el resto de la línea es mecánico.

---

## Lo que queda por hacer

> [!tip] Dile a tu agente
> Me llamó don Rodolfo del Colegio Los Robles, quieren cotización para el segundo semestre: doscientos cuadernos, cincuenta resmas y material de arte. Se la mando mañana.

### Mira `AHORA.md` y después `PENDIENTES.md`

Una sola frase dejó dos líneas en la bitácora: el hecho ocurrido y el compromiso contraído.

Solo una de las dos llegó a `PENDIENTES.md`. Compara el texto de las dos versiones: es idéntico palabra por palabra. Un hecho, un comando: al asentar el registro con su compromiso, la fila en `PENDIENTES.md` se abre sola por [consecuencia](../glosario.md#lo-que-se-escribe).

> [!tip] Ahora prueba esto
> Recuérdame que la Emilia tiene reunión de apoderados el jueves a las siete.

### Mira `AHORA.md`

Busca la palabra "recuérdame". No está. Lo que quedó escrito es el hecho y su compromiso, no la instrucción dirigida al agente.

---

## Lo que ya está hecho

> [!tip] Dile a tu agente
> Ya le mandé la cotización a Los Robles, quedó en un millón ochocientos más IVA.

### Mira `PENDIENTES.md` y `AHORA.md`

En `PENDIENTES.md` la fila desapareció.

En `AHORA.md` quedó la constancia de cierre con `~~(Hecho)~~` y la hora exacta en que lo informaste. El mismo comando que asienta el hecho retira el compromiso de la tabla. Nada desaparece sin dejar constancia en la bitácora.

### Trata de romperlo

> [!tip] Dile a tu agente
> Pagué las cotizaciones de la Katia en Previred, alcancé justo.

Eso está hecho, pero nunca estuvo registrado como pendiente. Mira `PENDIENTES.md`: no apareció ninguna fila nueva ni se alteró ninguna existente. El registro se escribió directo en `AHORA.md`. Un sistema que inventa pendientes ficticios para poder cerrarlos falsea tu propio historial.

---

## Un frente nuevo

Abre `AHORA.md` y mira entre corchetes dobles al inicio de cada línea: todo cayó en `personal`, el único frente que trae un vault recién instalado.

> [!tip] Dile a tu agente
> Colegio Los Robles es un cliente, ábrelo como un frente aparte.

### Mira la carpeta `ambitos/`

Apareció el directorio `ambitos/colegio-los-robles/` con su página `colegio-los-robles.md`, `AGENTS.md` y `CADENCIAS.md`.

### Vuelve a `AHORA.md`

Revisa los registros escritos hace veinte minutos: los que nombraban a Los Robles en texto plano ahora lo enlazan como `[[colegio-los-robles]]`. Las demás líneas quedaron intactas.

Esto ilustra que [la organización emerge del uso](../principios.md): registras primero, ordenas cuando el patrón madura, y el ciclo en curso se actualiza solo.

---

## Algo que no es de hoy

No todo lo que sabes ocurrió a una hora fija de hoy.

> [!tip] Dile a tu agente
> Guárdame una ficha de Los Robles: don Rodolfo Cifuentes es el administrador, compran para el segundo semestre, y les importa más el plazo de entrega que el precio.

### Mira `notas/` y `AHORA.md`

En `notas/` apareció la ficha enlazada al cliente. En `AHORA.md` quedó la constancia temporal de haberla creado hoy.

El día guarda lo que pasó; la nota guarda lo que sabes. Separar ambos ejes ([principio 6](../principios.md)) te permite consultar la ficha en marzo sin tener que releer agosto completo.

---

## Cuando quedó mal dicho

Dictaste rápido y quedó escrito algo que no era. Corregirlo también se dicta.

> [!tip] Dile a tu agente
> La reunión de apoderados de la Emilia no era a las siete, es a las seis y media. Y al frente ponle Liceo Los Robles, que cambiaron de categoría.

Lo que buscas: que el registro **y** el pendiente digan lo mismo. Un registro corregido y una fila sin corregir dejan un pendiente que ya no puedes cerrar, porque cerrarlo es repetir su texto. Por eso corregir es un solo comando y no dos.

Con el [ámbito](../glosario.md#el-árbol-de-ámbitos) pasa lo mismo pero en más sitios: la carpeta, su página y cada mención en tu bitácora. Míralo en `ambitos/` y en `AHORA.md`: no queda ni un `[[colegio-los-robles]]`.

> [!tip] Pídele algo que no tenga comando
> Fusiona Liceo Los Robles y personal en un solo frente.

Eso no lo hace ningún comando, y tu agente puede resolverlo igual, a mano. Lo que debe hacer primero es **decirte en una frase qué entendió** —en tus palabras, no en jerga— y esperar tu confirmación. Si se pone a trabajar sin decirte qué va a hacer, o si contesta con tecnicismos, eso es lo que hay que arreglar.

---

## Revisar con el doctor

Este es el segundo y último comando que corres directamente en tu terminal:

```bash
tuku doctor
```

Lee la salida. Si indica "pregunta" junto a una palabra tuya, no es un error: es un término nuevo que el sistema aceptó y sobre el que te consultará cuando corresponda formalizarlo en el estilo. El vocabulario lo defines tú.

> [!tip] Hazlo enojar
> Abre `PENDIENTES.md` en tu editor y borra manualmente una fila.

Ejecuta de nuevo `tuku doctor`. Detectará de inmediato la inconsistencia cruzando `AHORA.md` con `PENDIENTES.md`. Deshaz el cambio manual antes de seguir.

---

## El día completo

Ahora prueba un dictado continuo, tal como hablarías al final de la jornada:

> [!tip] Dile a tu agente, todo junto
> Hoy es doce, le mandé todas las facturas y boletas del mes a la Ximena Rojas para el F29. Me dijo que este mes sale IVA a pagar, como ciento ochenta mil.
> 
> Llamé a la señora Patricia Lillo del Liceo Andes, que no me compra desde abril. Me contestó de buena: resulta que cambiaron de proveedor por precio pero no quedaron contentos con los plazos. Me pidió que le cotizara de nuevo.
> 
> Fui al banco a ver la línea de capital de trabajo para la compra de marzo. Me atendió Felipe Correa, me pidió los últimos tres F29 y el balance del año pasado.
> 
> Y el Vicente amaneció con fiebre, lo tuve que ir a buscar al colegio a las once. Perdí toda la mañana.

### Mira `AHORA.md` y `PENDIENTES.md`

Las cuatro frases se desglosaron en sus respectivos hechos independientes, asignando ámbitos, horas y compromisos abiertos.

Puedes contrastar el resultado con [`referencia-pyme.md`](../../corpus/referencia/referencia-pyme.md) (Parte 2, miércoles 12), el texto de referencia escrito originalmente a mano.

---

Siguiente: [3. Conversar](03-conversar.md).
