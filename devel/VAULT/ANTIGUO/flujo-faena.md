# Simulación 1 (v2) — Ciclo de turno completo

> Reemplaza a la v1. Aplica el changeset de la sesión 2026-08-01: formato posicional de
> tareas, entradas sin siembra de días, marcadores, colector de cadencias, RADAR, alcance
> del cierre por entidad y `outcome`/`followup`/`blockuntil`.
>
> Convención: **▸ INPUT** es lo que la persona dice o escribe. **⚙ TUKU** es lo que hace el
> motor, con referencia a la spec que lo rige. `⚠ GAP` marca lo que la spec aún no cubre.

---

## 0. Estado del perfil antes de empezar

```
entidades/
├── personal/
│   ├── personal.md
│   └── medico/{medico.md, kinesiologo.md}
├── trabajo/
│   ├── trabajo.md
│   ├── jefatura.md                     # área permanente
│   ├── soporte-sw.md                   # área permanente
│   ├── personas/                       # type: employee
│   │   ├── personas.md
│   │   ├── persona1.md
│   │   ├── persona2.md
│   │   ├── persona3.md
│   │   └── persona4.md
│   ├── colaboraciones/{colaboraciones.md, tesis-estudiante.md}
│   └── datos/{datos.md, nucleo-datos.md, fuentes-datos.md}
└── lateral/{lateral.md, metodo.md}
```

`tareas/tareas.md` — 14 tareas abiertas. Extracto:

```markdown
- [ ] 2026-05-13 4h nucleo-datos next:turno - - manual Completar el documento conceptual ^t-2026-0104
      <!-- tuku: cycles=5 -->
- [ ] 2026-05-13 2h colaboraciones next:turno - - manual Enviar correo de postulación conjunta ^t-2026-0087
      <!-- tuku: cycles=6 -->
      > Requiere acuerdo previo sobre autoría y reparto de horas.
- [ ] 2026-05-27 1h personal ~2026-08 - - manual Reembolsos médicos ^t-2026-0142
      <!-- tuku: cycles=4 -->
- [ ] 2026-07-20 1h jefatura 2026-08-11 - - manual Formación administrativa en la sede central ^t-2026-0143
      <!-- tuku: cycles=1 -->
- [ ] 2026-07-06 3h fuentes-datos next:descanso - - manual Prototipo de tablero ^t-2026-0151
      <!-- tuku: cycles=1 -->
```

`entidades/trabajo/colaboraciones/tesis-estudiante.md` → `status: blocked_until: 2026-08-10`.

`.tuku/cache/cadencias-resueltas.yaml` — recién regenerado por el colector, combina sistema +
ámbitos + tipos + entidad, `entidadX.md` con autoridad última (`spec/cadencia.md` §3.1):

```yaml
- id: cad-ciclo-turno
  origen: sistema
  trigger: { type: calendar, rule: "every:14d", from: 2026-03-03 }
  emit: { kind: ciclo, cycle_type: turno, duration: 8d }
- id: cad-pagos-mes
  origen: personal
  trigger: { type: calendar, rule: "monthly:1" }
  emit: { kind: tarea, text: "Realizar pagos mensuales", deadline: "+3d" }
- id: cad-uno-a-uno
  origen: jefatura
  trigger: { type: event, on: uno-a-uno, delta: 3M }
  emit: { kind: tarea, text: "Conversación individual con {entidad}" }
- id: cad-ausencia-trabajo
  origen: trabajo
  trigger: { type: absence, window: 4w }
  emit: { kind: alerta, text: "Sin actividad en más de {window}" }
```

---

## 1. Lunes 3 de agosto — apertura del ciclo

Cron 06:00, sin nadie conectado. `apertura-ciclo`, pasos deterministas
(`spec/artefactos-ciclo.md` §5, ya sin siembra de días):

1. `cad-ciclo-turno` corresponde a 2026-08-04. Idempotencia: sin registro previo de esta
   ocurrencia. Emite ciclo `turno`, 2026-08-04 a 2026-08-11.
2. Incrementa `cycles` de las 14 tareas abiertas. `t-2026-0087` pasa a `cycles=7`.
3. Re-resuelve fechas relativas contra el calendario de planes (`spec/tarea.md` §4.1):

| Tarea | Resuelve a | Vigente este ciclo |
|---|---|---|
| `t-2026-0104` | 2026-08-04 | sí |
| `t-2026-0087` | 2026-08-04 | sí |
| `t-2026-0142` | ventana intersecta | sí |
| `t-2026-0143` | precisa, 08-11 | sí |
| `t-2026-0151` | 2026-08-12 (next:descanso) | no |

**⚙ Paso con agente** — siembra `ciclos/plan_2026-08-04_turno.md`:

```markdown
---
id: plan-2026-08-04-turno
type: plan
cycle_type: turno
place: Sede remota
cycle_start: 2026-08-04
cycle_end: 2026-08-11
status: open
created: 2026-08-03
seeded_by: tuku 0.4.2 / deepseek-v4-flash
---

# Plan del ciclo

## Intención
1. **[jefatura]** — Conversaciones individuales pendientes del trimestre (4 personas).
2. **[soporte-sw]** — Turno operativo los primeros cinco días.
3. **[nucleo-datos]** — Retomar el documento conceptual. *Arrastra 5 ciclos.*
4. **[colaboraciones]** — Enviar el correo de postulación conjunta. *Arrastra 6 ciclos.*
5. **[personal]** — Pagos del mes y reembolsos.

## No entra (y por qué)
- **[lateral/metodo]** — carga operativa alta durante el turno.

## Restricciones y contexto
- Rol operativo del 4 al 8 de agosto.

## Señales a vigilar
- `t-2026-0087` acumula 7 ciclos. Si no cierra este ciclo, corresponde cancelarla o
  redefinirla.
- `tesis-estudiante` sale de `blocked_until` el 10 de agosto.

<!-- tuku:derived id=tareas-del-ciclo hash=3c9f21 -->
- [ ] [Completar el documento conceptual](../tareas/tareas.md#^t-2026-0104) ⟳5
- [ ] [Enviar correo de postulación conjunta](../tareas/tareas.md#^t-2026-0087) ⟳7
- [ ] [Reembolsos médicos](../tareas/tareas.md#^t-2026-0142) ⟳4
- [ ] [Formación administrativa en la sede central](../tareas/tareas.md#^t-2026-0143)
<!-- /tuku:derived -->
```

**▸ INPUT — el usuario corrige el plan por la mañana**

Mueve el punto 3 a "No entra": *"[nucleo-datos] — sin espacio real este turno; requiere
concentración larga."*

**⚙ TUKU** (`spec/artefactos-ciclo.md` §5.3 — resuelto en el momento, no después):

1. Escribe `status: blocked_until: 2026-08-11` en `nucleo-datos.md`
   (`spec/entidad.md` §5, resolución automática desde el plan).
2. Pregunta qué hacer con `t-2026-0104`, vigente de esa entidad. Opción por defecto:
   posponer al próximo `turno`. El usuario acepta con "sí".
3. `t-2026-0104` pasa a `2026-08-04 4h nucleo-datos next:turno - - manual … ⟳5` sin cambiar
   el resto de sus campos — solo se reescribe `deadline`.
4. Registra `<!-- tuku: seed_delta=1_intencion_movida_a_no_entra -->`.

> `nucleo-datos` queda bloqueada y su tarea pospuesta **en el mismo paso**. No hay ventana en
> la que la desviación falsa o la alerta de ausencia puedan aparecer — ambos problemas de la
> v1 (GAP 1 y 2) quedan cerrados por diseño, no por parche posterior.

---

## 2. Martes 4 — primer día

**▸ INPUT (voz, 19:40):** *"Subí hoy. Traspaso con quien sale de turno. Conversación
individual con Persona1, salió bien, quiere moverse a otro subgrupo. Pagué las cuentas del
mes."*

**⚙ TUKU** — entrada en `entradas/entradas.md` (sin encabezados sembrados; el día se escribe
porque hay algo que registrar, no porque el sistema lo anticipó):

```markdown
## 2026-08-04, Martes
- [soporte-sw](../entidades/trabajo/soporte-sw.md) Traspaso con el turno saliente.
- [persona1](../entidades/trabajo/personas/persona1.md) **Hito:** Conversación individual realizada. #uno-a-uno
- [jefatura](../entidades/trabajo/jefatura.md) **Señal:** Persona1 manifiesta interés en cambiar de subgrupo.
```

- El marcador `#uno-a-uno` (`spec/entradas.md` §3.4) es lo que permite a `cad-uno-a-uno`
  reconocer *esta* entrada como el evento que dispara, no cualquier Hito de `persona1`.
- Cascada: nueva tarea `2026-08-04 1h persona1 - 2026-11-04 - cad-uno-a-uno Conversación
  individual con persona1 ^t-2026-0201`. `followup=2026-11-04`: no es un vencimiento, es un
  recordatorio de que corresponde volver a conversar — el RADAR la levantará al acercarse.
- Marca de pago cierra `t-2026-0198`: `- [x] … cad-pagos-mes … ^t-2026-0198`
  `<!-- tuku: outcome=done completed=2026-08-04 -->`.

---

## 3. Miércoles 5 a viernes 7 — densidad operativa

**▸ INPUT (miércoles, escrito directo en Obsidian):**

```markdown
## 2026-08-05, Miércoles
- (09:00) [soporte-sw](…) Emergencia por falla de suministro. Dos horas.
- [soporte-sw](…) **Hito:** Corregido el problema de sincronía en el subsistema principal.
- [persona2](../entidades/trabajo/personas/persona2.md) Conversación individual. #uno-a-uno
- [datos](…) **Decisión:** Avanzar con el prototipo en servidor propio sin esperar a la unidad de sistemas.
```

**⚙ TUKU** — escritura directa en zona canónica, janitors solo validan (E1–E5). Marcador
dispara `t-2026-0202` con `followup=2026-11-05`. Build sobre diff recomputa solo las
proyecciones de `soporte-sw`, `persona2` y `datos`.

**▸ INPUT (jueves, voz):** *"Mandé el correo de la postulación. Por fin."*

**⚙ TUKU**
- Entrada `Hito` en `colaboraciones`.
- Cierra `t-2026-0087`: `[x] … ^t-2026-0087` `<!-- tuku: cycles=7 outcome=done
  completed=2026-08-06 -->`.
- **Curiosidad acotada** (`docs/brief.md` P4, `spec/artefactos-ciclo.md` §3.2): siete
  ciclos de arrastre es una alarma real. El agente pregunta, una sola vez: *"Esta tarea
  llevaba siete ciclos sin cerrarse — ¿qué la destrabó hoy?"*
  **▸ INPUT:** *"Tenía dudas de reparto de horas con el otro equipo, las resolvimos ayer."*
  Se guarda como candidato a Aprendizaje del cierre, con la entidad como origen.

**▸ INPUT (viernes):** *"Terminé el turno operativo. Conversación con Persona3 y con
Persona4."*

**⚙ TUKU** — dos entradas con `#uno-a-uno`, dos tareas `followup` para noviembre
(`t-2026-0203`, `t-2026-0204`).

> **Nota de diseño, no simulada este ciclo**: si en octubre `persona4` se archiva (por
> ejemplo, deja el equipo), `t-2026-0204` —prevista para noviembre— se resuelve automática
> `outcome=expired: la persona de origen ya no está activa` en vez de quedar colgando sin
> explicación (`spec/tarea.md` §7, regla agregada en el changeset).

---

## 4. Sábado 8 y domingo 9 — baja densidad

**▸ INPUT (sábado):** *"Nada de trabajo. Salida con los niños."*

**⚙ TUKU** — entrada sin entidad, `sin-clasificar` (`spec/entradas.md` §3.1). El agente no
pregunta a qué entidad pertenece.

**⚙ TUKU — cron domingo 06:00**

`cad-ausencia-trabajo` evalúa entidades de `trabajo/` con `status: active`:

| Entidad | Última actividad | `status` | ¿Dispara? |
|---|---|---|---|
| `fuentes-datos` | 2026-07-06 | active | **sí** |
| `nucleo-datos` | 2026-07-01 | `blocked_until: 2026-08-11` | **no** — silenciada por el plan |
| `tesis-estudiante` | 2026-07-07 | `blocked_until: 2026-08-10` | **no** |

Alerta materializada solo para `fuentes-datos` en el dashboard de `trabajo/trabajo.md`. La
diferencia con la v1: `nucleo-datos` ya no aparece — el bloqueo automático desde el plan la
silencia sin que nadie lo pida dos veces.

---

## 5. Lunes 10 — desbloqueo, y uso de RADAR

**▸ INPUT (mañana, conversación libre, sin comando explícito):** *"¿cómo vamos?"*

**⚙ TUKU** — el agente invoca **RADAR** (`docs/arquitectura.md` §11): consulta en vivo, sin
archivo propio, sobre el estado presente del perfil.

> *"`tesis-estudiante` salió de su bloqueo ayer — llevaba esperando desde julio. `t-2026-0142`
> (reembolsos) va en cinco ciclos de arrastre. Nada más resalta hoy."*

Esto reemplaza por completo lo que en la v1 era un `⚠ GAP` sin mecanismo: el aviso de
desbloqueo no necesita archivo ni cadencia propia — es una lectura del estado, disponible
apenas se pregunta.

**▸ INPUT:** *"Hablé con el tutor, retomamos. Mando el plan B mañana."*

**⚙ TUKU** — entrada `Hito`, nueva tarea `2026-08-10 1h tesis-estudiante 2026-08-11 - -
manual Enviar plan alternativo por correo ^t-2026-0205`.

---

## 6. Martes 11 — cierre del ciclo

**▸ INPUT:** *"Bajo de turno. Fui a la formación administrativa. Mandé el correo del plan
B."*

**⚙ TUKU** — dos entradas, cierra `t-2026-0143` y `t-2026-0205` con `outcome=done`.

**⚙ TUKU — `cierre-ciclo`**

**Alcance evaluable** (`spec/artefactos-ciclo.md` §3.2): entidades de la Intención
(`jefatura`, `soporte-sw`, `colaboraciones`, `personal`) **∪** entidades con entradas no
planeadas (`datos`, `persona1`–`persona4`, `tesis-estudiante`). **`nucleo-datos` y
`lateral/metodo` quedan fuera**: la primera por bloqueo explícito desde "No entra", la
segunda por no tocada y no declarada.

Para cada entidad del alcance, contraste contra su `alineamiento` y su descripción inferida
— no un filtro plano. Ejemplo del contraste en `colaboraciones`: el `alineamiento` declara
"mantener la colaboración externa activa"; la descripción inferida señala que esta entidad
avanza a saltos, no de forma continua; el cierre de una tarea de siete ciclos encaja con ese
patrón y **no** se lee como anomalía — pero el arrastre mismo sí amerita mención.

```markdown
---
id: res-2026-08-04-turno
type: resultados
cycle_type: turno
cycle_start: 2026-08-04
cycle_end: 2026-08-11
entities: [jefatura, soporte-sw, colaboraciones, datos, tesis-estudiante, personal, persona1, persona2, persona3, persona4]
carryover_alerts: [t-2026-0142]
generated: 2026-08-11T18:20:00-04:00
seeded_by: tuku 0.4.2 / deepseek-v4-flash
---

# Resultados del ciclo

## TL;DR
> Turno de alta carga operativa, compensado con el cierre de las cuatro conversaciones
> individuales del trimestre y el desbloqueo de la colaboración externa tras siete ciclos.

## Avances
- Cuatro conversaciones individuales completadas (persona1–persona4).
- Correo de postulación conjunta enviado — cerraba una tarea de siete ciclos de arrastre.
- Problema de sincronía del subsistema principal corregido.
- Tesis desbloqueada: contacto retomado y plan alternativo enviado.
- Formación administrativa completada. Pagos del mes resueltos.

## Desviaciones
- `[personal]` Reembolsos médicos: quinto ciclo sin cerrarse. ⟳5

## Aprendizajes
- Avanzar con el prototipo en servidor propio sin esperar a la unidad de sistemas evitó
  bloquear la entrega.
- La tarea de postulación conjunta arrastró siete ciclos por una duda de reparto de horas
  con el otro equipo, no por falta de tiempo — resolverla tomó una conversación de un día.
- El interés de Persona1 por cambiar de subgrupo es una señal de que la distribución de
  trabajo entre subgrupos puede estar desbalanceada, no un tema solo individual.

## Momentum y señales
- `[fuentes-datos]` sin actividad en más de cuatro semanas.
- `[nucleo-datos]` permanece bloqueada por decisión propia hasta el cierre de este ciclo.
- La colaboración externa recupera tracción tras el envío del correo.

<!-- tuku:derived id=bitacora-ciclo hash=… -->
…entradas del 2026-08-04 al 2026-08-11, congeladas…
<!-- /tuku:derived -->
```

> El segundo Aprendizaje existe **solo** porque el agente preguntó una vez, en el momento de
> cerrar la tarea, qué la había destrabado. Sin esa pregunta puntual, el cierre habría
> registrado el hito sin la razón — la parte más útil de la retrospectiva se habría perdido.

**Cierre del plan**: `status: closed`. Archivado de tareas cerradas con retención vencida.
`entradas/entradas.md` no rota todavía — sigue dentro de agosto. Janitors, commit
`cierre(2026-08-04): resultados de ciclo turno`.

**▸ INPUT — el usuario corrige el tercer aprendizaje**, lo deja tal cual estaba sembrado.
Sembrado + sin corrección también es una corrección válida: el `seed_delta` de esta sección
queda en cero, y eso también es información sobre qué tan bien calibrado estuvo el agente.

---

## 7. `tuku.log` — extracto del ciclo (no versionado)

```
2026-08-03T06:00:00 cron apertura-ciclo cad-ciclo-turno emitido plan-2026-08-04-turno
2026-08-03T06:00:01 cron apertura-ciclo cycles++ 14 tareas
2026-08-03T09:14:22 manual plan_2026-08-04_turno.md corregido por usuario seed_delta=1
2026-08-06T21:03:10 manual entrada #uno-a-uno detectada → cad-uno-a-uno → t-2026-0201 emitida
2026-08-10T06:00:00 cron cad-ausencia-trabajo evaluado: 1 alerta (fuentes-datos)
2026-08-11T18:20:00 manual cierre-ciclo ejecutado → resultados-2026-08-04-turno.md sembrado
```

---

## 8. Hallazgos frente a la v1

| # | GAP de la v1 | Estado en v2 |
|---|---|---|
| 1 | "No entra" no posterga tareas | **Resuelto** — se resuelve en el momento de corregir el plan (§1) |
| 2 | "No entra" no silencia la ausencia | **Resuelto** — `blocked_until` automático desde el plan (§1, §4) |
| 3 | Personas no eran entidades | **Resuelto** — `type: employee` bajo `trabajo/personas/` |
| 4 | `on:` sin granularidad | **Resuelto** — marcadores inline (§2, §3) |
| 5 | Arrastre alto sin capturar la causa | **Resuelto** — curiosidad acotada en el cierre (§3, §6) |
| 6 | Desbloqueo sin aviso | **Resuelto** — RADAR conversacional (§5) |
| 7 | Días fuera de ciclo | **No aplica** — ya no hay días sembrados que puedan quedar fuera de rango |
| 8 | Entradas sin entidad en fin de semana | Confirmado como comportamiento correcto, sin cambios |

**Lo que queda genuinamente abierto:**
- El límite exacto de "cuántas preguntas de curiosidad por cierre" sigue siendo criterio del
  agente, no una regla numérica — es deliberado (`docs/brief.md` P4), pero conviene
  observar en uso real si el umbral se siente bien calibrado.
- `blocked_until` a nivel de entidad ahora carga dos causas distintas —espera de terceros y
  decisión propia del ciclo— bajo el mismo campo. Sigue siendo una simplificación aceptada,
  no un defecto encontrado en esta simulación.
- No se ejercitó en este ciclo el caso de `outcome=expired` automático (Persona4 / octubre):
  quedó como nota de diseño, no como traza ejecutada, porque excede la ventana de una semana.
  Candidato natural para una segunda simulación que cruce dos ciclos.
