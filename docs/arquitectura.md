# Arquitectura

> `docs/arquitectura.md` · La forma del sistema. Se apoya en [`principios.md`](principios.md)
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
│   ├── config.yaml          # schema_version, ciclo, tipos, derivaciones, clasificaciones
│   └── procesos/            # punteros a los procesos del motor instalado
├── AGENTS.md                # instrucciones de agente, anidables por nivel
├── ciclos/
│   ├── plan_2026-08-04_turno.md
│   ├── bitacora_2026-08-04_turno.md
│   └── resultados_2026-07-28_turno.md
├── entidades/
│   ├── VIGENTES/
│   └── ARCHIVADAS/
├── tareas/
│   ├── abiertas.md          # mutable
│   └── tareas-2026.md       # completadas del año, inmutable
├── estrategia/
│   ├── cadencias.md
│   └── capacidad.md
└── notas/
```

Dos observaciones sobre la forma:

**La jerarquía POSIX no es solo organización.** Permite anidar instrucciones de agente:
un `AGENTS.md` por nivel acota el contexto y el comportamiento esperado según dónde se
esté trabajando. Es una razón de diseño, no una comodidad.

**`entidades/` se divide por ciclo de vida, no por tipo.** `VIGENTES` y `ARCHIVADAS` son
estados; el tipo va en el front matter (P6). Archivar es mover un archivo, no reclasificar.

---

## 3. Canónico y proyección

**La regla de oro del modelo de datos**: cada dato se escribe una sola vez, en un lugar
canónico. Todo lo demás es proyección recomputable. Nada se copia; todo se proyecta.

**Canónicos** (fuente de verdad, editables):

| Almacén | Naturaleza | Notas |
|---|---|---|
| Entradas de bitácora | append-only | inmutables: una entrada nunca cambia de fecha |
| Tareas abiertas | tabla mutable | única verdad del estado de una tarea |
| Entidades: secciones editables | mutable | descripción, objetivos, recursos |
| `estrategia/` | mutable con gate humano | capacidad y cadencias (P5) |
| Notas | mutable | |

**Proyecciones** (derivadas, jamás editadas a mano):

- La bitácora de una entidad **no es un archivo ni una copia**: es una sección de su página
  generada filtrando las entradas por pertenencia.
- El bloque de tareas del ciclo en la bitácora.
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
  - target: "ciclos/bitacora_{fecha}_{tipo}.md#tareas-del-ciclo"
    sources: ["tareas/abiertas.md", "estrategia/cadencias.md"]
    build: "tareas_del_ciclo"

  - target: "entidades/VIGENTES/{entidad}.md#bitacora-entidad"
    sources: ["ciclos/bitacora_*.md"]
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
| Apertura | `bitacora_FECHA_tipo.md` | humano y agente |
| Cierre | `resultados_FECHA_tipo.md` | sembrado, luego del humano |

**Un archivo, un dueño.** Separar el plan de la bitácora evita tener que marcar propiedad
por zonas dentro de un mismo archivo, y deja la bitácora como superficie de escritura
limpia.

**Las clasificaciones hacen barato el cierre.** Cada entrada lleva una clasificación
extensible —`hito`, `decision`, `senal`, `friccion`, `msg`—, de modo que el informe de
cierre es mayormente un filtro determinista que el agente **redacta**, no una inferencia
que el agente inventa. Avances ← hitos. Desviaciones ← fricciones. Señales ← senal.

**El informe es la memoria de largo plazo.** Markdown no es una base de datos: la consulta
histórica se responde por informes, no escaneando el detalle. El crudo se conserva por año
y no se destruye nunca, pero un informe pobre es memoria perdida. Por eso su formato es un
problema de arquitectura.

---

## 8. Ejecución

| Componente | Decisión |
|---|---|
| Almacén | archivos `.md` + Git |
| Janitors | Python 3 |
| Motor agéntico (pruebas) | Hermes + modelo económico, invocado por CLI |
| Procesos | Markdown ejecutable por humano o agente medio |
| Scheduler | cron: revisa cadencias vencidas, tareas difusas por reevaluar, encadenamientos |
| Configuración | `.tuku/config.yaml`, uno por perfil |

**El scheduler no es opcional.** Sin un lazo periódico, las cadencias solo se evalúan
cuando el usuario aparece, y el sistema pierde su carácter proactivo — que es justamente lo
que promete el nombre.

**La elección del modelo económico es una prueba de P2**, no una restricción de
presupuesto: si un proceso necesita un modelo de frontera para no descarrilar, el proceso
está mal escrito.

---

## 9. Versionado del esquema

Los datos sobreviven al motor. El perfil declara `schema_version` en `.tuku/config.yaml`;
el motor declara qué rango soporta; `tuku doctor` compara; `tuku migrate` transforma, en un
commit propio y aislado para que el usuario revise el diff. Las migraciones se acumulan y
ninguna se borra.

---

## 10. Decisiones abiertas

| # | Decisión | De qué depende |
|---|---|---|
| 1 | `effortTime` en tareas y su mecanismo de aprendizaje | Hacer verificable el cruce con capacidad. Se decidirá con experiencia de uso |
| 2 | Cuándo se reevalúa la descripción inferida de una entidad | Frescura del modelo de operación vs. ruido de reescritura |
| 3 | Formato interno del informe de cierre | Es la memoria de largo plazo; debe ser re-consultable por un agente |
| 4 | Promoción de secciones a átomos | Diferida; el gancho (`id` por sección) ya está |
