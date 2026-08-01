# spec/artefactos-ciclo.md — Plan, bitácora e informes

> Define qué archivos produce la apertura y el cierre de un ciclo, quién es dueño de cada
> uno y cómo se generan.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §7.
> Ver también [`spec/bitacora.md`](bitacora.md), [`spec/tarea.md`](tarea.md),
> [`spec/cadencia.md`](cadencia.md).

---

## 1. Los tres artefactos

| Momento | Archivo | Dueño | Naturaleza |
|---|---|---|---|
| Apertura | `plan_YYYY-MM-DD_<tipo>.md` | sembrado → humano | mixto |
| Apertura | `bitacora_YYYY-MM-DD_<tipo>.md` | humano y agente | canónico |
| Cierre | `resultados_YYYY-MM-DD_<tipo>.md` | sembrado → humano | mixto |

**Un archivo, un dueño.** Separar plan, registro y retrospectiva evita tener que marcar
propiedad por zonas dentro de un mismo archivo y deja la bitácora como superficie de
escritura limpia. Los tres comparten `YYYY-MM-DD` —primer día del ciclo— y `<tipo>`, de modo
que se ordenan juntos y se emparejan sin índice.

**Sembrado** significa: el agente lo genera **una vez**, el humano lo corrige, y desde ese
momento ningún janitor vuelve a tocarlo. No es derivado y no se regenera.

---

## 2. `plan_*` — Plan del ciclo

### 2.1 Front matter

```yaml
---
id: plan-2026-06-30-turno
type: plan
created: 2026-06-30
modified: 2026-06-30
cycle_type: turno
cycle_start: 2026-06-30
cycle_end: 2026-07-07
seeded_by: tuku 0.4.2+g27b3aed / deepseek-v4-flash
---
```

### 2.2 Estructura

```markdown
# Plan del ciclo

## Intención
1. **[entidad]** — qué se busca lograr.
2. …

## No entra (y por qué)
- **[entidad]** — razón explícita.

## Restricciones y contexto
- …

## Señales a vigilar
- …

<!-- tuku:derived id=tareas-del-ciclo hash=… -->
…tareas vigentes y postergadas…
<!-- /tuku:derived -->
```

### 2.3 "No entra (y por qué)"

Sección obligatoria. Declara el alcance **negativo** del ciclo con su justificación.

Es la pieza que convierte un plan en un compromiso: sin ella, todo lo no hecho parece
incumplimiento. Con ella, el cierre puede distinguir tres cosas distintas —lo que se
decidió no hacer, lo que se intentó y no salió, y lo que simplemente se olvidó— y solo la
segunda y la tercera son desviaciones.

Está en uso en los ocho ciclos del corpus, sin excepción. Es la única sección del plan que
no puede quedar vacía: si no hay nada excluido, el plan no está acotado.

### 2.4 Insumos del sembrado

| Insumo | Aporta |
|---|---|
| `resultados_*` de los 3–4 ciclos anteriores | aprendizajes, desviaciones, momentum |
| `tareas/abiertas.md` | vigentes, postergadas al ciclo, bloqueadas, arrastre |
| Entidades VIGENTES con sus objetivos | qué está activo y qué persigue |
| `estrategia/capacidad.md` | límite contra el que se contrasta la intención |
| Cadencias vigentes | compromisos rítmicos que caen en el ciclo |

Sin las entidades vigentes y sus objetivos, el cruce con capacidad es decorativo. Es el
insumo que más eleva la calidad del plan sugerido y el más fácil de omitir.

### 2.5 Delta de corrección

El motor registra la diferencia entre lo sembrado y lo que queda tras la corrección humana,
en `<!-- tuku: seed_delta=… -->`. Es gratis de capturar y es la única medida directa de qué
tan mal calibrado está el sembrado respecto a la realidad del usuario. Un delta grande y
sostenido no es fallo del usuario: es señal de que hay que revisar el proceso de apertura.

---

## 3. `resultados_*` — Cierre del ciclo

### 3.1 Estructura

```markdown
# Resultados del ciclo

## TL;DR
> Una o dos frases: carácter del ciclo y su saldo.

## Avances
- …

## Desviaciones
- …

## Aprendizajes
- …

## Momentum y señales
- …
```

### 3.2 Cómo se genera: filtro primero, redacción después

| Sección | Origen | Familia |
|---|---|---|
| Avances | entradas clasificadas `Hito` + tareas completadas en el ciclo | derivación |
| Desviaciones | intención del plan sin entradas asociadas · tareas del ciclo no cerradas · tareas con `cycles` sobre el umbral | derivación |
| Aprendizajes | entradas `Señal` y `Decisión` | derivación como insumo, redacción semántica |
| Momentum y señales | entradas `Señal` + entidades con actividad creciente o detenida | derivación como insumo, redacción semántica |

El agente **no busca** qué pasó: recibe un conjunto ya filtrado y lo redacta. Esa es la
razón por la que las clasificaciones de entrada existen, y lo que hace que el cierre sea
barato y reproducible.

**Lo excluido en "No entra" nunca cuenta como desviación.** Es la regla que impide que el
informe confunda una decisión con un fracaso.

**Las tareas canceladas se listan aparte de las incumplidas**, con su razón. Cancelar es una
decisión; no cerrar es una desviación.

### 3.3 Formato estable, obligatorio

El informe es la **memoria de largo plazo** del sistema: Markdown no es una base de datos y
la consulta histórica se responde por informes, no escaneando el detalle. Un informe pobre
es memoria perdida, sin recuperación posible.

De ahí dos exigencias:

- **Front matter completo**, incluidas las entidades tocadas en el ciclo, para que un agente
  pueda encontrar el informe sin leerlo entero.
- **Encabezados fijos**. Las cinco secciones de §3.1 no cambian de nombre ni de orden entre
  ciclos ni entre versiones del motor. Todo lo variable va en los informes por audiencia
  (§4), no aquí.

```yaml
---
id: res-2026-06-30-turno
type: resultados
cycle_type: turno
cycle_start: 2026-06-30
cycle_end: 2026-07-07
entities: [deputy, sw-responsible, pds, colaboraciones]
carryover_alerts: [t-2026-0087]
generated: 2026-07-07T18:04:00-04:00
seeded_by: tuku 0.4.2+g27b3aed / deepseek-v4-flash
---
```

### 3.4 Cierre de la bitácora

El cierre marca `status: closed` en la bitácora del ciclo. A partir de ahí es inmutable
(`spec/bitacora.md` §6).

---

## 4. Informes por audiencia

`resultados_*` tiene una audiencia: el propio usuario, en el ciclo siguiente. Hay otros
informes que se generan **desde el mismo material** para audiencias distintas, con idioma,
estructura y nivel de detalle propios.

Caso observado: los ciclos de tipo `turno` producen un informe de fin de turno en inglés,
organizado por rol —mantenimiento, proyectos, administración—, destinado a colegas de la
institución. Los ciclos de tipo `descanso` no lo producen.

### 4.1 Modelo

Un informe por audiencia es un **skill invocable**, y opcionalmente una **cadencia asociada
al fin de un ciclo de cierto tipo**:

```yaml
reports:
  - id: fin-de-turno
    cycle_types: [turno]
    template: plantillas/fin-de-turno.md
    trigger: cycle_close        # o manual
    language: en
```

- `trigger: cycle_close` lo genera automáticamente al cerrar un ciclo de ese tipo.
- `trigger: manual` lo deja disponible como skill a pedido.

En ambos casos el resultado es **sembrado**: se genera una vez y pasa a ser del humano.

### 4.2 Plantillas de informe

La estructura de un informe por audiencia **va a cambiar** con el tiempo, y eso es normal:
depende de qué espera quien lo lee. Por eso vive en una **plantilla editable del perfil**,
no en el código del motor. Cambiar la forma del informe de fin de turno es editar un
Markdown, no actualizar TUKU.

Las plantillas admiten marcadores de sección que el motor rellena con material ya filtrado
(§3.2), de modo que quien edita la plantilla decide **qué aparece y en qué orden**, sin
tener que describir cómo obtenerlo.

### 4.3 Dónde viven

```
ciclos/informes/fin-de-turno_2026-06-30.md
plantillas/fin-de-turno.md
```

---

## 5. Apertura de ciclo — orden de operaciones

1. Resolver el ciclo desde las cadencias: tipo, fecha inicial y final.
2. Crear `bitacora_*` con los días sembrados y el front matter completo.
3. Incrementar `cycles` de las tareas abiertas.
4. Resolver las fechas relativas: `(next:<tipo>)` que apunten a este ciclo pasan a vigentes.
5. Crear `plan_*` sembrado con los insumos de §2.4.
6. Renderizar las derivadas: tareas del ciclo en plan y bitácora.
7. Correr los janitors de invariantes.
8. Commit semántico.

Los pasos 1–4, 6, 7 y 8 son deterministas y funcionan sin ningún modelo. Solo el 5 requiere
agente, y si no hay agente disponible el plan se crea con los insumos listados y sin
redacción. **El ciclo abre igual sin conexión.**

---

## 6. Cierre de ciclo — orden de operaciones

1. Recoger marcas de completitud dejadas en proyecciones y propagarlas al canónico.
2. Calcular los conjuntos de §3.2.
3. Crear `resultados_*` sembrado.
4. Generar los informes por audiencia con `trigger: cycle_close`.
5. Marcar la bitácora `status: closed`.
6. Archivar tareas completadas cuyo plazo de retención venció.
7. Janitors e invariantes.
8. Commit semántico.

---

## 7. Invariantes

| # | Regla | Garante |
|---|---|---|
| C1 | Los tres artefactos de un ciclo comparten `cycle_start` y `cycle_type` | janitor |
| C2 | Existe a lo más un ciclo abierto por `cycle_type` | janitor |
| C3 | Los ciclos de un mismo tipo no se solapan | janitor |
| C4 | Un ciclo cerrado tiene sus tres artefactos | janitor |
| C5 | `plan_*` tiene "No entra" no vacío | janitor |
| C6 | Un artefacto sembrado no se regenera tras la corrección humana | janitor de build |
| C7 | Los encabezados de `resultados_*` son los cinco de §3.1 | janitor |

---

## 8. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | ¿Pueden coexistir ciclos de tipos distintos y solapados —por ejemplo un ciclo mensual sobre uno de turno—? Hoy C2 y C3 lo permiten entre tipos distintos, pero no está resuelto cómo se reparten las tareas entre ellos |
| 2 | Resumen anual: ¿derivado puro que concatena `resultados_*`, o artefacto sembrado propio? |
| 3 | Sintaxis exacta de los marcadores de sección en las plantillas de informe |
