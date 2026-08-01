# spec/artefactos-ciclo.md — Plan, resultados e informes

> Define qué archivos declara y produce un ciclo, quién es dueño de cada uno y cómo se
> generan.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §7.
> Ver también [`spec/entradas.md`](entradas.md), [`spec/tarea.md`](tarea.md),
> [`spec/cadencia.md`](cadencia.md).

---

## 1. Dos artefactos

| Momento | Archivo | Dueño | Naturaleza |
|---|---|---|---|
| Apertura | `plan_YYYY-MM-DD_<tipo>.md` | sembrado → humano | **declaración canónica del ciclo** |
| Cierre | `resultados_YYYY-MM-DD_<tipo>.md` | sembrado → humano | informe |

```
ciclos/
├── plan_2026-08-10_temuco.md
├── resultados_2026-07-28_turno.md
└── 2025/
```

**No existe un archivo de bitácora de ciclo.** Las entradas viven en `entradas/` y la
bitácora del ciclo es una proyección que se congela dentro de `resultados_*` al cerrar
(§3.5). Durante el ciclo se escribe en el mes, nunca sobre una proyección.

**Sembrado** significa: el agente lo genera **una vez**, el humano lo corrige, y desde ese
momento ningún janitor vuelve a tocarlo. No es derivado y no se regenera.

---

## 2. `plan_*` — Declaración del ciclo

El plan responde dos cosas a la vez: **dónde y cuándo estoy**, y **qué me propongo**. Lo
primero es lo que lo convierte en pieza estructural.

### 2.1 Front matter

```yaml
---
id: plan-2026-08-10-temuco
type: plan
cycle_type: temuco          # string libre
place: Temuco               # opcional
cycle_start: 2026-08-10
cycle_end: 2026-08-16
status: open                # open | closed
created: 2026-08-09
modified: 2026-08-10
seeded_by: tuku 0.4.2+g27b3aed / deepseek-v4-flash
---
```

`cycle_type` es **string libre**: `turno`, `descanso`, `vacaciones`, `mision`, `temuco`. Es
P6 aplicado al eje temporal — los modos de vida de una persona no son anticipables y no
tienen por qué serlo.

### 2.2 El conjunto de planes es el calendario

Los archivos `plan_*` —pasados y futuros— **son** el calendario de ciclos del usuario. De
ahí se siguen tres cosas:

- Las cadencias **proponen** ciclos y siembran sus planes; el archivo de plan es la verdad.
- `(next:turno)` y sus formas se resuelven contra este conjunto (`spec/tarea.md` §4.1).
- **Romper la cadencia es normal, no excepcional.** Si la próxima semana el usuario trabaja
  desde otra ciudad, crea `plan_2026-08-10_temuco.md`; las tareas postergadas al próximo
  turno se re-resuelven solas al turno que efectivamente corresponda.

Un ciclo declarado a mano y uno sembrado por cadencia son indistinguibles: mismo formato,
mismas reglas.

### 2.3 Estructura

```markdown
# Plan del ciclo

## Intención
1. **[entidad]** — qué se busca lograr.

## No entra (y por qué)
- **[entidad]** — razón explícita.

## Restricciones y contexto
- …

## Señales a vigilar
- …

<!-- tuku:derived id=tareas-del-ciclo hash=… -->
…tareas vigentes, postergadas y bloqueadas…
<!-- /tuku:derived -->
```

### 2.4 "No entra (y por qué)"

Sección obligatoria y no vacía. Declara el alcance **negativo** del ciclo con su
justificación.

Es lo que convierte un plan en un compromiso: sin ella, todo lo no hecho parece
incumplimiento. Con ella, el cierre distingue tres cosas —lo que se decidió no hacer, lo que
se intentó y no salió, y lo que se olvidó— y solo las dos últimas son desviaciones. Está en
uso en los ocho ciclos del corpus real, sin excepción. Si no hay nada excluido, el plan no
está acotado.

### 2.5 Insumos del sembrado

| Insumo | Aporta |
|---|---|
| `resultados_*` de los 3–4 ciclos anteriores | aprendizajes, desviaciones, momentum |
| `tareas/abiertas.md` | vigentes, postergadas al ciclo, bloqueadas, arrastre |
| Entidades vigentes con su `alineamiento` | qué está activo y qué persigue |
| `estrategia/capacidad.md` | límite contra el que se contrasta la intención |
| Cadencias vigentes | compromisos rítmicos que caen en el ciclo |

Sin las entidades vigentes y sus objetivos el cruce con capacidad es decorativo. Es el
insumo que más eleva la calidad del plan y el más fácil de omitir.

### 2.6 Delta de corrección

El motor registra la diferencia entre lo sembrado y lo que queda tras la corrección humana
en `<!-- tuku: seed_delta=… -->`. Cuesta cero capturarlo y es la única medida directa de qué
tan mal calibrado está el sembrado. Un delta grande y sostenido no es fallo del usuario: es
señal de revisar el proceso de apertura.

---

## 3. `resultados_*` — Cierre del ciclo

### 3.1 Estructura

```markdown
# Resultados del ciclo

## TL;DR
> Una o dos frases: carácter del ciclo y su saldo.

## Avances
## Desviaciones
## Aprendizajes
## Momentum y señales

<!-- tuku:derived id=bitacora-ciclo hash=… -->
…entradas del ciclo, congeladas…
<!-- /tuku:derived -->
```

### 3.2 Cómo se genera: filtro primero, redacción después

| Sección | Origen | Familia |
|---|---|---|
| Avances | entradas `Hito` + tareas completadas en el rango | derivación |
| Desviaciones | intención sin entradas asociadas · tareas del ciclo no cerradas · tareas con `cycles` sobre el umbral | derivación |
| Aprendizajes | entradas `Señal` y `Decisión` | derivación como insumo, redacción semántica |
| Momentum y señales | entradas `Señal` + entidades con actividad creciente o detenida | derivación como insumo, redacción semántica |

El agente **no busca** qué pasó: recibe un conjunto ya filtrado y lo redacta. Esa es la razón
por la que existen las clasificaciones de entrada, y lo que hace el cierre barato y
reproducible.

**Lo excluido en "No entra" nunca cuenta como desviación.** Es la regla que impide confundir
una decisión con un fracaso.

**Las tareas canceladas se listan aparte de las incumplidas**, con su razón.

### 3.3 Formato estable, obligatorio

El informe es la **memoria de largo plazo**: Markdown no es una base de datos y la consulta
histórica se responde por informes, no escaneando el detalle. Un informe pobre es memoria
perdida.

- **Front matter completo**, incluidas las entidades tocadas, para que un agente lo encuentre
  sin leerlo entero.
- **Encabezados fijos**: las cuatro secciones más el TL;DR no cambian de nombre ni de orden
  entre ciclos ni entre versiones del motor. Todo lo variable va en los informes por
  audiencia (§4).

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

### 3.4 Cierre del plan

El cierre marca `status: closed` en el `plan_*` del ciclo.

### 3.5 Bitácora del ciclo congelada

La proyección de las entradas del rango se genera **una vez, al cerrar**, y queda dentro de
`resultados_*` como zona derivada con su hash. Durante el ciclo no existe: quien quiera ver
"lo del ciclo" lo consulta en `entradas/`, filtrado por la interfaz.

Esto elimina la única zona donde el usuario podría haber escrito sobre una proyección.

---

## 4. Informes por audiencia

`resultados_*` tiene una audiencia: el propio usuario, en el ciclo siguiente. Otros informes
se generan **desde el mismo material** para audiencias distintas, con idioma, estructura y
detalle propios.

Caso observado: los ciclos de tipo `turno` producen un informe de fin de turno en inglés,
organizado por rol, destinado a colegas de la institución. Los de tipo `descanso` no.

### 4.1 Modelo

Un informe por audiencia es un **skill invocable** y opcionalmente una **cadencia asociada
al fin de un ciclo de cierto tipo**:

```yaml
reports:
  - id: fin-de-turno
    cycle_types: [turno]
    template: plantillas/fin-de-turno.md
    trigger: cycle_close        # o manual
    language: en
```

En ambos casos el resultado es **sembrado**.

### 4.2 Plantillas

La estructura de un informe por audiencia **va a cambiar** con el tiempo: depende de qué
espera quien lo lee. Por eso vive en una **plantilla editable del perfil**, no en el código.
Cambiar la forma del informe de fin de turno es editar un Markdown, no actualizar TUKU.

Las plantillas admiten marcadores de sección que el motor rellena con material ya filtrado
(§3.2): quien edita la plantilla decide **qué aparece y en qué orden**, sin describir cómo
obtenerlo.

### 4.3 Dónde viven

```
ciclos/informes/fin-de-turno_2026-06-30.md
plantillas/fin-de-turno.md
```

---

## 5. Apertura — orden de operaciones

1. Resolver el ciclo desde las cadencias, o tomar el `plan_*` que el usuario ya declaró.
2. Sembrar los encabezados de día del rango en `entradas/YYYY-MM.md`.
3. Incrementar `cycles` de las tareas abiertas.
4. Re-resolver las fechas relativas contra el calendario de planes.
5. Crear `plan_*` sembrado con los insumos de §2.5.
6. Renderizar las derivadas del plan.
7. Janitors de invariantes.
8. Commit semántico.

Los pasos 1–4 y 6–8 son deterministas y funcionan sin ningún modelo. Solo el 5 requiere
agente, y sin agente el plan se crea con los insumos listados y sin redacción. **El ciclo
abre igual sin conexión.**

---

## 6. Cierre — orden de operaciones

1. Recoger marcas de completitud dejadas en proyecciones y propagarlas al canónico.
2. Calcular los conjuntos de §3.2.
3. Crear `resultados_*` sembrado, con la bitácora del ciclo congelada.
4. Generar los informes por audiencia con `trigger: cycle_close`.
5. Marcar `status: closed` en el plan.
6. Archivar tareas cuyo plazo de retención venció; archivar meses cerrados de `entradas/`.
7. Janitors e invariantes.
8. Commit semántico.

---

## 7. Invariantes

| # | Regla | Garante |
|---|---|---|
| C1 | Plan y resultados de un ciclo comparten `cycle_start` y `cycle_type` | janitor |
| C2 | No se solapan dos ciclos del **mismo** `cycle_type` | janitor |
| C3 | Ciclos de tipos distintos **sí** pueden solaparse | — |
| C4 | Un ciclo cerrado tiene plan y resultados | janitor |
| C5 | `plan_*` tiene "No entra" no vacío | janitor |
| C6 | Un artefacto sembrado no se regenera tras la corrección humana | janitor de build |
| C7 | Los encabezados de `resultados_*` son los de §3.1 | janitor |
| C8 | Todo día sembrado en `entradas/` cae en el rango de algún plan | janitor (advertencia, no error) |

C3 es deliberado: una misión dentro de un turno, o un ciclo mensual de finanzas sobre los
turnos, son casos legítimos. Como las entradas viven en `entradas/` y no bajo el ciclo, el
solapamiento no duplica nada: son dos filtros sobre el mismo conjunto.

---

## 8. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | Resumen anual: ¿derivado puro que concatena `resultados_*`, o artefacto sembrado propio? |
| 2 | Sintaxis exacta de los marcadores de sección en las plantillas de informe |
| 3 | Si un ciclo puede declararse sin plan sembrado —solo front matter— para casos triviales |
