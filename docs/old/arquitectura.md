# Arquitectura

> `docs/arquitectura.md` · La forma del sistema. Se apoya en [`brief.md#3-principios`](brief.md#3-principios) y precede a `spec/`, que fija los formatos exactos.

---

## 1. La tesis arquitectónica

Toda la arquitectura se deduce de una sola afirmación: **la información vive en el Markdown**. No en una base de datos, no en el motor, no en la memoria de un agente. Todo lo demás (visores, agentes, janitors, servidores) es periferia reemplazable alrededor de un repositorio de archivos de texto.

De ahí salen cuatro capas, en este orden de dependencia:

```
  JANITORS          Python determinista                  garantizan, no juzgan
  AGENTES           Hermes / Claude Code / Antigravity   proponen, no deciden
  VISORES           Obsidian → Quartz → web              muestran, no interpretan
  ─────────────────────────────────────────────────────
  ARCHIVOS          repositorio Git de .md               la verdad
```

Cada capa superior puede desaparecer sin que la de abajo pierda nada. Si mañana no existe ningún agente, el repositorio sigue siendo un sistema de gestión operable a mano.

Esta arquitectura no parte de cero. TUKU generaliza `mac-jpgil`, un repositorio MaC en uso real con ámbitos, `AGENTS.md` anidados, janitors y procesos semanales. Lo que aquí se especifica ya fue probado a mano; el trabajo es volverlo instalable para alguien que no es su autor.

---

## 2. Dos artefactos

TUKU se compone de un **motor** y N **perfiles**. Nunca se mezclan.

| | Motor | Perfil |
|---|---|---|
| Qué es | código, janitors, procesos, plantillas | bitácora, tareas, entidades, notas |
| Dónde vive | site-packages, vía pipx | repositorio Git del usuario |
| Quién lo versiona | PEWMA.AI | el usuario |
| Vida útil | años | décadas |

El motor nunca se copia dentro del perfil. Un motor sirve N perfiles, y el flag `--profile` existe desde el primer commit: **el diseño local es el diseño del servidor**. Detalle completo en [`deployment.md`](deployment.md).

---

## 3. Layout del perfil

```
mi-tuku/
├── .tuku/
│   ├── config.yaml          # schema_version, tipos, derivaciones, clasificaciones
│   ├── tuku.log             # log del motor, no versionado
│   └── procesos/            # punteros a los procesos del motor instalado
├── AGENTS.md                # reglas raíz, anidables por nivel
├── CLAUDE.md → AGENTS.md    # symlink, compatibilidad de clientes (§6)
├── entradas/                # canónico inmutable
│   ├── entradas.md          # activo, superficie de escritura
│   ├── entradas-2026-08.md  # mes cerrado
│   └── 2025/                # años anteriores, archivado por año
├── tareas/
│   ├── tareas.md            # único archivo mutable
│   └── 2025/                # años anteriores, archivado por año
├── ciclos/
│   ├── plan_2026-08-10_turno.md
│   └── resultados_2026-07-28_turno.md
├── ambitos/
│   ├── paranal/
│   │   ├── paranal.md       # página del ámbito
│   │   ├── AGENTS.md        # reglas propias del ámbito
│   │   └── analisis-datos/
│   │       ├── analisis-datos.md
│   │       └── paper-congreso.md
│   ├── pewma/
│   └── personal/
├── tipos/
│   └── cliente.md
├── estrategia/
│   ├── cadencias.md
│   └── capacidad.md
└── notas/
    ├── notas.md             # índice derivado
    └── ARCHIVADO/
```

**La jerarquía es sistema → ámbito → niveles libres → entidad.** Lo que en `mac-jpgil` se llamaba *organización* aquí es **ámbito**: el término anterior sugería una empresa, y `personal` no lo es. El ámbito es obligatorio y es la frontera de confidencialidad y de compartición: es lo que algún día se federa, lo que se excluye de un export, lo que puede tener convenciones propias. Entre el ámbito y la entidad la profundidad es libre.

**Cada nivel tiene su página homónima**: `paranal/paranal.md`, `paranal/analisis-datos/analisis-datos.md`. Da un lugar natural para describir el nivel, declarar su gobernanza y alojar sus proyecciones.

**El path no lleva el estado.** El ciclo de vida es `lifecycle: vigente | archivada` en front matter. Archivar es cambiar una palabra, no mover un archivo: mover rompería enlaces relativos y ensuciaría el historial con renombres masivos.

**`parent` se deriva del path**, no se declara. El `id` sigue siendo estable e independiente, así que mover una entidad no rompe referencias.

---

## 4. Canónico y proyección

**La regla de oro del modelo de datos**: cada dato se escribe una sola vez, en un lugar canónico. Todo lo demás es proyección recomputable. Nada se copia; todo se proyecta.

**Canónicos** (fuente de verdad, editables):

| Almacén | Naturaleza | Notas |
|---|---|---|
| `entradas/` | inmutable, particionado por mes | una entrada nunca cambia de fecha ni contenido |
| `tareas/tareas.md` | mutable | única verdad del estado de una tarea |
| `ciclos/plan_*` | declaración del ciclo | el conjunto es el calendario |
| Entidades: secciones editables | mutable | descripción, objetivos, recursos |
| `estrategia/` | mutable con gate humano | capacidad y cadencias (P5) |
| `notas/*.md` | mutable | se corrige editando, no enmendando |

**Proyecciones** (derivadas, jamás editadas a mano):

- La bitácora de una entidad y la de un ciclo son **la misma clase de objeto**: proyecciones de `entradas/` con distinto filtro, por pertenencia una y por rango de fechas la otra. Ninguna es un almacén.
- El bloque de tareas del ciclo, dentro del plan.
- El índice de notas y la proyección de notas en la página de su entidad.
- Índices, dashboards, resúmenes anuales.

### 4.1 Marcado de secciones

Una página de entidad es un **compuesto**: mezcla secciones editables y derivadas, marcadas con comentarios HTML invisibles en cualquier renderizador.

```markdown
<!-- tuku:editable id=descripcion -->
...contenido del usuario...
<!-- /tuku:editable -->

<!-- tuku:derived id=bitacora-entidad hash=a1b2c3 -->
...generado por el motor...
<!-- /tuku:derived -->
```

Toda sección está marcada como una u otra; no hay ambigüedad.

### 4.2 No se hace read-only: se detecta

El usuario escribirá dentro de una zona derivada tarde o temprano, porque Obsidian no lo impide y porque es lo natural. La respuesta no es bloquear el archivo sino **detectar la divergencia**: si el contenido no coincide con el hash registrado, el motor pregunta antes de sobrescribir.

### 4.3 El grafo de derivaciones

La relación entre canónicos y proyecciones **se declara**, no se programa. En `.tuku/config.yaml`:

```yaml
derivations:
  - target: "ambitos/{ruta}/{entidad}.md#bitacora-entidad"
    sources: ["entradas/**/*.md"]
    filter: "entidad == {entidad}"
    build: "proyeccion_entidad"
```

El grafo debe ser acíclico y se valida al arrancar. El build corre sobre el diff, no sobre el repositorio completo: el motor recibe la lista de archivos cambiados y recomputa solo lo alcanzable desde ahí. Ningún LLM participa de este lazo.

---

## 5. Determinismo primero, agencia al final

Materialización de P3, y la regla que gobierna el diseño de todo janitor. Cada familia de coherencia tiene garante y costo propios:

| Familia | Ejemplos | Garante | Costo |
|---|---|---|---|
| **Invariante** | front matter válido, `id` único, enlaces resuelven, grafo acíclico | janitor | barato |
| **Derivación** | todo derivado existe y su hash coincide | janitor de build | barato |
| **Semántica** | la proyección se lee bien, una desviación se reporta | agente | caro |

Los janitors son idempotentes por construcción: correrlos dos veces produce el mismo resultado, y borrar un derivado no pierde información.

**Criterio de asignación.** Ante cualquier función nueva, la pregunta es si puede escribirse como regla. Si puede, es janitor, y no se admite que un agente la haga porque resulte más rápido de programar. El agente entra solo donde hay juicio irreducible: redactar, clasificar lo ambiguo, contrastar lo esperado contra lo ocurrido.

**Herencia de `mac-jpgil`.** Los janitors existentes se portan, no se reinventan: corrección de enlaces Obsidian a Markdown, detección de enlaces rotos y huérfanos, índice de notas desde front matter, regeneración de las páginas de ámbito, vocabulario controlado de categorías, gestión de pendientes (linter, scan, transfer, validate) y contexto de commits. Todos comparten el prefijo `jntr.` y la misma promesa: sin API, sin red, sin créditos.

---

## 6. La interfaz de agente

El agente es la puerta principal del sistema, pero **no es una pieza de TUKU**: es un cliente que lee el repositorio y escribe en él siguiendo las reglas que encuentra ahí dentro.

**Tres clientes soportados a la vez, sin adaptadores.** Hermes, Claude Code y Antigravity deben poder operar el mismo perfil, en cualquier orden y sin que el repositorio note la diferencia. La compatibilidad no se logra con una capa de abstracción sino eliminando la necesidad de una: los tres son clientes de terminal que leen archivos de instrucciones del árbol y ejecutan comandos.

| Cliente | Rol en las fases iniciales |
|---|---|
| **Claude Code** | desarrollo del motor y operación del perfil propio |
| **Hermes** | agente de referencia, el que se instala con el producto |
| **Antigravity** | verificación de que el diseño no depende de un proveedor |

La convención de instrucciones es `AGENTS.md`, con `CLAUDE.md` como symlink hacia él. Un solo texto, tres lectores: si hay que escribir dos versiones, la regla estaba mal escrita (criterio de éxito 7 del brief).

**Los límites del agente se declaran en el propio `AGENTS.md`**, siguiendo el patrón ya probado en `mac-jpgil`: dos niveles, *preguntar primero* (mover archivos, tocar `AGENTS.md`, cerrar un ciclo) y *nunca* (escribir fuera de las carpetas conocidas, borrar sin confirmación, comprometer credenciales).

**El agente propone, el usuario dispone.** Cuando el agente deduce algo a partir de la bitácora (un cliente nuevo, un proyecto que cambió de estado, una persona que vale la pena registrar) no lo escribe: lo ofrece como opciones concretas, y el usuario aprueba con una palabra. Es P4 y P5 vueltos mecánica de conversación, y es el mecanismo por el que la estructura emerge sin que nadie la declare por adelantado.

---

## 7. Las reglas viven junto a lo que rigen

`AGENTS.md` se guarda en la carpeta de aquello que rige y vale para todo lo que cuelga hacia abajo. Un nivel más adentro afina la regla sin repetir lo de arriba, así que la carpeta de un cliente sabe cosas que la de los clientes en general no tiene por qué saber.

Esto no es configuración, es el sistema mismo: mover una carpeta se lleva sus reglas consigo, copiarla las replica, y un cliente nuevo nace sabiendo cómo se lo gestiona porque cuelga de donde eso está escrito. Es también lo que mantiene honesta la promesa de que la verdad está en los archivos: la lógica no está escondida en el motor ni en la memoria del agente.

---

## 8. Orden de construcción

El sistema se construye por capacidades completas, en este orden. Cada escalón se usa de verdad antes de abrir el siguiente, y ninguno requiere que el posterior exista.

| # | Capacidad | Qué habilita |
|---|---|---|
| 1 | **Registrar en la bitácora** | una línea en lenguaje natural entra como entrada con fecha y clasificación |
| 2 | **Tareas y pendientes** | lo registrado se reconoce como tarea y vive con estado propio |
| 3 | **Cadencias declaradas** | existe un lugar donde escribir lo que debe volver, y vuelve |
| 4 | **Apertura y cierre de ciclo** | plan al abrir, reporte al cerrar |
| 5 | **Reportes de período** | cómo vamos esta semana, este mes, este período |
| 6 | **Notas asistidas** | el agente redacta el front matter tedioso, el usuario escribe la nota |
| 7 | **Entidades y ámbitos** | el sistema reconoce de qué y de quién se está hablando |

El orden no es arbitrario: cada capacidad produce el insumo de la siguiente. Sin bitácora no hay qué reportar; sin tareas no hay qué planificar; sin cadencias el ciclo no se abre solo. Las entidades van al final a propósito, porque la estructura debe emerger de material real y no declararse en vacío (brief §4.5).

---

## 9. Ciclos, cadencias y memoria

**El ciclo lo define la vida del usuario, no el almanaque**: un turno de martes a martes, un descanso, una semana, un semestre. La cadencia de ciclo lo declara, y el conjunto de archivos `plan_*` **es** el calendario.

| Momento | Artefacto | Dueño |
|---|---|---|
| Apertura | `plan_FECHA_tipo.md` | propuesto, luego del usuario |
| Cierre | `resultados_FECHA_tipo.md` | propuesto, luego del usuario |

**Cuatro formas de disparo de una cadencia:**

| Forma | Se dispara por | Ejemplo |
|---|---|---|
| Absoluta | calendario | el día 1, pagar cuentas |
| Relativa a evento | evento + Δt | venta hoy → contactar en 3 meses |
| Por ausencia | que *no* pasó nada | entidad sin entradas en 4 semanas |
| Por completitud | cierre de una tarea | al cerrar X, activar Y |

La forma por ausencia es la más valiosa y la que necesita silenciador: dispara siempre de forma determinista, y el estado de la entidad (`active | paused | blocked_until`) la silencia. La inteligencia va en interpretar el silencio, no en decidir si avisar.

**Las clasificaciones abaratan el cierre.** Cada entrada lleva una clasificación extensible (`hito`, `decision`, `senal`), de modo que buena parte del reporte parte de un filtro determinista que el agente **redacta**, no de una inferencia que inventa. Las desviaciones son la excepción: no existe clasificación de fricción porque nadie rotula sus propios fracasos mientras trabaja, y se descubren al cerrar contrastando lo esperado de cada entidad contra lo registrado.

**El reporte es la memoria de largo plazo.** Markdown no es una base de datos: la consulta histórica se responde por reportes, no escaneando el detalle. El crudo se conserva por año y no se destruye nunca, pero un reporte pobre es memoria perdida, y por eso su formato es un problema de arquitectura.

---

## 10. Visores

Obsidian es el primer caso de uso de interfaz gráfica, y sirve de prueba para los demás: **si funciona en Obsidian, funciona en Quartz y en cualquier servidor web**, porque los tres leen los mismos archivos y ninguno interpreta. Un visor que necesite lógica propia para que los archivos tengan sentido es evidencia de que la arquitectura de archivos está mal (P1).

| Visor | Cuándo | Estado |
|---|---|---|
| **Obsidian** | frente al computador, local | primero |
| **Quartz** | acceso web de solo lectura | después |
| **Servidor web** | multiusuario | eventual |

El único requisito que los visores imponen al formato es que el marcado de secciones (§4.1) sea invisible para todos ellos, y por eso son comentarios HTML.

---

## 11. Instalación y despliegue

**`pipx install`** desde el repositorio, y `tuku init` crea un perfil vacío con su layout, su `config.yaml`, sus `AGENTS.md` de ejemplo y las cadencias de sistema ya propuestas, de modo que el primer cierre de ciclo ocurra aunque el usuario no haya configurado nada.

Las preconfiguraciones de agente se instalan **en el perfil, no en el motor**: los `AGENTS.md` del árbol y `.tuku/procesos/` con punteros a los procesos del motor instalado. La razón es que son datos del usuario, versionados y editables por él, no código versionado por PEWMA.AI. Un `AGENTS.md` que viviera en site-packages no podría corregirse un domingo por la tarde, que es justamente la prueba de que la regla estaba bien escrita.

**El camino de despliegue:**

| Fase | Dónde | Qué corre |
|---|---|---|
| Ahora | computador del usuario | motor por pipx, Obsidian, agente de terminal |
| Después | VM en Oracle Cloud | Quartz 5 y Hermes con gateway API |

El paso de local a servidor cambia dónde viven los perfiles, no el modelo, y por eso `--profile` existe desde el primer commit. Nada de lo que se construya ahora debe asumir un solo perfil ni una sola máquina.

---

## 12. Ejecución

| Componente | Decisión |
|---|---|
| Almacén | archivos `.md` + Git |
| Janitors | Python 3.14, prefijo `jntr.` |
| Clientes de agente | Hermes, Claude Code, Antigravity (los tres) |
| Procesos | Markdown ejecutable por humano o agente medio |
| Scheduler | cron: cadencias vencidas, tareas por reevaluar, encadenamientos |
| Configuración | `.tuku/config.yaml`, uno por perfil |
| `tuku.log` | log del motor, en `.tuku/`, **no versionado** |

**El scheduler no es opcional.** Sin un lazo periódico las cadencias solo se evalúan cuando el usuario aparece, y el sistema pierde su carácter proactivo, que es justamente lo que promete el nombre.

**La elección del modelo económico es una prueba de P2**, no una restricción de presupuesto: si un proceso necesita un modelo de frontera para no descarrilar, el proceso está mal escrito.

**Aislamiento de pruebas agénticas.** Cada test integrado instancia un perfil de agente desde cero, en entorno efímero, para que las pruebas sean deterministas y no arrastren contexto previo.

---

## 13. Modos de evaluación

Tres formas de obtener información del perfil, con costo y persistencia distintos:

| Modo | Materializa | Cuándo |
|---|---|---|
| **Build** | sí, con hash de fuentes | derivaciones declaradas en el grafo |
| **Invariante** | no, solo valida | janitors de coherencia |
| **Consulta (RADAR)** | no, nunca | bajo demanda, siempre fresca |

**RADAR** es la capa de consulta: tareas trancadas, entidades con actividad anómala, seguimientos vencidos, entidades recién desbloqueadas. Todo lo que un humano responsable notaría con solo mirar el estado actual. Es determinista, se calcula con Python sobre el estado presente, sin LLM. El agente la invoca en mitad de una conversación; no tiene archivo propio ni existe fuera del momento en que se consulta.

---

## 14. Versionado del esquema

Los datos sobreviven al motor. El perfil declara `schema_version` en `.tuku/config.yaml`; el motor declara qué rango soporta; `tuku doctor` compara; `tuku migrate` transforma, en un commit propio y aislado para que el usuario revise el diff. Las migraciones se acumulan y ninguna se borra.

---

## 15. Decisiones abiertas

| # | Decisión | De qué depende |
|---|---|---|
| 1 | `effortTime` en tareas y su mecanismo de aprendizaje | hacer verificable el cruce con capacidad; se decide con uso real |
| 2 | Cuándo se reevalúa la descripción inferida de una entidad | frescura del modelo vs. ruido de reescritura |
| 3 | Formato interno del reporte de cierre | es la memoria de largo plazo; debe ser re-consultable por un agente |
| 4 | Promoción de secciones a átomos | diferida; el gancho (`id` por sección) ya está |
| 5 | Alcance del gateway de Hermes en la VM | cuánto se quiere exponer fuera de la máquina local |
| 6 | Renombre `entidades/` → `ambitos/` en código y specs | el layout cambió aquí; falta propagarlo (§3) |
