# 005-01 · Las dos semanas de Andrea

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P2 (organización emerge del uso)](../../docs/principios.md#L17), [P6 (conjunto canónico)](../../docs/principios.md#L55), [P7 (carpetas archivan, enlaces conectan)](../../docs/principios.md#L65), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [Triangulación tiempo × compromiso](../../docs/brief.md#L27) · **Spec:** [`spec/ambitos.md`](../../spec/ambitos.md), [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/ciclo.md`](../../spec/ciclo.md), [`spec/bitacora.md`](../../spec/bitacora.md)

Andrea Bustos, dueña de una Pyme de insumos escolares, registra con un comando por hecho las dos semanas del [corpus](../../corpus/referencia/referencia-pyme.md), y la segunda cae sobre una primera que ya está cerrada en `bitacoras/`: el vault deja de estar vacío y cada comando se enfrenta a lo que ya hay.

Los comandos salen de la Parte 2 del corpus (la tabla de verdad), con cuatro ajustes y una adición que dicen cómo se lee esa tabla bajo la spec de hoy:

- Un registro nombra un ámbito y nunca una categoría ni una persona: `clientes` y `proveedores` son categorías (carpetas sin página), así que lo dicho sobre `[[clientes]]` va a `negocio`, y lo dicho sobre una persona de `equipo/` va a `equipo`.
- Un cuerpo no lleva wikilinks: `[[papelera-del-sur]]` se escribe «Papelera del Sur».
- Un `(Hecho)` cierra un pendiente solo si ese pendiente estaba abierto. Los que no (por ejemplo «revisar stock de bodega») son registros normales, con `**progreso**`.
- Un pendiente con día nace `con fecha` (`--due`), y uno que el corpus pospone nace en `próxima semana` (`--horizon`).
- Una adición del escenario: el miércoles 19, Paula Reyes, jefa de UTP de la Escuela Los Maitenes, pide el catálogo. Pone a una segunda Paula en la historia, y el [`005-06`](005-06-el-agente-con-historia.md) la necesita.

## Escenario: el árbol de Andrea nace con su negocio

Dado un directorio vacío
Cuando se siembra el vault y se abren los frentes de la Pyme, con las palabras que los delatan
```bash
tuku init mi-vault --at 2026-08-10 --author "Andrea Bustos"
cd mi-vault
tuku scope create negocio --at "2026-08-10 07:40" --keyword Kelluwün
mkdir ambitos/negocio/clientes ambitos/negocio/proveedores
tuku scope create colegio-los-robles --parent clientes --at "2026-08-10 07:41" --keyword "Los Robles" --keyword Rodolfo --keyword Cifuentes
tuku scope create jardin-semillita --parent clientes --at "2026-08-10 07:42" --keyword Semillita --keyword Marcela --keyword Ossandón
tuku scope create liceo-tecnico-andes --parent clientes --at "2026-08-10 07:43" --keyword "Liceo Andes" --keyword Patricia --keyword Lillo
tuku scope create libreria-el-compas --parent clientes --at "2026-08-10 07:44" --keyword Compás --keyword Óscar --keyword Tapia
tuku scope create escuela-los-maitenes --parent clientes --at "2026-08-10 07:45" --keyword Maitenes --keyword Sonia --keyword Cárdenas --keyword "Paula Reyes"
tuku scope create importadora-andina --parent proveedores --at "2026-08-10 07:46" --keyword Gloria --keyword "Importadora Andina"
tuku scope create papelera-del-sur --parent proveedores --at "2026-08-10 07:47" --keyword Papelera --keyword Iván --keyword Zamora
tuku scope create bodega --parent negocio --at "2026-08-10 07:48" --keyword stock --keyword inventario
tuku scope create temporada-marzo --parent negocio --at "2026-08-10 07:49" --keyword temporada --keyword mercadería
tuku scope create catalogo-marzo --parent negocio --at "2026-08-10 07:50" --keyword catálogo --keyword Paula
tuku scope create canal-feria --parent negocio --at "2026-08-10 07:51" --keyword feria
tuku scope create equipo --parent negocio --at "2026-08-10 07:52" --keyword Katia --keyword Hernán --keyword Ximena --keyword flete
tuku scope create administracion --at "2026-08-10 07:53" --keyword caja --keyword banco --keyword Previred
tuku scope create tributario --parent administracion --at "2026-08-10 07:54" --keyword SII --keyword F29 --keyword IVA --keyword patente
tuku scope create cobranza --parent administracion --at "2026-08-10 07:55" --keyword cobranza --keyword "facturas vencidas"
tuku scope create financiamiento --parent administracion --at "2026-08-10 07:56" --keyword "Felipe Correa" --keyword "línea de capital"
tuku scope update personal --keyword Emilia,Vicente
```
Entonces el negocio y la administración tienen sus ámbitos dentro, y `clientes/` y `proveedores/` son categorías sin página
Y cada ámbito lleva en `keywords` los nombres con que Andrea lo menciona
Y `tuku scope lint` y `tuku doctor` salen limpios
```bash
tuku scope lint
tuku doctor
```

## Escenario: la primera semana se registra día por día

Dado el vault con los frentes abiertos
```bash
cp -r ../el-arbol-de-andrea-nace-con-su/mi-vault .
cd mi-vault
```
Cuando el lunes 10 se registra lo que Andrea contó
```bash
tuku entry create --at "2026-08-10 08:15" --scope bodega --body "**progreso**: revisar stock de bodega"
tuku entry create --at "2026-08-10 08:30" --scope bodega --body "**señal**: quiebre de stock en cuadernos universitarios de cien hojas y témperas de doce colores"
tuku todo open --at "2026-08-10 08:35" --scope negocio --body "pedir cuadernos universitarios y témperas a Papelera del Sur"
tuku entry create --at "2026-08-10 09:40" --scope administracion --body "**progreso**: pagar cotizaciones previsionales de Katia Fuenzalida en Previred"
tuku entry create --at "2026-08-10 10:20" --scope colegio-los-robles --body "**señal**: Rodolfo Cifuentes, administrador de Colegio Los Robles, solicitó cotización de reposición de segundo semestre: 200 cuadernos, 50 resmas y material de arte para cursos menores"
tuku todo open --at "2026-08-10 10:25" --scope colegio-los-robles --body "enviar cotización de reposición de segundo semestre"
tuku entry create --at "2026-08-10 11:50" --scope temporada-marzo --body "**progreso**: consultar a Gloria Pinto de Importadora Andina por plazos de la mercadería de marzo"
tuku entry create --at "2026-08-10 11:55" --scope temporada-marzo --body "**decisión**: Importadora Andina exige confirmación durante agosto; sin confirmar en agosto no hay mercadería importada para marzo"
tuku todo open --at "2026-08-10 17:10" --scope personal --due "2026-08-13 19:00" --body "asistir a reunión de apoderados de Emilia el jueves 13 de agosto a las 19:00"
tuku entry create --at "2026-08-10 21:30" --scope negocio --body "**cadencia**: llamar a los dos días hábiles a todo cliente que no responde una cotización enviada"
```
Y el martes 11
```bash
tuku todo close --at "2026-08-11 09:05" --scope colegio-los-robles --body "enviar cotización de reposición de segundo semestre"
tuku entry create --at "2026-08-11 09:10" --scope colegio-los-robles --body "**progreso**: cotización enviada por $1.800.000 más IVA"
tuku todo close --at "2026-08-11 10:30" --scope negocio --body "pedir cuadernos universitarios y témperas a Papelera del Sur"
tuku entry create --at "2026-08-11 10:35" --scope papelera-del-sur --body "**progreso**: Iván Zamora comprometió despacho para el jueves 13 de agosto"
tuku entry create --at "2026-08-11 12:40" --scope jardin-semillita --body "**hito**: venta despachada a Jardín Semillita: témperas, cartulinas y dos cajas de plasticina"
tuku entry create --at "2026-08-11 12:45" --scope jardin-semillita --body "**nota**: Marcela Ossandón, sostenedora del jardín, solicita boleta y no factura"
tuku entry create --at "2026-08-11 16:20" --scope catalogo-marzo --body "**señal**: Paula Ibáñez, diseñadora freelance, tiene disponibilidad en septiembre para el catálogo de marzo"
tuku todo open --at "2026-08-11 16:25" --scope catalogo-marzo --body "enviar brief y fotografías del catálogo a Paula Ibáñez"
tuku entry create --at "2026-08-11 18:00" --scope liceo-tecnico-andes --body "**señal**: Liceo Técnico Andes sin compras desde abril de 2026, tras haber comprado mensualmente"
```
Y el miércoles 12
```bash
tuku entry create --at "2026-08-12 09:00" --scope tributario --body "**progreso**: enviar facturas y boletas del mes a Ximena Rojas para el F29"
tuku entry create --at "2026-08-12 09:30" --scope tributario --body "**señal**: Ximena Rojas estima IVA a pagar de aproximadamente $180.000 en el F29 de agosto"
tuku entry create --at "2026-08-12 10:15" --scope liceo-tecnico-andes --body "**progreso**: llamar a Patricia Lillo de Liceo Técnico Andes"
tuku entry create --at "2026-08-12 10:20" --scope liceo-tecnico-andes --body "**señal**: Liceo Técnico Andes cambió de proveedor por precio y quedó disconforme con los plazos de entrega del nuevo"
tuku todo open --at "2026-08-12 10:25" --scope liceo-tecnico-andes --body "cotizar de nuevo a Liceo Técnico Andes con precio ajustado"
tuku entry create --at "2026-08-12 11:00" --scope personal --body "**fricción**: Vicente con fiebre en el colegio, retirado a las 11:00; se perdió la jornada de la mañana"
tuku entry create --at "2026-08-12 15:40" --scope financiamiento --body "**progreso**: Felipe Correa del banco solicitó los tres últimos F29 y el balance del año anterior para evaluar la línea de capital de trabajo"
tuku todo open --at "2026-08-12 15:45" --scope financiamiento --body "enviar los tres últimos F29 y el balance al banco"
```
Y el jueves 13
```bash
tuku entry create --at "2026-08-13 09:00" --scope cobranza --body "**progreso**: revisar facturas vencidas de la semana"
tuku entry create --at "2026-08-13 09:15" --scope libreria-el-compas --body "**señal**: factura de $400.000 de Librería El Compás vencida hace veinte días; las otras dos facturas abiertas están dentro de plazo"
tuku entry create --at "2026-08-13 09:20" --scope libreria-el-compas --body "**progreso**: escribir a Óscar Tapia por la factura vencida"
tuku entry create --at "2026-08-13 11:30" --scope papelera-del-sur --body "**fricción**: despacho de Papelera del Sur llegó incompleto: llegaron los cuadernos y no las témperas, comprometidas con Jardín Semillita para la semana siguiente"
tuku todo open --at "2026-08-13 11:35" --scope papelera-del-sur --body "reclamar a Iván Zamora las témperas no despachadas"
tuku todo open --at "2026-08-13 15:00" --scope colegio-los-robles --body "llamar a Colegio Los Robles por la cotización sin respuesta"
tuku todo close --at "2026-08-13 19:00" --scope personal --body "asistir a reunión de apoderados de Emilia el jueves 13 de agosto a las 19:00"
tuku entry create --at "2026-08-13 20:30" --scope personal --body "**señal**: el colegio solicita aporte de $80.000 por alumno para la gira de estudios de Emilia"
```
Y el viernes 14
```bash
tuku todo close --at "2026-08-14 10:20" --scope colegio-los-robles --body "llamar a Colegio Los Robles por la cotización sin respuesta"
tuku entry create --at "2026-08-14 10:25" --scope colegio-los-robles --body "**progreso**: Rodolfo Cifuentes informa que la cotización está en revisión de administración y responden la semana siguiente"
tuku todo close --at "2026-08-14 11:15" --scope papelera-del-sur --body "reclamar a Iván Zamora las témperas no despachadas"
tuku entry create --at "2026-08-14 11:20" --scope papelera-del-sur --body "**progreso**: Papelera del Sur despacha las témperas el lunes 17 de agosto sin costo de flete"
tuku entry create --at "2026-08-14 11:25" --scope papelera-del-sur --body "**fricción**: segundo despacho incompleto de Papelera del Sur en el año"
tuku todo close --at "2026-08-14 16:00" --scope catalogo-marzo --body "enviar brief y fotografías del catálogo a Paula Ibáñez"
tuku todo open --at "2026-08-14 16:05" --scope catalogo-marzo --horizon "próxima semana" --body "fotografiar el mobiliario para el catálogo de marzo"
tuku entry create --at "2026-08-14 17:30" --scope administracion --body "**progreso**: cuadrar caja y conciliar banco de la semana"
tuku entry create --at "2026-08-14 17:40" --scope administracion --body "**progreso**: ventas de la semana por $2.100.000"
```
Y el sábado 15
```bash
tuku entry create --at "2026-08-15 13:45" --scope canal-feria --body "**progreso**: venta de $120.000 en la feria de emprendedores de la plaza"
tuku entry create --at "2026-08-15 14:00" --scope escuela-los-maitenes --body "**señal**: Sonia Cárdenas, de Escuela Rural Los Maitenes, compra por convenio municipal y solicitó cotización de material didáctico; es un canal al que no se había llegado antes"
tuku todo open --at "2026-08-15 14:05" --scope escuela-los-maitenes --body "enviar cotización de material didáctico a Escuela Rural Los Maitenes"
tuku entry create --at "2026-08-15 14:20" --scope temporada-marzo --body "**señal**: demanda repetida de material didáctico Montessori en la feria, línea que hoy no está en catálogo"
tuku entry create --at "2026-08-15 17:00" --scope personal --body "**progreso**: asistir al cumpleaños de la sobrina con los niños"
```
Y el domingo 16
```bash
tuku entry create --at "2026-08-16 20:00" --scope administracion --body "**señal**: cerca de $1.000.000 en facturas por cobrar; la venta crece pero el capital de trabajo está inmovilizado"
tuku entry create --at "2026-08-16 20:15" --scope temporada-marzo --body "**decisión**: confirmar a Importadora Andina la compra de marzo por la mitad del volumen propuesto, para no comprometer el flujo de enero"
tuku todo open --at "2026-08-16 20:20" --scope temporada-marzo --body "confirmar a Gloria Pinto el pedido de marzo por la mitad del volumen"
tuku todo open --at "2026-08-16 20:30" --scope negocio --body "cerrar la cotización de Colegio Los Robles durante la semana del 17 de agosto"
```
Entonces `AHORA.md` tiene los siete días de la semana, y cada hecho está en su día y en orden de hora
Y `PENDIENTES.md` queda con los seis pendientes que la semana no alcanzó a cerrar
Y cada cierre saca su fila y, cuando abría y cerraba el mismo día, también la apertura
Y `tuku doctor` dice que el vault está sano
```bash
tuku doctor
```

## Escenario: la semana se cierra a mano y abre la siguiente

Dado el vault al domingo 16, con la semana escrita
```bash
cp -r ../la-primera-semana-se-registra/mi-vault .
cd mi-vault
```
Cuando se archiva la semana como lo haría Andrea con un editor, y se abre la siguiente
```bash
mkdir bitacoras
sed -e 's/^status: draft/status: stable/' -e 's|](ambitos/|](../ambitos/|g' AHORA.md > bitacoras/bitacora-2026-08-10-2026-08-16.md
rm AHORA.md
tuku cycle open --at 2026-08-17
```
Entonces `bitacoras/bitacora-2026-08-10-2026-08-16.md` tiene los registros de la semana, `status: stable`, y los links de cada ámbito resuelven desde `bitacoras/`
Y `AHORA.md` es la semana del 17 al 23, vacía de registros salvo el pendiente de revisar la bitácora anterior, con vencimiento el lunes 17
Y los seis pendientes de la primera semana siguen en `PENDIENTES.md`, sin duplicarse
Y `tuku doctor` dice que el vault está sano
```bash
tuku doctor
```

## Escenario: la segunda semana cae sobre lo ya escrito

Dado el vault con la primera semana archivada y la segunda abierta
```bash
cp -r ../la-semana-se-cierra-a-mano-y/mi-vault .
cd mi-vault
```
Cuando el lunes 17 se registra lo que Andrea contó
```bash
tuku entry create --at "2026-08-17 08:20" --scope bodega --body "**progreso**: revisar stock de bodega"
tuku entry create --at "2026-08-17 08:25" --scope papelera-del-sur --body "**progreso**: recibir las témperas pendientes de Papelera del Sur"
tuku entry create --at "2026-08-17 08:30" --scope papelera-del-sur --body "**progreso**: témperas recibidas sin costo de flete, según lo comprometido"
tuku entry create --at "2026-08-17 08:35" --scope bodega --body "**señal**: quiebre de stock en cartulina de color y pegamento en barra"
tuku todo close --at "2026-08-17 10:40" --scope escuela-los-maitenes --body "enviar cotización de material didáctico a Escuela Rural Los Maitenes"
tuku entry create --at "2026-08-17 10:50" --scope escuela-los-maitenes --body "**señal**: el convenio municipal paga a sesenta días y no a treinta, plazo que debe conocerse antes de aceptar el pedido"
tuku todo close --at "2026-08-17 11:30" --scope liceo-tecnico-andes --body "cotizar de nuevo a Liceo Técnico Andes con precio ajustado"
tuku entry create --at "2026-08-17 11:35" --scope liceo-tecnico-andes --body "**decisión**: la recotización garantiza entrega en cinco días hábiles, que es donde falló el proveedor competidor"
tuku todo close --at "2026-08-17 15:00" --scope temporada-marzo --body "confirmar a Gloria Pinto el pedido de marzo por la mitad del volumen"
tuku entry create --at "2026-08-17 15:10" --scope temporada-marzo --body "**señal**: Importadora Andina exige 40% de anticipo sobre el pedido de marzo"
```
Y el martes 18
```bash
tuku entry create --at "2026-08-18 09:30" --scope libreria-el-compas --body "**hito**: Librería El Compás pagó la factura vencida de $400.000"
tuku todo open --at "2026-08-18 09:35" --scope libreria-el-compas --body "ofrecer reposición a Librería El Compás"
tuku entry create --at "2026-08-18 11:00" --scope equipo --body "**progreso**: contratar a Katia Fuenzalida por dos días para el inventario de fin de mes"
tuku entry create --at "2026-08-18 12:15" --scope colegio-los-robles --body "**hito**: Colegio Los Robles aprobó la cotización completa por $1.800.000 más IVA"
tuku todo open --at "2026-08-18 12:20" --scope colegio-los-robles --due "2026-08-21" --body "despachar el pedido de Colegio Los Robles el viernes 21 de agosto"
tuku entry create --at "2026-08-18 16:40" --scope administracion --body "**señal**: la municipalidad informa que la patente comercial se renueva en enero y el trámite pasa a ser en línea"
```
Y el miércoles 19
```bash
tuku entry create --at "2026-08-19 09:00" --scope colegio-los-robles --body "**progreso**: pedido de Colegio Los Robles preparado para despacho"
tuku entry create --at "2026-08-19 09:30" --scope equipo --body "**progreso**: contratar flete a Hernán Vidal para el despacho del viernes por $45.000"
tuku entry create --at "2026-08-19 12:00" --scope catalogo-marzo --body "**progreso**: Paula Ibáñez entregó la primera propuesta del catálogo de marzo"
tuku entry create --at "2026-08-19 12:10" --scope catalogo-marzo --body "**fricción**: la propuesta del catálogo trae los precios del año anterior"
tuku todo open --at "2026-08-19 12:15" --scope catalogo-marzo --body "enviar la lista de precios corregida a Paula Ibáñez"
tuku todo close --at "2026-08-19 15:20" --scope financiamiento --body "enviar los tres últimos F29 y el balance al banco"
tuku entry create --at "2026-08-19 15:25" --scope financiamiento --body "**señal**: el banco responde la solicitud de línea de capital de trabajo en diez días hábiles"
tuku todo open --at "2026-08-19 17:00" --scope liceo-tecnico-andes --body "llamar a Liceo Técnico Andes por la cotización sin respuesta"
tuku entry create --at "2026-08-19 17:30" --scope escuela-los-maitenes --body "**señal**: Paula Reyes, jefa de UTP de la Escuela Los Maitenes, pidió ver el catálogo de material didáctico"
```
Y el jueves 20
```bash
tuku entry create --at "2026-08-20 09:00" --scope cobranza --body "**progreso**: revisar facturas vencidas de la semana"
tuku entry create --at "2026-08-20 09:10" --scope cobranza --body "**progreso**: sin facturas vencidas esta semana; dos vencen la semana siguiente"
tuku todo close --at "2026-08-20 10:30" --scope liceo-tecnico-andes --body "llamar a Liceo Técnico Andes por la cotización sin respuesta"
tuku entry create --at "2026-08-20 10:35" --scope liceo-tecnico-andes --body "**progreso**: Patricia Lillo presenta la propuesta al consejo del lunes 24 de agosto"
tuku entry create --at "2026-08-20 14:00" --scope equipo --body "**progreso**: pagar la primera mitad del catálogo a Paula Ibáñez contra boleta de honorarios, con retención"
tuku entry create --at "2026-08-20 18:20" --scope personal --body "**fricción**: el control médico de Vicente del viernes en la mañana coincide con el despacho a Colegio Los Robles"
tuku entry create --at "2026-08-20 18:25" --scope personal --body "**decisión**: la hermana de Andrea lleva a Vicente al control médico del viernes"
```
Y el viernes 21
```bash
tuku todo close --at "2026-08-21 12:30" --scope colegio-los-robles --body "despachar el pedido de Colegio Los Robles el viernes 21 de agosto"
tuku entry create --at "2026-08-21 12:40" --scope colegio-los-robles --body "**hito**: entrega recibida conforme y firmada por Rodolfo Cifuentes"
tuku entry create --at "2026-08-21 12:45" --scope colegio-los-robles --body "**progreso**: factura emitida a treinta días"
tuku entry create --at "2026-08-21 17:30" --scope administracion --body "**progreso**: cuadrar caja y conciliar banco de la semana"
tuku entry create --at "2026-08-21 17:40" --scope administracion --body "**progreso**: ventas de la semana por $3.200.000, la mayor del mes"
tuku entry create --at "2026-08-21 20:00" --scope escuela-los-maitenes --body "**señal**: el pedido de Escuela Los Maitenes a sesenta días compite por el mismo flujo que el anticipo de importación de marzo"
```
Y el sábado 22
```bash
tuku entry create --at "2026-08-22 16:00" --scope personal --body "**progreso**: salir al cine con Emilia y Vicente"
tuku entry create --at "2026-08-22 22:10" --scope temporada-marzo --body "**decisión**: consultar la línea Montessori a Importadora Andina antes de buscar un proveedor nuevo"
tuku todo open --at "2026-08-22 22:15" --scope temporada-marzo --horizon "próxima semana" --body "consultar a Gloria Pinto si Importadora Andina trae línea Montessori"
```
Y el domingo 23
```bash
tuku entry create --at "2026-08-23 19:30" --scope administracion --body "**progreso**: la venta de agosto supera a la del año anterior"
tuku entry create --at "2026-08-23 19:35" --scope administracion --body "**señal**: el anticipo de Importadora Andina deja el flujo ajustado hasta octubre"
tuku entry create --at "2026-08-23 19:50" --scope negocio --body "**aprendizaje**: las dos ventas perdidas del año anterior fueron por no llamar a tiempo; este mes se llamó a los dos días en los tres casos y dos resultaron"
tuku todo open --at "2026-08-23 20:10" --scope bodega --body "realizar el inventario de fin de mes con Katia Fuenzalida"
tuku todo open --at "2026-08-23 20:15" --scope escuela-los-maitenes --body "decidir si se acepta el pedido de Escuela Los Maitenes a sesenta días"
```
Entonces los pendientes de la primera semana que se cumplieron salieron de `PENDIENTES.md` y su cierre quedó en el día en que se dijo
Y la tabla de `PENDIENTES.md` tiene los pendientes que siguen abiertos, cada uno en su horizonte, y ninguno repetido
Y `tuku doctor` dice que el vault está sano
```bash
tuku doctor
```

## Escenario: repetir la segunda semana deja el vault igual

Dado el vault al domingo 23
```bash
cp -r ../la-segunda-semana-cae-sobre-lo/mi-vault .
cd mi-vault
```
Cuando se repite el lunes 17 sin cambiar una palabra
```bash
tuku entry create --at "2026-08-17 08:20" --scope bodega --body "**progreso**: revisar stock de bodega"
tuku entry create --at "2026-08-17 08:25" --scope papelera-del-sur --body "**progreso**: recibir las témperas pendientes de Papelera del Sur"
tuku entry create --at "2026-08-17 08:30" --scope papelera-del-sur --body "**progreso**: témperas recibidas sin costo de flete, según lo comprometido"
tuku entry create --at "2026-08-17 08:35" --scope bodega --body "**señal**: quiebre de stock en cartulina de color y pegamento en barra"
tuku todo close --at "2026-08-17 10:40" --scope escuela-los-maitenes --body "enviar cotización de material didáctico a Escuela Rural Los Maitenes"
tuku entry create --at "2026-08-17 10:50" --scope escuela-los-maitenes --body "**señal**: el convenio municipal paga a sesenta días y no a treinta, plazo que debe conocerse antes de aceptar el pedido"
tuku todo close --at "2026-08-17 11:30" --scope liceo-tecnico-andes --body "cotizar de nuevo a Liceo Técnico Andes con precio ajustado"
tuku entry create --at "2026-08-17 11:35" --scope liceo-tecnico-andes --body "**decisión**: la recotización garantiza entrega en cinco días hábiles, que es donde falló el proveedor competidor"
tuku todo close --at "2026-08-17 15:00" --scope temporada-marzo --body "confirmar a Gloria Pinto el pedido de marzo por la mitad del volumen"
tuku entry create --at "2026-08-17 15:10" --scope temporada-marzo --body "**señal**: Importadora Andina exige 40% de anticipo sobre el pedido de marzo"
```
Y el martes 18
```bash
tuku entry create --at "2026-08-18 09:30" --scope libreria-el-compas --body "**hito**: Librería El Compás pagó la factura vencida de $400.000"
tuku todo open --at "2026-08-18 09:35" --scope libreria-el-compas --body "ofrecer reposición a Librería El Compás"
tuku entry create --at "2026-08-18 11:00" --scope equipo --body "**progreso**: contratar a Katia Fuenzalida por dos días para el inventario de fin de mes"
tuku entry create --at "2026-08-18 12:15" --scope colegio-los-robles --body "**hito**: Colegio Los Robles aprobó la cotización completa por $1.800.000 más IVA"
tuku todo open --at "2026-08-18 12:20" --scope colegio-los-robles --due "2026-08-21" --body "despachar el pedido de Colegio Los Robles el viernes 21 de agosto"
tuku entry create --at "2026-08-18 16:40" --scope administracion --body "**señal**: la municipalidad informa que la patente comercial se renueva en enero y el trámite pasa a ser en línea"
```
Y el miércoles 19
```bash
tuku entry create --at "2026-08-19 09:00" --scope colegio-los-robles --body "**progreso**: pedido de Colegio Los Robles preparado para despacho"
tuku entry create --at "2026-08-19 09:30" --scope equipo --body "**progreso**: contratar flete a Hernán Vidal para el despacho del viernes por $45.000"
tuku entry create --at "2026-08-19 12:00" --scope catalogo-marzo --body "**progreso**: Paula Ibáñez entregó la primera propuesta del catálogo de marzo"
tuku entry create --at "2026-08-19 12:10" --scope catalogo-marzo --body "**fricción**: la propuesta del catálogo trae los precios del año anterior"
tuku todo open --at "2026-08-19 12:15" --scope catalogo-marzo --body "enviar la lista de precios corregida a Paula Ibáñez"
tuku todo close --at "2026-08-19 15:20" --scope financiamiento --body "enviar los tres últimos F29 y el balance al banco"
tuku entry create --at "2026-08-19 15:25" --scope financiamiento --body "**señal**: el banco responde la solicitud de línea de capital de trabajo en diez días hábiles"
tuku todo open --at "2026-08-19 17:00" --scope liceo-tecnico-andes --body "llamar a Liceo Técnico Andes por la cotización sin respuesta"
tuku entry create --at "2026-08-19 17:30" --scope escuela-los-maitenes --body "**señal**: Paula Reyes, jefa de UTP de la Escuela Los Maitenes, pidió ver el catálogo de material didáctico"
```
Y el jueves 20
```bash
tuku entry create --at "2026-08-20 09:00" --scope cobranza --body "**progreso**: revisar facturas vencidas de la semana"
tuku entry create --at "2026-08-20 09:10" --scope cobranza --body "**progreso**: sin facturas vencidas esta semana; dos vencen la semana siguiente"
tuku todo close --at "2026-08-20 10:30" --scope liceo-tecnico-andes --body "llamar a Liceo Técnico Andes por la cotización sin respuesta"
tuku entry create --at "2026-08-20 10:35" --scope liceo-tecnico-andes --body "**progreso**: Patricia Lillo presenta la propuesta al consejo del lunes 24 de agosto"
tuku entry create --at "2026-08-20 14:00" --scope equipo --body "**progreso**: pagar la primera mitad del catálogo a Paula Ibáñez contra boleta de honorarios, con retención"
tuku entry create --at "2026-08-20 18:20" --scope personal --body "**fricción**: el control médico de Vicente del viernes en la mañana coincide con el despacho a Colegio Los Robles"
tuku entry create --at "2026-08-20 18:25" --scope personal --body "**decisión**: la hermana de Andrea lleva a Vicente al control médico del viernes"
```
Y el viernes 21
```bash
tuku todo close --at "2026-08-21 12:30" --scope colegio-los-robles --body "despachar el pedido de Colegio Los Robles el viernes 21 de agosto"
tuku entry create --at "2026-08-21 12:40" --scope colegio-los-robles --body "**hito**: entrega recibida conforme y firmada por Rodolfo Cifuentes"
tuku entry create --at "2026-08-21 12:45" --scope colegio-los-robles --body "**progreso**: factura emitida a treinta días"
tuku entry create --at "2026-08-21 17:30" --scope administracion --body "**progreso**: cuadrar caja y conciliar banco de la semana"
tuku entry create --at "2026-08-21 17:40" --scope administracion --body "**progreso**: ventas de la semana por $3.200.000, la mayor del mes"
tuku entry create --at "2026-08-21 20:00" --scope escuela-los-maitenes --body "**señal**: el pedido de Escuela Los Maitenes a sesenta días compite por el mismo flujo que el anticipo de importación de marzo"
```
Y el sábado 22
```bash
tuku entry create --at "2026-08-22 16:00" --scope personal --body "**progreso**: salir al cine con Emilia y Vicente"
tuku entry create --at "2026-08-22 22:10" --scope temporada-marzo --body "**decisión**: consultar la línea Montessori a Importadora Andina antes de buscar un proveedor nuevo"
tuku todo open --at "2026-08-22 22:15" --scope temporada-marzo --horizon "próxima semana" --body "consultar a Gloria Pinto si Importadora Andina trae línea Montessori"
```
Y el domingo 23
```bash
tuku entry create --at "2026-08-23 19:30" --scope administracion --body "**progreso**: la venta de agosto supera a la del año anterior"
tuku entry create --at "2026-08-23 19:35" --scope administracion --body "**señal**: el anticipo de Importadora Andina deja el flujo ajustado hasta octubre"
tuku entry create --at "2026-08-23 19:50" --scope negocio --body "**aprendizaje**: las dos ventas perdidas del año anterior fueron por no llamar a tiempo; este mes se llamó a los dos días en los tres casos y dos resultaron"
tuku todo open --at "2026-08-23 20:10" --scope bodega --body "realizar el inventario de fin de mes con Katia Fuenzalida"
tuku todo open --at "2026-08-23 20:15" --scope escuela-los-maitenes --body "decidir si se acepta el pedido de Escuela Los Maitenes a sesenta días"
```
Y se regenera lo derivado
```bash
tuku regenerate
```
Entonces el diff del vault es vacío
Y `tuku doctor` dice que el vault está sano
```bash
tuku doctor
```

## Qué se mira a mano

- La bitácora cerrada de la primera semana se lee entera con un editor de texto, y sus links abren las páginas de los ámbitos.
- La página de `colegio-los-robles` cuenta el hilo de la cotización: solicitud, envío, silencio, llamada, aprobación y despacho, en ese orden.
- El lunes 17 muestra el pendiente de revisar la bitácora anterior antes del primer registro.

## Aceptación humana (en Obsidian)

- El árbol de `ambitos/` se ve como el negocio de Andrea: `negocio` con sus clientes y proveedores, `administracion` con tributario, cobranza y financiamiento.
- `PENDIENTES.md` se lee de arriba abajo como la lista de lo que Andrea todavía debe, en el orden en que le conviene mirarlo.
