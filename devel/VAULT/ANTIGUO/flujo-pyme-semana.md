# Simulación 2 — Primera semana de una usuaria nueva

> Perfil: `pyme_manager`, dueña de una empresa de insumos escolares en una ciudad
> intermedia. Ficticio, construido sobre la **forma** de un diagnóstico real; ningún dato
> identificable.
>
> **Propósito distinto al de la simulación 1.** Allí se narraba sobre un perfil maduro. Aquí
> el perfil **no existe** al empezar: es la prueba de si TUKU sirve a alguien que nunca vio
> Markdown, y de si el modelo aguanta un dominio ajeno al de su autor **sin tocar `src/`**
> (criterio de éxito 4 del brief).
>
> Convención: **▸ INPUT** / **⚙ TUKU** / `⚠ GAP`.

---

## 0. Punto de partida

Repositorio recién creado con `tuku init`. Contiene:

```
mi-tuku/
├── .tuku/config.yaml          # schema_version, clasificaciones por defecto
├── AGENTS.md
├── entradas/entradas.md       # vacío, solo front matter
├── tareas/tareas.md           # vacío
├── entidades/personal/personal.md
├── estrategia/{cadencias.md, capacidad.md}
└── notas/
```

`estrategia/cadencias.md` trae las cadencias de sistema sembradas
(`spec/cadencia.md` §8): ciclo semanal por defecto, cierre, archivado, ausencia genérica,
arrastre. Nada más. **No hay historia, no hay entidades de negocio, el tesauro vivo está
vacío.**

Lo que la usuaria trae: olvida compromisos y lo sabe; su ventana de atención buena es de
07:00 a 14:00; su operación central es cotizar; su base de clientes vive repartida entre una
planilla, su teléfono y su memoria.

---

## 1. Lunes — el primer día

**⚙ TUKU** — Al abrir, la interfaz muestra los días restantes de la semana y un chat:
*"¿qué quieres registrar hoy?"*. No hay asistente de configuración, no hay que elegir
plantillas, no hay que crear nada primero (`brief` §5.3).

**▸ INPUT (voz, 08:20):** *"Llamé al Colegio San Marcos, quieren cotización de 200 cuadernos
y 50 resmas. Se las mando mañana."*

**⚙ TUKU**
- El tesauro vivo está vacío: "Colegio San Marcos" no resuelve a nada. En vez de fallar o de
  pedirle que configure algo, **propone**:
  > *"No conozco a Colegio San Marcos. ¿Lo doy de alta? Parece un cliente."*
  **▸ INPUT:** *"sí, es un cliente, uno de los grandes"*
- Alta de entidad y **alta del tipo en el mismo movimiento**, porque `cliente` tampoco
  existía (`spec/entidad.md` §1, P6):

```markdown
<!-- entidades/negocio/clientes/colegio-san-marcos.md -->
---
id: colegio-san-marcos
type: cliente
lifecycle: vigente
status: active
alineamiento: Cliente grande y recurrente; sostener el volumen de compra anual.
created: 2026-08-03
modified: 2026-08-03
keywords: [colegio, cuadernos, resmas]
---
```

- **Ámbito resuelto**: El motor pregunta una vez al crear un ámbito nuevo (`negocio/`) y nunca más (`spec/entidad.md` §2.1).
- Entrada canónica:

```markdown
## 2026-08-03, Lunes
- [colegio-san-marcos](../entidades/negocio/clientes/colegio-san-marcos.md) Solicitud de cotización: 200 cuadernos, 50 resmas.
```

- Tarea:
```
- [ ] 2026-08-03 1h colegio-san-marcos 2026-08-04 - - manual Enviar cotización de cuadernos y resmas ^t-2026-0001
```

**▸ INPUT (10:45):** *"El Liceo del Valle no me contesta hace como cuatro meses. Antes compraba todos los meses."*

**⚙ TUKU** — alta de `liceo-del-valle`, y una entrada `Señal`. El agente nota el patrón y propone:
> *"¿Quieres que te avise cuando un cliente lleve mucho tiempo sin actividad? Puedo hacerlo para todos los clientes, no solo para este."*

**▸ INPUT:** *"sí, avísame si pasan dos meses"*

**⚙ TUKU** — escribe la **primera cadencia de tipo** de este perfil, en `tipos/negocio/cliente.md`, dentro del comentario canónico (`spec/cadencia.md` §3.2):

```markdown
<!-- tuku:cadencias
- id: cad-cliente-frio
  descripcion: Avisar cuando un cliente lleva dos meses sin actividad registrada
  trigger: { type: absence, window: 8w }
  emit: { kind: alerta, text: "{entidad} sin actividad hace más de {window}" }
-->
<!-- tuku:derived id=cadencias-legibles hash=… -->
**Cadencias de todo cliente**
- Si pasan más de 8 semanas sin actividad registrada, aparece un aviso.
<!-- /tuku:derived -->
```

> Aquí está la prueba de P6 funcionando: la usuaria no definió un esquema, no eligió un tipo de un catálogo, no abrió una pantalla de configuración. **Dijo una frase.** El tipo `cliente` y su primera regla existen porque el agente los escribió al vuelo.

**▸ INPUT (13:10):** *"Ojo que yo trabajo bien de 7 a 2 de la tarde. Después ando en la calle y no me sirve que me recuerdes cosas."*

**⚙ TUKU** — escribe la franja de notificación `notify_window: "07:00-14:00"` en el front matter de `estrategia/capacidad.md` (`spec/perfil.md` §2.1). Las cadencias que emiten alertas o tareas usan `notify: window` por defecto (`spec/cadencia.md` §5), difiriendo el aviso sin retrasar la emisión de la tarea.

---

## 2. Martes — la cotización como proceso

**▸ INPUT (07:40):** *"Mandé la cotización a San Marcos. Ahora a esperar."*

**⚙ TUKU** — cierra `t-2026-0001` con `outcome=done`. Y la operación de cotizar se reconoce como una **instancia de proceso** (`spec/proceso.md`): no se llena el árbol con entidades efímeras ni se colapsa la cotización en una sola tarea.

La plantilla `procesos/cotizacion.md` se instancia sobre `colegio-san-marcos` emitiendo las tareas correspondientes con `process=cot-0001` y sus dependencias implícitas. El seguimiento lleva `followup="+2d"`.

```markdown
- [ ] 2026-08-04 0.5h colegio-san-marcos - - 2026-08-06 - proc-cotizacion Revisar si respondieron cotización ^t-2026-0004
      <!-- tuku: process=cot-0001 step=seguimiento deps=t-2026-0003 -->
```

El campo `followup` (`spec/tarea.md` §3) marca que es un re-chequeo diferido, no un vencimiento rígido.

**▸ INPUT (11:20):** *"Vendí a Jardín Los Aromos: témperas y cartulinas. Ya despaché."*

**⚙ TUKU** — alta de `jardin-los-aromos`, entrada con marcador:

```markdown
- [jardin-los-aromos](…) **Hito:** Venta despachada: témperas y cartulinas. #venta
```

Y el agente propone la cadencia que es el corazón del negocio:
> *"¿Quieres que te recuerde ofrecerles reposición en unos meses?"*
> **▸ INPUT:** *"sí, a los tres meses, eso es justo lo que se me olvida"*

Se agrega al tipo `cliente` —no a este cliente— porque aplica a todos:

```yaml
- id: cad-reposicion
  descripcion: Ofrecer reposición tres meses después de cada venta
  trigger: { type: event, on: venta, delta: 3M }
  emit: { kind: tarea, text: "Contactar a {entidad} para ofrecer reposición", effort: 0.5h }
```

Dispara de inmediato sobre la entrada recién escrita:

```
- [ ] 2026-08-04 0.5h jardin-los-aromos - 2026-11-04 - cad-reposicion Contactar para ofrecer reposición ^t-2026-0006
```

---

## 3. Miércoles — el problema logístico

**▸ INPUT (09:15):** *"El pedido de resmas del proveedor del norte no llegó. Lo prometieron para hoy. Tengo que entregarle a San Marcos el viernes."*

**⚙ TUKU** — alta de `proveedor-norte` (`type: proveedor`, string libre), entrada, y tarea con `followup`:

```
- [ ] 2026-08-05 0.5h proveedor-norte - 2026-08-06 - manual Confirmar despacho de resmas ^t-2026-0009
```

La fricción no se marca al escribir (`spec/entradas.md` §3.2); el cierre del viernes la descubrirá por contraste de la entidad contra lo esperado (`spec/artefactos-ciclo.md` §3.2).

---

## 4. Jueves y viernes — el viaje como plan anidado

**▸ INPUT (miércoles tarde):** *"El jueves y viernes me voy a la ciudad vecina. Llevo pedidos y aprovecho de visitar clientes."*

**⚙ TUKU** — crea un **plan anidado** (`parent_cycle: plan-2026-08-03-semana`, `spec/artefactos-ciclo.md` §3.6):

```yaml
---
id: plan-2026-08-06-viaje
type: plan
cycle_type: viaje
parent_cycle: plan-2026-08-03-semana
place: Ciudad vecina
cycle_start: 2026-08-06
cycle_end: 2026-08-07
status: open
---
```

Un plan anidado no genera `resultados_*` separado al cerrarse; sus avances y aprendizajes se integran al cierre del ciclo contenedor de la semana.

**▸ INPUT (jueves, voz desde el auto, 18:30):** *"Entregué en el Colegio San Marcos, quedaron conformes. Pasé a ver al Liceo del Valle sin aviso, hablé con la administradora, me dijo que cambiaron de proveedor por precio pero que están abiertos a cotizar de nuevo. Y el proveedor del norte por fin despachó, llega mañana."*

**⚙ TUKU**
- Tres entradas, tres entidades distintas.
- La de `liceo-del-valle` se clasifica `Señal` —información relevante sin acción inmediata— y el agente propone una tarea de cotización.
- Cierra `t-2026-0009` (`proveedor-norte`) con `outcome=done`.
- La entrada de `liceo-del-valle` reinicia su reloj de ausencia: `cad-cliente-frio` ya no disparará.

---

## 5. Viernes — RADAR antes de salir

**▸ INPUT (07:10):** *"¿qué se me está quedando?"*

**⚙ TUKU** — RADAR (`docs/arquitectura.md` §11), consulta en vivo, sin archivo, determinista:

> *"Tres cosas. La cotización de Colegio San Marcos: te avisé de revisarla ayer y sigue sin respuesta suya. El pedido de resmas llega hoy y tienes entrega comprometida hoy mismo — son la misma entrega. Y quedó pendiente cotizarle de nuevo al Liceo del Valle, de la conversación de ayer."*

**▸ INPUT (13:40):** *"Entregado San Marcos. Cerramos la semana."*

---

## 6. Cierre del ciclo `semana`

**Alcance evaluable** (`spec/artefactos-ciclo.md` §3.2): al ser el primer ciclo sin Intención declarada previa, el cierre **omite Desviaciones** y en su lugar propone la Intención del ciclo siguiente a partir de lo observado (`spec/artefactos-ciclo.md` §3.2).

```markdown
---
id: res-2026-08-03-semana
type: resultados
cycle_type: semana
cycle_start: 2026-08-03
cycle_end: 2026-08-07
entities: [colegio-san-marcos, liceo-del-valle, jardin-los-aromos, proveedor-norte]
generated: 2026-08-07T18:00:00-04:00
---

# Resultados del ciclo

## TL;DR
> Primera semana con el sistema. Cuatro relaciones comerciales quedaron registradas, una venta despachada con su seguimiento a tres meses ya programado, y un cliente inactivo reabierto durante el viaje.

## Avances
- Cotización enviada a Colegio San Marcos y entrega cumplida el viernes.
- Venta despachada a Jardín Los Aromos, con contacto de reposición agendado para noviembre.
- Liceo del Valle reabierto: cambió de proveedor por precio, pero acepta cotizar de nuevo.

## Desviaciones
*(No hubo intención declarada esta semana: es el primer ciclo.)*

## Aprendizajes
- El pedido de resmas del proveedor del norte se atrasó dos días y coincidía con una entrega comprometida. La entrega se cumplió, pero sin margen: el atraso de un proveedor se propaga directo a un compromiso con cliente cuando no hay stock propio.
- La visita sin aviso al Liceo del Valle recuperó una relación que llevaba cuatro meses sin movimiento. El motivo de la pérdida fue precio, no servicio.

## Momentum y señales
- Ningún cliente en alerta de inactividad al cierre de la semana.
- La operación de cotizar concentra la mayor parte del tiempo registrado.

## Intención propuesta para el próximo ciclo
1. **[liceo-del-valle]** — Cotizar de nuevo, con revisión de precio.
2. **[proveedor-norte]** — Definir margen de anticipación para pedidos con entrega comprometida.
```

> El Aprendizaje sobre el proveedor no vino de ninguna clasificación. Salió del contraste entre lo esperado y lo registrado. **La fricción no se declara, se descubre.**

---

## 7. Hallazgos resueltos

| # | GAP de la versión original | Resolución en v2 |
|---|---|---|
| 1 | El ámbito se inventó solo | **Resuelto** — El motor pregunta una vez al crear un ámbito nuevo (`spec/entidad.md` §2.1) |
| 2 | `capacidad` sin ventana horaria | **Resuelto** — `notify_window` en `capacidad.md` + `notify: window` en `emit` (`spec/perfil.md` §2, `spec/cadencia.md` §5) |
| 3 | Cotización no es tarea ni entidad | **Resuelto** — Primitiva **Proceso** e instancia de proceso (`spec/proceso.md`) |
| 4 | Fricción no etiquetada | **Confirmado** — Se descubre por contraste de entidad en el cierre (`spec/artefactos-ciclo.md` §3.2) |
| 5 | Ciclos solapados (viaje) | **Resuelto** — Planes anidados (`parent_cycle`) integran su cierre al contenedor (`spec/artefactos-ciclo.md` §3.6) |
| 6 | Primer ciclo sin plan previo | **Resuelto** — Cierre omite Desviaciones y propone Intención inicial (`spec/artefactos-ciclo.md` §3.2) |

**Lo que la simulación confirma:**
- **Un dominio comercial complejo funciona sin tocar `src/`.**
- **El bootstrap es por acumulación natural**, la usuaria nunca ve formularios ni configuraciones.
- **`followup` y RADAR** entregan el máximo valor operativo al rescatar compromisos olvidados en franjas adecuadas.
- **Los hallazgos de la simulación inicial quedan cerrados**: la franja horaria de capacidad y las cotizaciones como instancias de proceso resuelven las brechas del modelo comercial sin agregar desorden.
