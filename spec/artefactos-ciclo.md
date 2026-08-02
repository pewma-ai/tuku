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
├── plan_2026-08-10_viaje.md
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
id: plan-2026-08-10-viaje
type: plan
cycle_type: viaje           # string libre
place: Santiago             # opcional
parent_cycle: plan-2026-08-03-semana    # opcional; si existe, es un plan anidado
cycle_start: 2026-08-10
cycle_end: 2026-08-16
status: open                # open | closed
created: 2026-08-09
modified: 2026-08-10
seeded_by: tuku 0.4.2+g27b3aed / deepseek-v4-flash
---
```

`cycle_type` es **string libre**: `turno`, `descanso`, `vacaciones`, `mision`, `viaje`. Es
P6 aplicado al eje temporal — los modos de vida de una persona no son anticipables y no
tienen por qué serlo.

### 2.2 El conjunto de planes es el calendario

Los archivos `plan_*` —pasados y futuros— **son** el calendario de ciclos del usuario. De
ahí se siguen tres cosas:

- Las cadencias **proponen** ciclos y siembran sus planes; el archivo de plan es la verdad.
- `(next:turno)` y sus formas se resuelven contra este conjunto (`spec/tarea.md` §4.1).
- **Romper la cadencia es normal, no excepcional.** Si la próxima semana el usuario trabaja
  desde otra ciudad, crea `plan_2026-08-10_viaje.md`; las tareas postergadas al próximo
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
…tareas vigentes de este ciclo…
<!-- /tuku:derived -->
```

En el bloque derivado `tareas-del-ciclo`, las tareas se proyectan mostrando el texto y enlazando al canónico con anchor de Obsidian:

```markdown
- [ ] [Enviar correo de postulación conjunta](../tareas/tareas.md#^t-2026-0087) ⟳7
```

### 2.4 "No entra (y por qué)"

Sección obligatoria y no vacía. Declara el alcance **negativo** del ciclo con su justificación.

Es lo que convierte un plan en un compromiso: sin ella, todo lo no hecho parece incumplimiento. Con ella, el cierre distingue tres cosas —lo que se decidió no hacer, lo que se intentó y no salió, y lo que se olvidó— y solo las dos últimas son desviaciones. Está en uso en los ocho ciclos del corpus real, sin excepción. Si no hay nada excluido, el plan no está acotado.

Cuando el usuario mueve una entidad a "No entra" al corregir el plan, el motor **resuelve en ese momento**, no después: aplica §4.1 de `spec/entidad.md` (bloquea la entidad hasta el cierre del ciclo) y pregunta qué hacer con las tareas vigentes de esa entidad para este ciclo — postergarlas al mismo `cycle_type` siguiente es la opción por defecto. Esto reemplaza cualquier mecanismo de detección posterior: la consecuencia se decide al mismo tiempo que la exclusión.

### 2.5 Insumos del sembrado

| Insumo | Aporta |
|---|---|
| `resultados_*` de los 3–4 ciclos anteriores | aprendizajes, desviaciones, momentum |
| `tareas/tareas.md` | vigentes, postergadas al ciclo, bloqueadas, arrastre |
| Entidades vigentes con su `alineamiento` | qué está activo y qué persigue |
| `estrategia/capacidad.md` | límite contra el que se contrasta la intención |
| Cadencias vigentes | compromisos rítmicos que caen en el ciclo |

Sin las entidades vigentes y sus objetivos el cruce con capacidad es decorativo. Es el insumo que más eleva la calidad del plan y el más fácil de omitir.

### 2.6 Delta de corrección

El motor registra la diferencia entre lo sembrado y lo que queda tras la corrección humana en `<!-- tuku: seed_delta=… -->`. Cuesta cero capturarlo y es la única medida directa de qué tan mal calibrado está el sembrado. Un delta grande y sostenido no es fallo del usuario: es señal de revisar el proceso de apertura.

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

### 3.2 Cómo se genera: alcance por entidad, no solo por filtro

El alcance evaluable de un cierre es la unión de dos conjuntos: las entidades declaradas en la Intención del plan, y las entidades que efectivamente registraron entradas durante el ciclo, aunque no estuvieran planeadas. **Lo declarado en "No entra" y lo no tocado ni declarado quedan fuera: no se evalúan.**

Para cada entidad del alcance, el agente contrasta qué debería haber pasado —inferido de su `alineamiento`, de su descripción inferida (el modelo ligero de cómo opera esa entidad, `spec/entidad.md` §3.3) y de sus cadencias vigentes— contra lo que efectivamente pasó, leído de sus entradas y del estado de sus tareas. **Es una tarea cognitivamente compleja**: se hace como la haría un especialista de ese dominio, no como un filtro mecánico. Donde una clasificación basta (Hito → Avance), se usa el filtro simple de la tabla siguiente; donde hace falta juicio —¿esto era lo esperado? ¿esto es una desviación real o una decisión ya tomada?— el agente lo resuelve con ese contraste.

| Sección | Origen | Familia |
|---|---|---|
| Avances | entradas `Hito` + tareas completadas + contraste por entidad | derivación + juicio |
| Desviaciones | intención sin correspondencia + arrastre sobre umbral + contraste por entidad | derivación + juicio |
| Aprendizajes | entradas `Señal`/`Decisión` + lo que el contraste revela | juicio |
| Momentum y señales | señales + entidades con actividad anómala | derivación + juicio |

**Curiosidad acotada.** Si el contraste revela algo que sorprendería a un especialista del dominio —una tarea que se destraba tras arrastre extremo, una desviación mayor, una contradicción entre lo declarado y lo ocurrido— el agente lo señala explícitamente, con como máximo una pregunta puntual para capturar la explicación. No es interrogatorio: es la misma alarma que notaría un humano responsable ante algo genuinamente fuera de lo esperado.

**Lo excluido en "No entra" nunca cuenta como desviación.** Es la regla que impide confundir una decisión con un fracaso.

**Las tareas canceladas se listan aparte de las incumplidas**, con su razón.

> En la simulación de un perfil comercial, el aprendizaje más útil del ciclo —el atraso de un proveedor propagándose a un compromiso con cliente— **no provino de ninguna clasificación**. Ninguna entrada estaba marcada. Salió del contraste por entidad entre lo esperado y lo registrado. Es la evidencia de por qué no existe una clasificación de fricción: **la fricción no se declara, se descubre.**

**Ciclo sin Intención declarada.** El mecanismo de Desviaciones asume un plan previo, que no existe en el primer ciclo de un perfil nuevo. En ese caso el cierre **omite Desviaciones** y en su lugar propone la Intención del ciclo siguiente a partir de lo observado. El primer cierre no evalúa: **arranca el ciclo de gestión.**

### 3.6 Planes anidados

Un plan con `parent_cycle` es **anidado**. Al cerrarse:

- **No genera `resultados_*` propio.** Sus avances, desviaciones y aprendizajes se integran como material del cierre de su contenedor.
- Sus entradas ya pertenecen al contenedor por rango de fechas: no hay duplicación ni doble narración, porque las entradas no viven bajo el ciclo.
- Si el anidado termina **después** que su contenedor, el contenedor cierra igual con lo ocurrido hasta su propia fecha; el resto cae en el ciclo siguiente. Nada se pierde.

**Solo hay un cierre completo por ciclo raíz.** Un anidado que necesite informe propio es un caso de informe por audiencia (§4), no un cierre.

---

## 4. Informes por audiencia

`resultados_*` tiene una audiencia: el propio usuario, en el ciclo siguiente. Otros informes se generan **desde el mismo material** para audiencias distintas, con idioma, estructura y detalle propios.

Caso observado: los ciclos de tipo `turno` producen un informe de fin de turno en inglés, organizado por rol, destinado a colegas de la institución. Los de tipo `descanso` no.

### 4.1 Modelo

Un informe por audiencia es un **skill invocable** y opcionalmente una **cadencia asociada al fin de un ciclo de cierto tipo**:

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

La estructura de un informe por audiencia **va a cambiar** con el tiempo: depende de qué espera quien lo lee. Por eso vive en una **plantilla editable del perfil**, no en el código. Cambiar la forma del informe de fin de turno es editar un Markdown, no actualizar TUKU.

Las plantillas admiten marcadores de sección que el motor rellena con material ya filtrado (§3.2): quien edita la plantilla decide **qué aparece y en qué orden**, sin describir cómo obtenerlo.

### 4.3 Dónde viven

```
ciclos/informes/fin-de-turno_2026-06-30.md
plantillas/fin-de-turno.md
```

---

## 5. Apertura — orden de operaciones

1. Resolver el ciclo desde las cadencias, o tomar el `plan_*` que el usuario ya declaró.
2. Incrementar `cycles` de las tareas abiertas.
3. Re-resolver las fechas relativas contra el calendario de planes.
4. Crear `plan_*` sembrado con los insumos de §2.5.
5. Renderizar las derivadas del plan.
6. Janitors de invariantes.
7. Commit semántico.

Los pasos 1–3 y 5–7 son deterministas y funcionan sin ningún modelo. Solo el 4 requiere agente, y sin agente el plan se crea con los insumos listados y sin redacción. **El ciclo abre igual sin conexión.**

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
| C2 | Dos ciclos del mismo `cycle_type` no se solapan, y un plan anidado no puede tener el mismo `cycle_type` que su padre | janitor |
| C3 | Ciclos de tipos distintos **sí** pueden solaparse | — |
| C4 | Un ciclo cerrado tiene plan y resultados | janitor |
| C5 | `plan_*` tiene "No entra" no vacío (salvo el primer ciclo de un perfil nuevo sin plan sembrado) | janitor |
| C6 | Un artefacto sembrado no se regenera tras la corrección humana | janitor de build |
| C7 | Los encabezados de `resultados_*` son los de §3.1 | janitor |

C3 es deliberado: una misión dentro de un turno, o un ciclo mensual de finanzas sobre los turnos, son casos legítimos. Como las entradas viven en `entradas/` y no bajo el ciclo, el solapamiento no duplica nada: son dos filtros sobre el mismo conjunto.

---

## 8. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | Resumen anual: ¿derivado puro que concatena `resultados_*`, o artefacto sembrado propio? |
| 2 | Sintaxis exacta de los marcadores de sección en las plantillas de informe |
| 3 | Si un ciclo puede declararse sin plan sembrado —solo front matter— para casos triviales |
