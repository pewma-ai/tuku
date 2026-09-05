# Sesiones de ejemplo TUKU — PYME

> Corpus de referencia, ficticio y público. La autora, su familia, sus clientes, proveedores y colaboradores son inventados: no hay correspondencia con ninguna persona o empresa real, ni acá ni en ninguna parte. Cualquier nombre que aparezca acá se trata como el nombre real de este corpus.

> [!note] Para qué sirve este corpus
> Es el par de [`referencia-developer.md`](referencia-developer.md) en un dominio deliberadamente distinto. Allá quien escribe TUKU registra su propio trabajo técnico, con vocabulario que el diseño ya conoce. Acá la usuaria **nunca vio Markdown**, su operación es comercial y su calendario lo fijan terceros: el SII, el banco, los colegios y el año escolar.
>
> Sirve para dos cosas. Probar que el modelo aguanta un dominio ajeno al de su autor sin tocar `src/`, y probar las cadencias, que en un negocio son casi todas de fecha fija impuesta desde afuera, no de ritmo propio.

## La usuaria

**Andrea Bustos**, 43 años, dueña de **Insumos Kelluwün**, una PYME de venta de insumos educacionales en una ciudad intermedia: cuadernos, útiles, material didáctico, mobiliario menor y reposición para colegios, jardines infantiles y librerías revendedoras.

Trabaja sola casi todo el año. Contrata profesionales por encargo cuando el trabajo lo pide: una contadora mensual, una diseñadora freelance para el catálogo, un fletero para las entregas grandes y una asistente de bodega en temporada alta.

Tiene dos hijos, **Emilia** (14) y **Vicente** (9). La operación y la casa comparten calendario y no se separan: es el mismo día.

Su ciclo es **semanal**, de lunes a domingo. No tiene turnos: tiene meses buenos y meses malos, y agosto es el mes en que se decide la temporada de marzo, porque los proveedores importados piden cuatro meses de anticipación.

Lo que trae al sistema: se le olvidan los seguimientos de cotización, que es exactamente donde está su margen; su base de clientes vive repartida entre una planilla, su teléfono y su memoria; y las fechas del SII las cumple siempre a último minuto.

---

# Parte 1: Input en Lenguaje Natural (Sesiones de Dictado)

> Lo que Andrea dicta, tal como lo dice: por voz, entre cosas, sin formato. Es el input crudo del que se debe derivar la Parte 2.

## Semana 1 (10 al 16 de Agosto de 2026)

### Lunes 10 de Agosto

* "Partí revisando la bodega como todos los lunes. Estamos abajo en cuadernos universitarios de cien hojas y en témperas de doce colores, hay que pedir."
* "Pagué las cotizaciones de la Katia en Previred, alcancé justo, hoy es diez."
* "Me llamó el Colegio Los Robles, don Rodolfo Cifuentes, quieren cotización para reposición de segundo semestre: doscientos cuadernos, cincuenta resmas y material de arte para los cursos chicos. Se la mando mañana."
* "Le escribí a la Gloria de Importadora Andina para preguntar por los plazos de la mercadería de marzo. Me dijo que si no le confirmo en agosto, en marzo no hay."
* "La Emilia tiene reunión de apoderados el jueves a las siete."
* "Nota mental que siempre se me olvida: cuando mando una cotización tengo que llamar a los dos días si no me contestan. Ahí es donde pierdo ventas."

---

### Martes 11 de Agosto

* "Mandé la cotización a Los Robles, quedó en un millón ochocientos más IVA."
* "Le hice el pedido a Papelera del Sur, a Iván Zamora: los cuadernos y las témperas. Quedó de despachar el jueves."
* "Vendí y despaché al Jardín Semillita: témperas, cartulinas y dos cajas de plasticina. La señora Marcela Ossandón me pidió boleta, no factura."
* "Me escribió la Paula Ibáñez, la diseñadora, que tiene tiempo en septiembre para el catálogo de marzo. Tengo que pasarle el brief y las fotos."
* "El Liceo Técnico Andes no me compra desde abril. Antes me compraban todos los meses. Algo pasó ahí."

---

### Miércoles 12 de Agosto

* "Hoy es doce, le mandé todas las facturas y boletas del mes a la Ximena Rojas para el F29. Me dijo que este mes sale IVA a pagar, como ciento ochenta mil."
* "Llamé a la señora Patricia Lillo del Liceo Andes. Me contestó de buena, resulta que cambiaron de proveedor por precio pero no quedaron contentos con los plazos de entrega. Me pidió que le cotizara de nuevo."
* "Fui al banco a ver la línea de capital de trabajo para la compra de marzo. Me atendió Felipe Correa, me pidió los últimos tres F29 y el balance del año pasado."
* "Vicente amaneció con fiebre, lo tuve que ir a buscar al colegio a las once. Perdí toda la mañana."

---

### Jueves 13 de Agosto

* "Jueves de cobranza. Tengo tres facturas vencidas: Librería El Compás, cuatrocientos mil, vencida hace veinte días. Le escribí a don Óscar Tapia. Las otras dos están dentro del plazo."
* "Llegó el despacho de Papelera del Sur pero vino incompleto: llegaron los cuadernos y no llegaron las témperas. Y yo tengo comprometidas témperas con el Jardín Semillita para la otra semana."
* "Los Robles no me han contestado la cotización. Van dos días justos."
* "Reunión de apoderados de la Emilia. Piden aporte para la gira de estudios, ochenta mil por alumno."

---

### Viernes 14 de Agosto

* "Viernes de cierre: cuadré la caja y el banco. La semana cerró bien, como dos millones cien en ventas."
* "Llamé a don Rodolfo de Los Robles por la cotización. Me dijo que la están viendo en administración y que me responden la próxima semana. Al menos ya sé que está viva."
* "Le reclamé a Iván Zamora por las témperas. Quedó de despacharlas el lunes sin costo de flete. Anoté que es la segunda vez que me pasa esto con ellos."
* "Le pasé el brief del catálogo a la Paula por WhatsApp, más las fotos que tenía. Faltan las fotos del mobiliario."

---

### Sábado 15 de Agosto

* "Sábado en la feria de emprendedores de la plaza. Vendí poco, como ciento veinte mil, pero conocí a la señora Sonia Cárdenas de la Escuela Rural Los Maitenes, que compra por convenio municipal y nunca había llegado a ellos. Me pidió cotización para material didáctico."
* "Me di cuenta de una cosa en la feria: la gente pregunta por material didáctico Montessori y yo no tengo. Puede ser una línea nueva para marzo."
* "Cumpleaños de la sobrina en la tarde, fuimos con los niños."

---

### Domingo 16 de Agosto

* "Cierre de la semana. Estuve viendo los números: la venta va bien pero la plata está toda en la calle, tengo casi un millón en facturas por cobrar."
* "Decidí que voy a confirmarle a la Gloria de Importadora Andina la compra de marzo, pero la mitad de lo que ella me propuso. No me da el flujo para más y no quiero quedar apretada en enero."
* "La semana que viene tengo que cerrar sí o sí lo de Los Robles y cotizarle a la Escuela Los Maitenes y al Liceo Andes."

---

## Semana 2 (17 al 23 de Agosto de 2026)

### Lunes 17 de Agosto

* "Revisión de bodega del lunes. Llegaron las témperas de Papelera del Sur, sin flete como habíamos quedado. Ahora estoy bajo en cartulina de color y en pegamento en barra."
* "Le mandé la cotización a la Escuela Rural Los Maitenes. Me acordé de preguntar cómo pagan y resulta que por convenio municipal pagan a sesenta días, no a treinta. Eso hay que tenerlo claro antes de aceptar."
* "Cotizé de nuevo al Liceo Técnico Andes, con el precio ajustado y garantizando entrega en cinco días hábiles, que es lo que les falló al otro proveedor."
* "Le confirmé a Gloria Pinto el pedido de marzo: la mitad del volumen que me ofreció. Pide cuarenta por ciento de anticipo."

---

### Martes 18 de Agosto

* "Don Óscar Tapia del Compás me pagó la factura vencida. Cuatrocientos mil. Le agradecí y le ofrecí reposición, quedó de avisarme."
* "Contraté a la Katia Fuenzalida por dos días la próxima semana para el inventario, que lo tengo que hacer antes de fin de mes."
* "Me llegó el correo de la municipalidad: la patente comercial se renueva en enero y este año hay que hacerlo en línea."
* "Salió el pago de Los Robles: aprobaron la cotización completa. Un millón ochocientos más IVA. Tengo que despachar el viernes."

---

### Miércoles 19 de Agosto

* "Preparé el despacho de Los Robles. Contraté a don Hernán Vidal para el flete del viernes, cuarenta y cinco mil."
* "La Paula me mandó la primera propuesta del catálogo. Se ve muy bien pero le puso los precios del año pasado, hay que corregir eso."
* "Le mandé al banco lo que me pidió Felipe Correa: los tres F29 y el balance. Dice que en diez días hábiles tengo respuesta."
* "El Liceo Andes no ha contestado la cotización nueva. Van dos días."

---

### Jueves 20 de Agosto

* "Cobranza del jueves. No tengo vencidas esta semana, la del Compás ya se pagó. Hay dos que vencen la próxima."
* "Llamé al Liceo Andes. La señora Patricia me dijo que la propuesta les gustó y que la van a presentar en el consejo del lunes."
* "Le pagué a la Paula la primera mitad del catálogo, boleta de honorarios, con la retención."
* "Vicente tiene control médico el viernes en la mañana, justo con el despacho. Le voy a pedir a mi hermana que lo lleve."

---

### Viernes 21 de Agosto

* "Se despachó Los Robles con don Hernán. Entregado y recibido conforme, firmó don Rodolfo. Emití la factura a treinta días."
* "Cierre de caja y banco de la semana. Buena semana: tres millones doscientos, la mejor del mes."
* "Me quedó dando vuelta lo de la Escuela Los Maitenes. A sesenta días y con la compra de marzo encima, no sé si me conviene tomarlo completo."

---

### Sábado 22 de Agosto

* "Día familiar. Fuimos al cine con los niños."
* "En la noche estuve pensando en la línea Montessori. Le voy a preguntar a Gloria si la importadora la trae, antes de meterme a buscar otro proveedor."

---

### Domingo 23 de Agosto

* "Cierre de la quincena. La venta de agosto va mejor que el año pasado, pero el anticipo de la importadora me deja el flujo justo hasta octubre."
* "Aprendizaje de estas dos semanas: las dos ventas que se me cayeron el año pasado fueron por no llamar a tiempo. Este mes llamé a los dos días en los tres casos y en dos resultó. Eso ya no lo dejo a la memoria."
* "La próxima semana: inventario con la Katia, respuesta del Liceo Andes el lunes, y decidir lo de Los Maitenes."

---

# Parte 2: Tabla de Verdad (Ground Truth — Formato Bitácora)

> [!tip] Ground Truth para benchmarking de modelos
> Reproduce la entrada canónica que corresponde a cada dictado de la Parte 1, según `spec/bitacora.md`. Permite evaluar si un agente transforma habla desestructurada en entradas que se sostienen solas, con la marca correcta de la ontología cerrada (`**pendiente**`, `~~(Hecho)~~`, `**cadencia**`) y una clasificación abierta razonable.
>
> Tres cosas que este corpus pone a prueba y el de developer no: **la instrucción dirigida al oyente desaparece** ("nota mental que siempre se me olvida" no se registra, la cadencia sí); **el monto y el plazo son parte del hecho**, no adorno, porque de ellos dependen las consecuencias; y **una frase de negocio suele ser dos hechos**, la venta y su condición de pago.

## Semana 1 (10 al 16 de Agosto de 2026)

### Lunes 10 de Agosto
> [!tldr]
> Apertura de semana con revisión de bodega y quiebre de stock en dos productos. Entra solicitud de cotización de Colegio Los Robles por reposición de segundo semestre. Importadora Andina fija agosto como límite para comprometer la temporada de marzo. Se formaliza la cadencia de seguimiento de cotizaciones.

- 08:15 - [[bodega]] ~~(Hecho)~~: revisar stock de bodega
- 08:30 - [[bodega]] **señal**: quiebre de stock en cuadernos universitarios de cien hojas y témperas de doce colores
- 08:35 - [[proveedores]] **pendiente**: pedir cuadernos universitarios y témperas a [[papelera-del-sur]]
- 09:40 - [[administracion]] ~~(Hecho)~~: pagar cotizaciones previsionales de [[katia-fuenzalida]] en Previred
- 10:20 - [[clientes/colegio-los-robles]] **señal**: Rodolfo Cifuentes, administrador de Colegio Los Robles, solicitó cotización de reposición de segundo semestre: 200 cuadernos, 50 resmas y material de arte para cursos menores
- 10:25 - [[clientes/colegio-los-robles]] **pendiente**: enviar cotización de reposición de segundo semestre
- 11:50 - [[temporada-marzo]] ~~(Hecho)~~: consultar a Gloria Pinto de Importadora Andina por plazos de la mercadería de marzo
- 11:55 - [[temporada-marzo]] **decisión**: Importadora Andina exige confirmación durante agosto; sin confirmar en agosto no hay mercadería importada para marzo
- 17:10 - [[personal]] **pendiente**: asistir a reunión de apoderados de Emilia el jueves 13 de agosto a las 19:00
- 21:30 - [[clientes]] **cadencia**: llamar a los dos días hábiles a todo cliente que no responde una cotización enviada

---

### Martes 11 de Agosto
> [!tldr]
> Cotización enviada a Los Robles por $1.800.000 más IVA y pedido de reposición cursado a Papelera del Sur. Venta despachada a Jardín Semillita con boleta. Paula Ibáñez confirma disponibilidad de septiembre para el catálogo de marzo. Se detecta a Liceo Técnico Andes inactivo desde abril.

- 09:05 - [[clientes/colegio-los-robles]] ~~(Hecho)~~: enviar cotización de reposición de segundo semestre
- 09:10 - [[clientes/colegio-los-robles]] **progreso**: cotización enviada por $1.800.000 más IVA
- 10:30 - [[proveedores/papelera-del-sur]] ~~(Hecho)~~: pedir cuadernos universitarios y témperas a [[papelera-del-sur]]
- 10:35 - [[proveedores/papelera-del-sur]] **progreso**: Iván Zamora comprometió despacho para el jueves 13 de agosto
- 12:40 - [[clientes/jardin-semillita]] **hito**: venta despachada a Jardín Semillita: témperas, cartulinas y dos cajas de plasticina
- 12:45 - [[clientes/jardin-semillita]] **nota**: Marcela Ossandón, sostenedora del jardín, solicita boleta y no factura
- 16:20 - [[catalogo-marzo]] **señal**: Paula Ibáñez, diseñadora freelance, tiene disponibilidad en septiembre para el catálogo de marzo
- 16:25 - [[catalogo-marzo]] **pendiente**: enviar brief y fotografías del catálogo a [[paula-ibanez]]
- 18:00 - [[clientes/liceo-tecnico-andes]] **señal**: Liceo Técnico Andes sin compras desde abril de 2026, tras haber comprado mensualmente

---

### Miércoles 12 de Agosto
> [!tldr]
> Cierre tributario del mes enviado a la contadora, con IVA a pagar de $180.000 aproximados. Se recupera el contacto con Liceo Técnico Andes: la pérdida fue por precio, pero el proveedor nuevo les falla en plazos. Iniciado el trámite de línea de capital de trabajo en el banco. Media jornada perdida por enfermedad de Vicente.

- 09:00 - [[administracion/tributario]] ~~(Hecho)~~: enviar facturas y boletas del mes a [[ximena-rojas]] para el F29
- 09:30 - [[administracion/tributario]] **señal**: Ximena Rojas estima IVA a pagar de aproximadamente $180.000 en el F29 de agosto
- 10:15 - [[clientes/liceo-tecnico-andes]] ~~(Hecho)~~: llamar a Patricia Lillo de Liceo Técnico Andes
- 10:20 - [[clientes/liceo-tecnico-andes]] **señal**: Liceo Técnico Andes cambió de proveedor por precio y quedó disconforme con los plazos de entrega del nuevo
- 10:25 - [[clientes/liceo-tecnico-andes]] **pendiente**: cotizar de nuevo a Liceo Técnico Andes con precio ajustado
- 11:00 - [[personal]] **fricción**: Vicente con fiebre en el colegio, retirado a las 11:00; se perdió la jornada de la mañana
- 15:40 - [[administracion/financiamiento]] **progreso**: Felipe Correa del banco solicitó los tres últimos F29 y el balance del año anterior para evaluar la línea de capital de trabajo
- 15:45 - [[administracion/financiamiento]] **pendiente**: enviar los tres últimos F29 y el balance al banco

---

### Jueves 13 de Agosto
> [!tldr]
> Cobranza semanal con una factura vencida hace veinte días en Librería El Compás. Despacho de Papelera del Sur llega incompleto y compromete una entrega ya vendida al Jardín Semillita. Los Robles cumple los dos días sin responder la cotización. Reunión de apoderados con aporte solicitado de $80.000 por la gira de Emilia.

- 09:00 - [[administracion/cobranza]] ~~(Hecho)~~: revisar facturas vencidas de la semana
- 09:15 - [[clientes/libreria-el-compas]] **señal**: factura de $400.000 de Librería El Compás vencida hace veinte días; las otras dos facturas abiertas están dentro de plazo
- 09:20 - [[clientes/libreria-el-compas]] ~~(Hecho)~~: escribir a Óscar Tapia por la factura vencida
- 11:30 - [[proveedores/papelera-del-sur]] **fricción**: despacho de Papelera del Sur llegó incompleto: llegaron los cuadernos y no las témperas, comprometidas con Jardín Semillita para la semana siguiente
- 11:35 - [[proveedores/papelera-del-sur]] **pendiente**: reclamar a Iván Zamora las témperas no despachadas
- 15:00 - [[clientes/colegio-los-robles]] **pendiente**: llamar a Colegio Los Robles por la cotización sin respuesta
- 19:00 - [[personal]] ~~(Hecho)~~: asistir a reunión de apoderados de Emilia el jueves 13 de agosto a las 19:00
- 20:30 - [[personal]] **señal**: el colegio solicita aporte de $80.000 por alumno para la gira de estudios de Emilia

---

### Viernes 14 de Agosto
> [!tldr]
> Cierre de caja y conciliación bancaria con ventas semanales de $2.100.000. La cotización de Los Robles sigue viva, en revisión de administración. Papelera del Sur se compromete a despachar el lunes sin costo de flete, y se registra que es la segunda falla del mismo proveedor.

- 10:20 - [[clientes/colegio-los-robles]] ~~(Hecho)~~: llamar a Colegio Los Robles por la cotización sin respuesta
- 10:25 - [[clientes/colegio-los-robles]] **progreso**: Rodolfo Cifuentes informa que la cotización está en revisión de administración y responden la semana siguiente
- 11:15 - [[proveedores/papelera-del-sur]] ~~(Hecho)~~: reclamar a Iván Zamora las témperas no despachadas
- 11:20 - [[proveedores/papelera-del-sur]] **progreso**: Papelera del Sur despacha las témperas el lunes 17 de agosto sin costo de flete
- 11:25 - [[proveedores/papelera-del-sur]] **fricción**: segundo despacho incompleto de Papelera del Sur en el año
- 16:00 - [[catalogo-marzo]] ~~(Hecho)~~: enviar brief y fotografías del catálogo a [[paula-ibanez]]
- 16:05 - [[catalogo-marzo]] **pendiente**: fotografiar el mobiliario para el catálogo de marzo
- 17:30 - [[administracion]] ~~(Hecho)~~: cuadrar caja y conciliar banco de la semana
- 17:40 - [[administracion]] **progreso**: ventas de la semana por $2.100.000

---

### Sábado 15 de Agosto
> [!tldr]
> Feria de emprendedores con venta baja de $120.000, pero con el contacto de Escuela Rural Los Maitenes, que compra por convenio municipal. Se detecta demanda no cubierta de material didáctico Montessori como posible línea nueva para marzo.

- 13:45 - [[canal-feria]] **progreso**: venta de $120.000 en la feria de emprendedores de la plaza
- 14:00 - [[clientes/escuela-los-maitenes]] **señal**: Sonia Cárdenas, de Escuela Rural Los Maitenes, compra por convenio municipal y solicitó cotización de material didáctico; es un canal al que no se había llegado antes
- 14:05 - [[clientes/escuela-los-maitenes]] **pendiente**: enviar cotización de material didáctico a Escuela Rural Los Maitenes
- 14:20 - [[temporada-marzo]] **señal**: demanda repetida de material didáctico Montessori en la feria, línea que hoy no está en catálogo
- 17:00 - [[personal]] ~~(Hecho)~~: asistir al cumpleaños de la sobrina con los niños

---

### Domingo 16 de Agosto
> [!tldr]
> Cierre de ciclo semanal. La venta acompaña pero el capital de trabajo está inmovilizado en casi $1.000.000 de facturas por cobrar. Se decide comprometer la temporada de marzo por la mitad del volumen ofrecido, priorizando el flujo de enero por sobre el volumen.

- 20:00 - [[administracion]] **señal**: cerca de $1.000.000 en facturas por cobrar; la venta crece pero el capital de trabajo está inmovilizado
- 20:15 - [[temporada-marzo]] **decisión**: confirmar a Importadora Andina la compra de marzo por la mitad del volumen propuesto, para no comprometer el flujo de enero
- 20:20 - [[temporada-marzo]] **pendiente**: confirmar a [[gloria-pinto]] el pedido de marzo por la mitad del volumen
- 20:30 - [[clientes]] **pendiente**: cerrar la cotización de Colegio Los Robles durante la semana del 17 de agosto

---

## Semana 2 (17 al 23 de Agosto de 2026)

### Lunes 17 de Agosto
> [!tldr]
> Papelera del Sur cumple el despacho comprometido sin flete y aparecen dos quiebres nuevos. Cotización enviada a Escuela Los Maitenes, donde se descubre que el convenio municipal paga a sesenta días. Recotización a Liceo Andes atacando el plazo de entrega, que es la falla del competidor. Pedido de marzo confirmado con 40% de anticipo.

- 08:20 - [[bodega]] ~~(Hecho)~~: revisar stock de bodega
- 08:25 - [[proveedores/papelera-del-sur]] ~~(Hecho)~~: recibir las témperas pendientes de Papelera del Sur
- 08:30 - [[proveedores/papelera-del-sur]] **progreso**: témperas recibidas sin costo de flete, según lo comprometido
- 08:35 - [[bodega]] **señal**: quiebre de stock en cartulina de color y pegamento en barra
- 10:40 - [[clientes/escuela-los-maitenes]] ~~(Hecho)~~: enviar cotización de material didáctico a Escuela Rural Los Maitenes
- 10:50 - [[clientes/escuela-los-maitenes]] **señal**: el convenio municipal paga a sesenta días y no a treinta, plazo que debe conocerse antes de aceptar el pedido
- 11:30 - [[clientes/liceo-tecnico-andes]] ~~(Hecho)~~: cotizar de nuevo a Liceo Técnico Andes con precio ajustado
- 11:35 - [[clientes/liceo-tecnico-andes]] **decisión**: la recotización garantiza entrega en cinco días hábiles, que es donde falló el proveedor competidor
- 15:00 - [[temporada-marzo]] ~~(Hecho)~~: confirmar a [[gloria-pinto]] el pedido de marzo por la mitad del volumen
- 15:10 - [[temporada-marzo]] **señal**: Importadora Andina exige 40% de anticipo sobre el pedido de marzo

---

### Martes 18 de Agosto
> [!tldr]
> Se recupera la factura vencida de Librería El Compás. Katia Fuenzalida contratada por dos días para el inventario de fin de mes. Colegio Los Robles aprueba la cotización completa por $1.800.000 más IVA, con despacho comprometido para el viernes. Aviso municipal de renovación de patente en enero, ahora en línea.

- 09:30 - [[clientes/libreria-el-compas]] **hito**: Librería El Compás pagó la factura vencida de $400.000
- 09:35 - [[clientes/libreria-el-compas]] **pendiente**: ofrecer reposición a Librería El Compás
- 11:00 - [[equipo/katia-fuenzalida]] ~~(Hecho)~~: contratar a Katia Fuenzalida por dos días para el inventario de fin de mes
- 12:15 - [[clientes/colegio-los-robles]] **hito**: Colegio Los Robles aprobó la cotización completa por $1.800.000 más IVA
- 12:20 - [[clientes/colegio-los-robles]] **pendiente**: despachar el pedido de Colegio Los Robles el viernes 21 de agosto
- 16:40 - [[administracion]] **señal**: la municipalidad informa que la patente comercial se renueva en enero y el trámite pasa a ser en línea

---

### Miércoles 19 de Agosto
> [!tldr]
> Preparación del despacho de Los Robles con flete contratado a Hernán Vidal por $45.000. Primera propuesta del catálogo recibida, con precios desactualizados. Antecedentes entregados al banco, con diez días hábiles de respuesta. Liceo Andes cumple dos días sin responder.

- 09:00 - [[clientes/colegio-los-robles]] **progreso**: pedido de Colegio Los Robles preparado para despacho
- 09:30 - [[equipo/hernan-vidal]] ~~(Hecho)~~: contratar flete a Hernán Vidal para el despacho del viernes por $45.000
- 12:00 - [[catalogo-marzo]] **progreso**: Paula Ibáñez entregó la primera propuesta del catálogo de marzo
- 12:10 - [[catalogo-marzo]] **fricción**: la propuesta del catálogo trae los precios del año anterior
- 12:15 - [[catalogo-marzo]] **pendiente**: enviar la lista de precios corregida a [[paula-ibanez]]
- 15:20 - [[administracion/financiamiento]] ~~(Hecho)~~: enviar los tres últimos F29 y el balance al banco
- 15:25 - [[administracion/financiamiento]] **señal**: el banco responde la solicitud de línea de capital de trabajo en diez días hábiles
- 17:00 - [[clientes/liceo-tecnico-andes]] **pendiente**: llamar a Liceo Técnico Andes por la cotización sin respuesta

---

### Jueves 20 de Agosto
> [!tldr]
> Cobranza semanal sin facturas vencidas por primera vez en el mes. Liceo Andes lleva la propuesta al consejo del lunes. Pago de la primera mitad del catálogo a Paula Ibáñez con retención de honorarios. Choque de agenda entre el control médico de Vicente y el despacho del viernes, resuelto con apoyo familiar.

- 09:00 - [[administracion/cobranza]] ~~(Hecho)~~: revisar facturas vencidas de la semana
- 09:10 - [[administracion/cobranza]] **progreso**: sin facturas vencidas esta semana; dos vencen la semana siguiente
- 10:30 - [[clientes/liceo-tecnico-andes]] ~~(Hecho)~~: llamar a Liceo Técnico Andes por la cotización sin respuesta
- 10:35 - [[clientes/liceo-tecnico-andes]] **progreso**: Patricia Lillo presenta la propuesta al consejo del lunes 24 de agosto
- 14:00 - [[equipo/paula-ibanez]] ~~(Hecho)~~: pagar la primera mitad del catálogo a Paula Ibáñez contra boleta de honorarios, con retención
- 18:20 - [[personal]] **fricción**: el control médico de Vicente del viernes en la mañana coincide con el despacho a Colegio Los Robles
- 18:25 - [[personal]] **decisión**: la hermana de Andrea lleva a Vicente al control médico del viernes

---

### Viernes 21 de Agosto
> [!tldr]
> Despacho a Colegio Los Robles entregado y recibido conforme, con factura emitida a treinta días. Mejor semana del mes con $3.200.000 en ventas. Queda abierta la duda sobre aceptar el pedido de Los Maitenes a sesenta días con el anticipo de importación encima.

- 12:30 - [[clientes/colegio-los-robles]] ~~(Hecho)~~: despachar el pedido de Colegio Los Robles el viernes 21 de agosto
- 12:40 - [[clientes/colegio-los-robles]] **hito**: entrega recibida conforme y firmada por Rodolfo Cifuentes
- 12:45 - [[clientes/colegio-los-robles]] **progreso**: factura emitida a treinta días
- 17:30 - [[administracion]] ~~(Hecho)~~: cuadrar caja y conciliar banco de la semana
- 17:40 - [[administracion]] **progreso**: ventas de la semana por $3.200.000, la mayor del mes
- 20:00 - [[clientes/escuela-los-maitenes]] **señal**: el pedido de Escuela Los Maitenes a sesenta días compite por el mismo flujo que el anticipo de importación de marzo

---

### Sábado 22 de Agosto
> [!tldr]
> Día familiar. Se decide consultar la línea Montessori al proveedor actual antes de abrir la búsqueda de uno nuevo.

- 16:00 - [[personal]] ~~(Hecho)~~: salir al cine con Emilia y Vicente
- 22:10 - [[temporada-marzo]] **decisión**: consultar la línea Montessori a Importadora Andina antes de buscar un proveedor nuevo
- 22:15 - [[temporada-marzo]] **pendiente**: consultar a [[gloria-pinto]] si Importadora Andina trae línea Montessori

---

### Domingo 23 de Agosto
> [!tldr]
> Cierre del ciclo. Agosto supera al año anterior en venta, pero el anticipo de importación deja el flujo ajustado hasta octubre. Se confirma con datos que el seguimiento a dos días recupera ventas: dos de tres cotizaciones seguidas resultaron.

- 19:30 - [[administracion]] **progreso**: la venta de agosto supera a la del año anterior
- 19:35 - [[administracion]] **señal**: el anticipo de Importadora Andina deja el flujo ajustado hasta octubre
- 19:50 - [[clientes]] **aprendizaje**: las dos ventas perdidas del año anterior fueron por no llamar a tiempo; este mes se llamó a los dos días en los tres casos y dos resultaron
- 20:10 - [[bodega]] **pendiente**: realizar el inventario de fin de mes con [[katia-fuenzalida]]
- 20:15 - [[clientes/escuela-los-maitenes]] **pendiente**: decidir si se acepta el pedido de Escuela Los Maitenes a sesenta días

---

# Parte 3: Estado Reconstruible del Repositorio

> [!abstract] Especificación de Estado Objetivo
> El estado documental y relacional que un sistema agéntico debe poder inferir, actualizar o reconstruir a partir de los inputs anteriores. A diferencia del corpus de developer, acá el árbol se escribe con la estructura de `spec/ambitos.md`: `ambitos/` con `AGENTS.md` y `CADENCIAS.md` obligatorios en cada directorio.

## 1. Árbol de ámbitos

```
ambitos/
├── AGENTS.md
├── CADENCIAS.md
├── negocio/
│   ├── negocio.md
│   ├── AGENTS.md
│   ├── CADENCIAS.md
│   ├── clientes/
│   │   ├── AGENTS.md
│   │   ├── CADENCIAS.md              <- cadencias de todo cliente
│   │   ├── colegio-los-robles.md
│   │   ├── jardin-semillita.md
│   │   ├── liceo-tecnico-andes.md
│   │   ├── libreria-el-compas.md
│   │   └── escuela-los-maitenes.md
│   ├── proveedores/
│   │   ├── AGENTS.md
│   │   ├── CADENCIAS.md
│   │   ├── importadora-andina.md
│   │   ├── papelera-del-sur.md
│   │   └── distribuidora-kimun.md
│   ├── bodega/
│   │   ├── bodega.md
│   │   ├── AGENTS.md
│   │   └── CADENCIAS.md              <- stock mínimo, inventario trimestral
│   ├── temporada-marzo/
│   │   ├── temporada-marzo.md
│   │   ├── AGENTS.md
│   │   └── CADENCIAS.md
│   ├── catalogo-marzo/
│   ├── canal-feria/
│   └── equipo/
│       ├── equipo.md                 <- profesionales contratados por encargo
│       ├── AGENTS.md
│       ├── CADENCIAS.md
│       ├── ximena-rojas.md
│       ├── paula-ibanez.md
│       ├── hernan-vidal.md
│       └── katia-fuenzalida.md
├── administracion/
│   ├── administracion.md
│   ├── AGENTS.md
│   ├── CADENCIAS.md                  <- caja, conciliación
│   ├── tributario/                   <- F29, patente, honorarios
│   ├── cobranza/
│   └── financiamiento/
└── personal/
    ├── personal.md
    ├── AGENTS.md
    └── CADENCIAS.md
```

`equipo/` es un ámbito y no una categoría: tiene página propia porque Andrea razona sobre "los que me ayudan" como un conjunto, aunque cada uno entre y salga por encargo.

## 2. Inventario de pendientes al 23 de agosto

Por horizonte, según la escalera de `spec/pendientes.md`.

Los nombres de los horizontes son **vocabulario abierto**: salen de `### Horizontes` en el libro de estilo del autor, no de TUKU. Andrea no tiene turnos, tiene semanas, así que sus horizontes son `^esta-semana` y `^proxima-semana` donde el corpus de developer dice `^este-turno` y `^proximo-turno`. La escalera es la misma y el janitor no cambia: lo que cambia es cómo se llama cada escalón.

* **Cerrados durante las dos semanas:**
  - `administracion`: pagar cotizaciones previsionales de Katia Fuenzalida en Previred.
  - `clientes/colegio-los-robles`: enviar cotización, llamar por la cotización sin respuesta, despachar el pedido.
  - `proveedores/papelera-del-sur`: pedir cuadernos y témperas, reclamar las témperas no despachadas.
  - `clientes/liceo-tecnico-andes`: cotizar de nuevo con precio ajustado, llamar por la cotización sin respuesta.
  - `clientes/escuela-los-maitenes`: enviar cotización de material didáctico.
  - `administracion/tributario`: enviar facturas y boletas del mes a Ximena Rojas para el F29.
  - `administracion/financiamiento`: enviar los tres últimos F29 y el balance al banco.
  - `catalogo-marzo`: enviar brief y fotografías a Paula Ibáñez.
  - `temporada-marzo`: confirmar a Gloria Pinto el pedido de marzo por la mitad del volumen.
  - `equipo`: contratar a Katia Fuenzalida para el inventario, contratar flete a Hernán Vidal, pagar la primera mitad del catálogo.
  - `personal`: asistir a reunión de apoderados de Emilia.

* **`^esta-semana` (semana del 24 de agosto):**
  - `bodega`: realizar el inventario de fin de mes con Katia Fuenzalida.
  - `clientes/escuela-los-maitenes`: decidir si se acepta el pedido a sesenta días.
  - `catalogo-marzo`: enviar la lista de precios corregida a Paula Ibáñez.
  - `clientes/libreria-el-compas`: ofrecer reposición a Librería El Compás.
  - `bodega`: pedir cartulina de color y pegamento en barra.

* **`^proxima-semana`:**
  - `temporada-marzo`: consultar a Gloria Pinto si Importadora Andina trae línea Montessori.
  - `catalogo-marzo`: fotografiar el mobiliario para el catálogo.
  - `administracion/financiamiento`: seguimiento de la respuesta del banco (vence el 2 de septiembre).

* **`^fin-de-mes`:**
  - `administracion/tributario`: pagar el F29 de agosto.
  - `personal`: responder por el aporte de $80.000 de la gira de estudios de Emilia.

* **`^sin-fecha`:**
  - `temporada-marzo`: evaluar la línea Montessori como producto nuevo.
  - `administracion/tributario`: renovar la patente comercial en enero, ahora en línea.
  - `proveedores/papelera-del-sur`: evaluar proveedor alternativo tras dos despachos incompletos.

## 3. Personas enlazadas (notas tipadas en `notas/`)

Con sus siglas de tres letras, formadas por la inicial del nombre y las dos primeras letras del apellido.

* **Clientes:**
  - `Rodolfo Cifuentes` (RCI) — Administrador de Colegio Los Robles; decide compras de reposición y firma recepciones.
  - `Marcela Ossandón` (MOS) — Sostenedora de Jardín Semillita; compra con boleta, no factura.
  - `Patricia Lillo` (PLI) — Encargada de adquisiciones de Liceo Técnico Andes; compra pasa por consejo.
  - `Óscar Tapia` (OTA) — Dueño de Librería El Compás; revendedor, paga tarde pero paga.
  - `Sonia Cárdenas` (SCA) — Escuela Rural Los Maitenes; compra por convenio municipal a sesenta días.

* **Proveedores y banca:**
  - `Gloria Pinto` (GPI) — Ejecutiva de Importadora Andina; controla el calendario de importación de la temporada de marzo.
  - `Iván Zamora` (IZA) — Contacto en Papelera del Sur; dos despachos incompletos en el año.
  - `Felipe Correa` (FCO) — Ejecutivo del banco; evalúa la línea de capital de trabajo.

* **Equipo por encargo:**
  - `Ximena Rojas` (XRO) — Contadora externa; F29 mensual, honorarios y balance.
  - `Paula Ibáñez` (PIB) — Diseñadora freelance; catálogo de temporada, pago contra boleta de honorarios con retención.
  - `Hernán Vidal` (HVI) — Fletero; despachos grandes, cobra por viaje.
  - `Katia Fuenzalida` (KFU) — Asistente de bodega en temporada e inventarios; con cotizaciones previsionales a cargo de Andrea.

* **Familia:**
  - `Emilia` — Hija, 14 años; colegio con gira de estudios en curso.
  - `Vicente` — Hijo, 9 años; controles médicos que suelen chocar con la operación.

## 4. Notas conceptuales y documentos (`notas/`)

* **Operación comercial:**
  - `Cómo cotizo` — Estructura de una cotización, márgenes por línea y condiciones de pago por tipo de cliente.
  - `Condiciones de pago por canal` — Colegio particular a treinta días, convenio municipal a sesenta, revendedor contra entrega, feria al contado.
  - `Proveedores y sus plazos reales` — Plazo prometido contra plazo cumplido, con el historial de fallas.
* **Temporada y financiamiento:**
  - `Temporada de marzo 2027` — Proyección de volumen, calendario de importación y punto de no retorno de agosto.
  - `Flujo de caja agosto-diciembre 2026` — Cruce del anticipo de importación con la cobranza esperada.
  - `Línea de capital de trabajo — antecedentes al banco` — Qué pidió el banco y cuándo se entregó.
* **Personal y del sistema:**
  - `Calendario escolar de Emilia y Vicente` — Fechas del colegio que compiten con la operación.
  - `Perfil de Andrea` — Ventana de atención productiva (07:00 a 14:00), cómo decide y qué delega.

## 5. Cadencias vigentes

Cada una vive en el `CADENCIAS.md` del ámbito donde aplica, según `spec/cadencias.md`. Casi todas tienen fecha impuesta desde afuera, que es la diferencia central con el corpus de developer, donde el ritmo lo pone quien escribe.

| Cadencia | Ámbito | Cuándo | Emite |
| --- | --- | --- | --- |
| Revisión de stock mínimo | `negocio/bodega` | Lunes, semanal | Pendiente de pedido por producto bajo mínimo |
| Cobranza de facturas vencidas | `administracion/cobranza` | Jueves, semanal | Pendiente por cada factura vencida |
| Cierre de caja y conciliación bancaria | `administracion` | Viernes, semanal | Pendiente con fecha |
| Cierre de ciclo semanal | `ambitos/` (raíz) | Domingo, semanal | Pendiente de cierre |
| Cotizaciones previsionales | `administracion` | Día 10, mensual | Pendiente con fecha |
| Declaración y pago del F29 | `administracion/tributario` | Día 12, mensual | Pendiente con fecha |
| Seguimiento de cotización enviada | `negocio/clientes` | Dos días hábiles tras enviar una cotización | Pendiente de llamada |
| Oferta de reposición | `negocio/clientes` | Tres meses después de una venta despachada | Pendiente de contacto |
| Cliente sin actividad | `negocio/clientes` | Ocho semanas sin actividad registrada | Pendiente de contacto |
| Inventario de bodega | `negocio/bodega` | Último fin de mes de cada trimestre | Pendiente con fecha |
| Confirmación de temporada | `negocio/temporada-marzo` | Agosto, anual | Pendiente con fecha, punto de no retorno |
| Renovación de patente comercial | `administracion/tributario` | Enero, anual | Pendiente con fecha |

> [!warning] Lo que este corpus pone a prueba en las cadencias
> **Dos son de evento y no de calendario** (seguimiento a dos días, reposición a tres meses) y una es de **ausencia** (ocho semanas sin actividad). Las tres nacieron acá de una frase de Andrea, no de una configuración, y las tres viven en el ámbito `clientes/` y no en cada cliente, porque aplican a todos.
>
> La de seguimiento a dos días es además la única que se puede **medir**: la entrada del domingo 23 dice que de tres cotizaciones seguidas, dos resultaron. Es el caso de prueba de si el sistema puede mostrarle a alguien que una regla suya sirve.

## 6. Procesos típicos que las entradas dejan ver

No son primitivas de `spec/`: son la forma que toma el trabajo real y que las entradas deberían permitir reconstruir.

1. **Cotización.** Solicitud → cotización enviada → seguimiento a dos días → aprobación → despacho → factura a plazo → cobranza. Es donde está el margen y donde Andrea pierde ventas: cuatro instancias en estas dos semanas, en cuatro estados distintos a la vez.
2. **Reposición de stock.** Quiebre detectado el lunes → pedido al proveedor → recepción → verificación contra lo pedido. Falla dos veces con el mismo proveedor, y la segunda falla es la que convierte un problema en un patrón.
3. **Cierre tributario mensual.** Facturas y boletas del mes → contadora → F29 el día 12 → pago. Fecha impuesta, sin margen de negociación.
4. **Encargo a profesional externo.** Disponibilidad → brief → entrega → corrección → boleta de honorarios con retención → pago. Aplica igual a la diseñadora, al fletero y a la asistente de bodega, con distinto tamaño.
5. **Temporada de marzo.** Es el proceso más largo y el más caro de equivocar: se decide en agosto, se paga el anticipo en agosto, la mercadería llega en diciembre y se vende en marzo. Compite por el mismo flujo de caja que la operación corriente, y esa competencia aparece explícita en las entradas del 21 y 23 de agosto.
