# Arquitectura

> `docs/arquitectura.md` · La forma del sistema. Se apoya en [`brief.md#3-principios`](brief.md#3-principios)
> y precede a `spec/`, que fija los formatos exactos.

---

## 1. Dos artefactos

TUKU se compone de un **motor** y N **perfiles**. Nunca se mezclan.

| | Motor | Perfil |
|---|---|---|
| Qué es | código, janitors, procesos, plantillas | bitácoras, tareas, entidades, notas |
| Dónde vive | site-packages, vía pipx | repositorio Git del usuario |
| Quién lo versiona | PEWMA.AI | el usuario |
| Vida útil | años | décadas |

El motor nunca se copia dentro del perfil. Un motor sirve N perfiles, y el flag
`--profile` existe desde el primer commit: **el diseño local es el diseño del servidor**.
Detalle completo en [`deployment.md`](deployment.md).

---

## 2. Layout del perfil

```
mi-tuku/
├── .tuku/
│   ├── config.yaml          # schema_version, tipos, derivaciones, clasificaciones
│   └── procesos/            # punteros a los procesos del motor instalado
├── AGENTS.md                # instrucciones de agente, anidables por nivel
├── tuku.log                 # log del motor, no versionado
├── entradas/                # canónico inmutable
│   ├── entradas.md          # activo — superficie de escritura sin fecha en el nombre
│   ├── entradas-2026-08.md  # mes cerrado
│   └── 2025/
├── tareas/
│   ├── tareas.md            # único archivo mutable
│   ├── tareas-2026-08.md
│   └── 2025/
├── ciclos/
│   ├── plan_2026-08-10_viaje.md
│   ├── resultados_2026-07-28_turno.md
│   └── 2025/
├── entidades/
│   ├── personal/
│   │   ├── personal.md      # página del ámbito
│   │   └── medico/
│   │       ├── medico.md    # página del subdirectorio
│   │       └── pediatra.md
│   └── trabajo/
│       ├── trabajo.md
│       ├── sw-responsible.md
│       └── analisis-datos/
│           ├── analisis-datos.md
│           └── paper-congreso.md
├── tipos/
│   └── pewma/cliente.md
├── estrategia/
│   ├── cadencias.md
│   └── capacidad.md
└── notas/
    ├── notas.md         # índice derivado
    └── ARCHIVADO/
```

Dos observaciones sobre la forma:

**La jerarquía es sistema → ámbito → niveles libres → entidad.** El ámbito es obligatorio y
es la frontera de confidencialidad y de compartición: `personal/` contiene salud y finanzas
familiares, otro ámbito puede contener datos de clientes. Es el ámbito —no el área— lo que
algún día se federa, lo que se excluye de un export, lo que puede tener convenciones
propias. Entre el ámbito y la entidad, la profundidad es libre: algunas entidades cuelgan
directo del ámbito y otras se agrupan en subdirectorios.

**Cada nivel tiene su página homónima**: `personal/personal.md`, `personal/medico/medico.md`.
Da un lugar natural para describir el nivel, declarar su gobernanza y alojar sus
proyecciones.

**El path no lleva el estado.** El ciclo de vida es `lifecycle: vigente | archivada` en front
matter. Archivar es cambiar una palabra, no mover un archivo: mover rompería enlaces
relativos y ensuciaría el historial con renombres masivos.

**`parent` se deriva del path**, no se declara. Declararlo además sería garantía de
desincronización. El `id` sigue siendo estable e independiente, así que mover una entidad no
rompe referencias.

**El anidamiento de `AGENTS.md` es una razón de diseño, no una comodidad.** Cada nivel puede
acotar el contexto y el comportamiento esperado del agente para lo que cuelga de él.

## 3. Canónico y proyección

**La regla de oro del modelo de datos**: cada dato se escribe una sola vez, en un lugar
canónico. Todo lo demás es proyección recomputable. Nada se copia; todo se proyecta.

**Canónicos** (fuente de verdad, editables):

| Almacén | Naturaleza | Notas |
|---|---|---|
| `entradas/` | inmutable, particionado por mes | una entrada nunca cambia de fecha ni contenido |
| `tareas/tareas.md` | mutable | única verdad del estado de una tarea |
| `ciclos/plan_*` | declaración del ciclo | dónde y cuándo estoy; el conjunto es el calendario |
| Entidades: secciones editables | mutable | descripción, objetivos, recursos |
| `estrategia/` | mutable con gate humano | capacidad y cadencias (P5) |
| `notas/*.md` | mutable | eje deliberativo; a diferencia de una entrada, se corrige editando (`spec/nota.md`) |

**Proyecciones** (derivadas, jamás editadas a mano):

- La bitácora de una entidad y la bitácora de un ciclo son **la misma clase de objeto**:
  proyecciones de `entradas/` con distinto filtro —por pertenencia una, por rango de fechas
  la otra—. Ninguna es un almacén.
- El bloque de tareas del ciclo, en el plan.
- El índice de notas (`notas/notas.md`) y la proyección de notas en la página de su entidad.
- Índices, dashboards, resúmenes anuales.

Esto resuelve el fallo estructural que motivó el rediseño: una tarea no se copia entre
bitácoras, y una entrada no se propaga al área — **se proyecta**.

### 3.1 Marcado de secciones

Una página de entidad es un **compuesto**: mezcla secciones editables y derivadas. Se
marcan con comentarios HTML, invisibles en Obsidian y en cualquier renderizador:

```markdown
<!-- tuku:editable id=descripcion -->
...contenido del usuario...
<!-- /tuku:editable -->

<!-- tuku:derived id=bitacora-entidad hash=a1b2c3 -->
...generado por el motor...
<!-- /tuku:derived -->
```

Toda sección está marcada como una u otra; no hay ambigüedad. El `hash` registra el estado
de las fuentes que la produjeron.

### 3.2 No se hace read-only: se detecta

El usuario escribirá dentro de una zona derivada tarde o temprano, porque Obsidian no lo
impide y porque es lo natural. La respuesta no es bloquear el archivo, sino **detectar la
divergencia**: si el contenido no coincide con el hash registrado, el motor pregunta antes
de sobrescribir. Esto preserva el hábito de edición directa sin romper la coherencia.

### 3.3 Átomos: diferido

Cuando una sección crece demasiado o necesita referenciarse desde varios lugares, podría
promoverse a archivo propio con transclusión desde la entidad. **Se difiere**: introduce un
invariante extra (átomos huérfanos), un mecanismo de transclusión que los tres
renderizadores deben entender, y riesgo de cajón de sastre. El gancho ya está puesto sin
costo: toda sección tiene `id` estable, así que promoverla después no rompe nada.

---

## 4. El grafo de derivaciones

La relación entre canónicos y proyecciones **se declara**, no se programa. En
`.tuku/config.yaml`:

```yaml
derivations:
  - target: "ciclos/plan_{fecha}_{tipo}.md#tareas-del-ciclo"
    sources: ["tareas/tareas.md", "estrategia/cadencias.md"]
    build: "tareas_del_ciclo"

  - target: "entidades/{ruta}/{entidad}.md#bitacora-entidad"
    sources: ["entradas/**/*.md"]
    filter: "entidad == {entidad}"
    build: "proyeccion_entidad"
```

Consecuencias:

- **El grafo debe ser acíclico**, y se valida al arrancar. Es también el control que
  necesitan las cadencias encadenadas (§6).
- **El build corre sobre el diff.** El motor no escanea el repositorio completo: recibe la
  lista de archivos cambiados —de `git diff`, de un watcher, o de una edición del agente— y
  recomputa solo lo alcanzable desde ahí. Un barrido completo queda para el cron nocturno.
- Ningún LLM participa de este lazo.

---

## 5. Coherencia en tres familias

Materialización de P3. Cada familia tiene garante y costo propios:

| Familia | Ejemplos | Garante |
|---|---|---|
| **Invariante** | front matter válido; `id` único; enlaces resuelven; estado de tarea consistente; grafo acíclico; toda sección marcada | janitor |
| **Derivación** | todo derivado existe y su hash de fuentes coincide | janitor de build |
| **Semántica** | la proyección de una entidad se lee bien y preserva sentido; una desviación repetida se reporta | agente |

Los janitors son idempotentes por construcción: correrlos dos veces produce el mismo
resultado, y borrar un derivado no pierde información.

---

## 6. Cadencias

La pieza que hace verdadera la promesa del nombre. Una cadencia es una regla que produce
artefactos en el tiempo — bitácoras, tareas, alertas — y absorbe lo que en otros sistemas
son rituales cableados: abrir y cerrar ciclo son cadencias, editables como cualquier otra.

**Tres orígenes con herencia**, donde lo específico gana sobre lo general y puede silenciar
lo heredado:

```
sistema  →  tipo de entidad  →  entidad concreta
```

**Cuatro formas de disparo:**

| Forma | Se dispara por | Ejemplo |
|---|---|---|
| Absoluta | calendario | el día 1, pagar cuentas |
| Relativa a evento | evento + Δt | venta hoy → contactar en 3 meses |
| Por ausencia | que *no* pasó nada | entidad sin entradas en 4 semanas |
| Por completitud | cierre de una tarea | al cerrar X, activar Y |

**La forma por ausencia necesita silenciador.** Si no distingue entre pausa deliberada,
bloqueo externo y abandono real, produce ruido semanal y el usuario aprende a ignorar el
bloque completo — y ahí muere la confianza en el sistema. Solución: la cadencia dispara
siempre, de forma determinista, y el estado de la entidad la silencia:

```yaml
status: active | paused | blocked_until
```

La inteligencia va en interpretar el silencio, no en decidir si avisar.

**Encadenamientos.** Las formas relativa y por completitud permiten cadenas. El grafo de
derivaciones ya exige aciclicidad; para las cadenas de cadencias aplica el mismo control
más un límite de profundidad por evaluación.

---

## 7. El ciclo y sus artefactos

El ciclo lo define la vida del usuario, no el almanaque: un turno de martes a martes, un
descanso, una semana ISO, un semestre. La cadencia de ciclo lo declara.

| Momento | Artefacto | Dueño |
|---|---|---|
| Apertura | `plan_FECHA_tipo.md` | sembrado, luego del humano |
| Cierre | `resultados_FECHA_tipo.md` | sembrado, luego del humano |

**El plan es la declaración canónica del ciclo**: `cycle_type` (string libre: turno,
descanso, vacaciones, misión), lugar y fechas. El conjunto de archivos `plan_*` **es** el
calendario del usuario, y es contra ese conjunto que se resuelve `(next:turno)`. Romper la
cadencia declarando un ciclo excepcional es el mecanismo normal, no un caso especial.

**No hay archivo de bitácora de ciclo.** Se escribe en `entradas/entradas.md`, el archivo
activo, que rota a `entradas/entradas-YYYY-MM.md` al cerrarse el mes. La apertura no siembra
días: el usuario escribe el día que corresponde cuando tiene algo que registrar, y "los días
de este ciclo" es una proyección bajo demanda (`spec/entradas.md` §2.2). La vista del ciclo se
congela dentro de `resultados_*` al cerrar. Así no queda ninguna zona donde el usuario pueda
escribir sobre una proyección.

**Ciclos de tipos distintos pueden solaparse** —una misión dentro de un turno, un ciclo
mensual de finanzas sobre los turnos— porque las entradas no viven bajo el ciclo: dos ciclos
solapados son dos filtros sobre el mismo conjunto. Solo se prohíbe el solapamiento entre
ciclos del mismo tipo.

**Las clasificaciones abaratan el cierre, pero no lo resuelven.** Cada entrada lleva una
clasificación extensible —`hito`, `decision`, `senal`, `msg`—, de modo que buena parte del
informe parte de un filtro determinista que el agente **redacta**, no de una inferencia que
el agente inventa: Avances ← hitos. Aprendizajes ← decisiones y señales.

**Las desviaciones no salen de un filtro.** No existe clasificación de fricción: nadie rotula
sus propios fracasos mientras trabaja —cero apariciones en el corpus real— y por eso el cierre
las **descubre** contrastando, entidad por entidad, lo esperado de ella contra lo registrado
(`spec/artefactos-ciclo.md` §3.2). Es la parte del cierre que genuinamente requiere juicio, y
la razón por la que el alcance del informe se define por entidad y no por filtro plano.

**El informe es la memoria de largo plazo.** Markdown no es una base de datos: la consulta
histórica se responde por informes, no escaneando el detalle. El crudo se conserva por año
y no se destruye nunca, pero un informe pobre es memoria perdida. Por eso su formato es un
problema de arquitectura.

---

## 8. Ejecución

| Componente | Decisión |
|---|---|
| Almacén | archivos `.md` + Git |
| Janitors | Python 3.14 |
| Motor agéntico (pruebas) | Hermes + modelo económico, invocado por CLI |
| Procesos | Markdown ejecutable por humano o agente medio |
| Scheduler | cron: revisa cadencias vencidas, tareas difusas por reevaluar, encadenamientos |
| Configuración | `.tuku/config.yaml`, uno por perfil |
| `tuku.log` | Log del motor —qué corrió, manual o vía cron—, en la raíz del perfil, **no versionado**. Distinto de `entradas/`, que es del usuario. Si se pierde, no importa: es diagnóstico, no memoria. |

**El scheduler no es opcional.** Sin un lazo periódico, las cadencias solo se evalúan cuando el usuario aparece, y el sistema pierde su carácter proactivo — que es justamente lo que promete el nombre.

**La elección del modelo económico es una prueba de P2**, no una restricción de presupuesto: si un proceso necesita un modelo de frontera para no descarrilar, el proceso está mal escrito.

**Aislamiento de pruebas agénticas:** En la ejecución de tests integrados con Hermes, cada test debe instanciar un perfil de Hermes desde cero (entorno efímero aislado), garantizando que las pruebas sean deterministas y no arrastren contexto previo del asistente.

---

## 9. Versionado del esquema

Los datos sobreviven al motor. El perfil declara `schema_version` en `.tuku/config.yaml`; el motor declara qué rango soporta; `tuku doctor` compara; `tuku migrate` transforma, en un commit propio y aislado para que el usuario revise el diff. Las migraciones se acumulan y ninguna se borra.

---

## 10. Decisiones abiertas

| # | Decisión | De qué depende |
|---|---|---|
| 1 | `effortTime` en tareas y su mecanismo de aprendizaje | Hacer verificable el cruce con capacidad. Se decidirá con experiencia de uso |
| 2 | Cuándo se reevalúa la descripción inferida de una entidad | Frescura del modelo de operación vs. ruido de reescritura |
| 3 | Formato interno del informe de cierre | Es la memoria de largo plazo; debe ser re-consultable por un agente |

---

## 11. Modos de evaluación

Tres formas de obtener información del perfil, con costo y persistencia distintos:

| Modo | Materializa | Cuándo |
|---|---|---|
| **Build** | sí, con hash de fuentes | derivaciones declaradas en el grafo |
| **Invariante** | no, solo valida | janitors de coherencia |
| **Consulta (RADAR)** | no, nunca | bajo demanda, siempre fresca |

**RADAR** es la capa de consulta: revisa tareas trancadas, entidades con actividad anómala, `followup` vencidos, entidades recién desbloqueadas — todo lo que un humano responsable notaría con solo mirar el estado actual, sin que nadie se lo pida. Es determinista: se calcula con Python sobre el estado presente, sin LLM. El agente la invoca en mitad de una conversación, o una GUI la muestra como panel de alertas. No tiene archivo propio ni existe fuera del momento en que se consulta.

Especificación completa diferida a un futuro `spec/agente.md`.
| 4 | Promoción de secciones a átomos | Diferida; el gancho (`id` por sección) ya está |
