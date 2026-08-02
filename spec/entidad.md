# spec/entidad.md — Entidades, ámbitos y jerarquía

> Define la primitiva del eje organizacional: qué es una entidad, cómo se organiza el árbol
> y qué ocurre a lo largo de su ciclo de vida.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §2 y §3.
> Ver también [`spec/cadencia.md`](cadencia.md) y [`spec/entradas.md`](entradas.md).

---

## 1. Definición

**Entidad** — Cualquier cosa sobre la que se gestiona: un ámbito, un área, un proyecto, un
cliente, un instrumento, un profesional de la salud. Es **un solo tipo** con atributos, no
una taxonomía.

`type` es **string libre** (P6). El sistema lo indexa, no lo valida contra un catálogo. La
diferencia entre un área y un proyecto es un atributo del usuario, no una distinción del
motor: el usuario decide, o el contexto sugiere.

---

## 2. Jerarquía

```
sistema → ámbito → niveles libres → entidad
```

```
entidades/
├── personal/
│   ├── personal.md              # página del ámbito
│   ├── medico/
│   │   ├── medico.md            # página del nivel
│   │   ├── pediatra.md
│   │   └── traumatologo.md
│   └── finanzas/
│       └── finanzas.md
├── trabajo/
│   ├── trabajo.md
│   ├── sw-responsible.md        # cuelga directo del ámbito
│   └── analisis-datos/
│       ├── analisis-datos.md
│       └── paper-congreso.md
└── pewma/
    ├── pewma.md
    └── productos/
        ├── productos.md
        └── tuku.md
```

### 2.1 El ámbito

Nivel raíz, obligatorio. Todo perfil tiene al menos `personal/`. El conjunto de ámbitos es
propio de cada usuario.

El ámbito no es "el nivel de más arriba": es la **frontera de confidencialidad y de
compartición**. Es lo que algún día se federa con colegas, lo que se excluye de un export, lo
que puede tener convenciones o idioma propios. Por eso tiene derechos que los niveles
intermedios no tienen —tipos propios, gobernanza declarada— y por eso es obligatorio.

### 2.2 Profundidad libre

Entre el ámbito y la entidad, la profundidad la decide el usuario. Algunas entidades cuelgan
directo del ámbito y otras se agrupan. Fijar tres niveles obligaría a inventar niveles vacíos
para cumplir el formato.

Cada nivel tiene su **página homónima**: `medico/medico.md`, `analisis-datos/analisis-datos.md`.
Es donde se describe el nivel, se declara su gobernanza y se alojan sus proyecciones.

### 2.3 El path es la jerarquía; el estado no

`parent` **se deriva del path**, no se declara. Declararlo además sería garantía de
desincronización.

El ciclo de vida va en front matter: `lifecycle: vigente | archivada`. Archivar es cambiar
una palabra, no mover un archivo — mover rompería enlaces relativos y ensuciaría el historial
con renombres masivos. Los dashboards siguen separando vigentes de archivadas; solo cambia
dónde vive el dato.

El `id` es estable e independiente del path (ADR 0001): mover una entidad de subdirectorio no
rompe ninguna referencia.

### 2.4 Anidamiento de instrucciones

Cualquier nivel puede tener un `AGENTS.md` que acota el contexto y el comportamiento
esperado para todo lo que cuelga de él. Es una razón de diseño de la jerarquía POSIX, no una
comodidad.

---

## 3. El archivo de entidad

### 3.1 Front matter

```yaml
---
id: paper-congreso            # estable, único en el perfil
type: proyecto                # string libre
lifecycle: vigente            # vigente | archivada
status: active                # active | paused | blocked_until: YYYY-MM-DD
alineamiento: >
  Publicación estratégica sobre clasificación automática de registros.
created: 2026-04-25
modified: 2026-07-06
keywords: [congreso, paper, deteccion]
---
```

| Campo | Obligatorio | Notas |
|---|---|---|
| `id` | sí | único en el perfil; no se reutiliza |
| `type` | sí | string libre |
| `lifecycle` | sí | `vigente` por defecto al alta |
| `status` | sí | silencia cadencias por ausencia (§5) |
| `alineamiento` | sí | **el objetivo de la entidad** |
| `created` / `modified` | sí | ISO |
| `keywords` | no | alimenta el tesauro vivo |

**`alineamiento` es obligatorio** porque es el insumo que permite cruzar entidades con
capacidad al abrir un ciclo. Sin él ese cruce vuelve a ser decorativo — y es lo que distingue
un plan sugerido útil de una lista de deseos.

### 3.2 Zonas

Una entidad es un **compuesto**: mezcla zonas editables y derivadas, marcadas
explícitamente. Toda zona está marcada; no hay ambigüedad.

```markdown
# Paper del congreso

<!-- tuku:editable id=descripcion -->
Paper sobre clasificación automática de registros operacionales.
<!-- /tuku:editable -->

<!-- tuku:derived id=tareas-entidad hash=… -->
**Pendientes activos**
- [ ] (2026-08-12) Archivar el proyecto `^t-2026-0210`
<!-- /tuku:derived -->

<!-- tuku:derived id=bitacora-entidad hash=… -->
### Julio 2026
**Hitos:**
- **2026-07-06:** Póster presentado.
<!-- /tuku:derived -->
```

Zonas derivadas estándar: `tareas-entidad`, `bitacora-entidad`, y en las páginas de nivel,
`dashboard`. Las editables las define el usuario o la plantilla del tipo.

**Las derivadas no se hacen read-only: se detecta la divergencia.** Si el contenido no
coincide con el hash registrado, el motor pregunta antes de sobrescribir
(`docs/arquitectura.md` §3.2).

### 3.3 Descripción inferida

El agente mantiene una descripción que intenta capturar un **modelo de operación rudimentario**
de la entidad: cómo se trabaja con ella, qué la hace avanzar, qué la estanca. Es lo que da
inteligencia a la cadencia por ausencia — permite distinguir "lleva un mes quieta y eso es
anormal" de "avanza a saltos de tres meses".

Vive en zona editable propia (`id=descripcion-inferida`) y sigue el patrón de sembrar y
corregir: el agente la propone, el humano la ajusta y pasa a ser suya.

---

## 4. Páginas de nivel y de ámbito

Una página homónima es una entidad con dos zonas derivadas adicionales.

### 4.1 Dashboard

Lista lo que cuelga del nivel con su estado, su foco sugerido y señales de actividad. Es
derivado puro:

```markdown
<!-- tuku:derived id=dashboard hash=… -->
**[SW Responsible](sw-responsible.md)** — Operación normal.
- 🤖 *Foco: generar el reporte legible de las revisiones periódicas.*

**[Herramientas](herramientas.md)** — Servidor de pruebas frágil; no intervenir.
- 📅 *Sin actividad en más de 1 mes*
<!-- /tuku:derived -->
```

El marcador de inactividad es la **cadencia por ausencia renderizada**, no un adorno.

### 4.2 Gobernanza declarada

Zona editable que el agente lee **siempre** que opera dentro de ese nivel:

```markdown
<!-- tuku:editable id=gobernanza -->
> [!warning] No sobre-burocratizar
> Este ámbito es deliberadamente ligero. Todo es un proyecto. Sin cadencias ni presión de
> entrega. Si algo necesita más estructura, probablemente pertenece a otro ámbito.
<!-- /tuku:editable -->
```

Es la formalización de una práctica ya en uso. Complementa al `AGENTS.md` del nivel: la
gobernanza es para el usuario y el agente por igual; el `AGENTS.md` es instrucción técnica.

---

## 5. `status` y el silencio

| Valor | Significado |
|---|---|
| `active` | operación normal |
| `paused` | detenida a propósito; las cadencias por ausencia no disparan |
| `blocked_until: YYYY-MM-DD` | esperando a un tercero; no dispara hasta esa fecha |

Sin esto, la cadencia por ausencia produce ruido semanal sobre entidades quietas por decisión, el usuario aprende a ignorar el bloque completo, y muere la confianza en el sistema entero. **La cadencia dispara siempre, de forma determinista; el `status` la silencia.** La inteligencia va en interpretar el silencio, no en decidir si avisar.

`status` lo fija el usuario con una frase al agente. Es corregible en una línea.

**Resolución automática desde el plan.** Cuando el usuario mueve una entidad a "No entra" al corregir el plan de un ciclo, el motor escribe automáticamente `status: blocked_until: <cycle_end de ese ciclo>` en la entidad. Reutiliza el campo que ya existe para "esperando a un tercero" en vez de crear uno nuevo — simplificación deliberada; si en el futuro hace falta distinguir "decidí no tocarlo" de "un tercero me tiene esperando", se separa en `paused_reason`.

---

## 6. Ciclo de vida

| Evento | Qué ocurre |
|---|---|
| **Alta** | Se asigna `id`, `created`, `lifecycle: vigente`, `status: active`. Se aplica la plantilla del tipo si existe |
| **Archivar** | `lifecycle: archivada`. Sus cadencias se **pausan**, no se borran: al reactivarla vuelven a emitir |
| **Archivar con tareas abiertas** | El motor las lista y **pide decisión**: cerrar, cancelar o reasignar. No archiva en silencio |
| **Reactivar** | `lifecycle: vigente`. Las cadencias vuelven a emitir desde ese momento; no se recuperan disparos perdidos |
| **Mover** | Cambia el path y el padre derivado; el `id` no cambia. Un janitor reescribe las rutas de los enlaces |
| **Eliminar** | Sus cadencias mueren. **Las tareas y entradas ya emitidas sobreviven** con referencia colgante |

### 6.1 La regla muere, lo emitido no

Una cadencia es una regla y tiene el ciclo de vida de su portador. Una tarea emitida es un
objeto canónico independiente y **sobrevive siempre** a la desaparición de su origen.

Si borrar una entidad borrara sus tareas pendientes, borrar algo eliminaría compromisos en
silencio. En un sistema cuya promesa es recordar, ese es el peor fallo posible.

Por eso `origin` es una referencia **blanda**: un `origin` que ya no resuelve no viola
ninguna invariante. Es una tarea huérfana perfectamente válida; el motor solo pierde la
capacidad de explicar por qué existe.

### 6.2 "¿Qué se rompe si borro esto?"

Como todo está declarado, el motor puede responderlo exacto antes de ejecutar: cuántas
entidades cuelgan, cuántas cadencias mueren, cuántas tareas quedan huérfanas, cuántas
entradas apuntan a ella. `tuku doctor` lo hace, y la eliminación lo muestra antes de
confirmar.

---

## 7. Invariantes

| # | Regla | Garante |
|---|---|---|
| N1 | Front matter válido con los campos obligatorios de §3.1 | janitor |
| N2 | `id` único en el perfil | janitor |
| N3 | Toda entidad está dentro de un ámbito | janitor |
| N4 | Todo directorio de nivel tiene su página homónima | janitor |
| N5 | Toda zona está marcada `editable` o `derived` | janitor |
| N6 | Toda zona derivada tiene hash de fuentes coincidente | janitor de build |
| N7 | Toda entidad vigente tiene `alineamiento` no vacío | janitor |
| N8 | Una entidad archivada no recibe tareas nuevas por cadencia | janitor |
| N9 | Los enlaces internos de la entidad resuelven | janitor |

---

## 8. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | Cuándo se reevalúa la descripción inferida |
| 2 | Si `type` admite una plantilla obligatoria de zonas editables, o queda a criterio del usuario |
| 3 | Promoción de una zona a archivo propio (átomos). Diferida; el gancho —`id` por zona— ya está |
| 4 | Si las páginas de ámbito admiten políticas ejecutables (export, federación) o solo prosa |
