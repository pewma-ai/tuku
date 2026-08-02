# spec/proceso.md — Procesos y sus instancias

> Define el trabajo recurrente y estructurado: una plantilla de pasos que se instancia sobre
> una entidad y produce un grupo de tareas relacionadas.
> Depende de [`spec/tarea.md`](tarea.md) y [`spec/cadencia.md`](cadencia.md).

---

## 1. Definición

**Proceso** — Plantilla de trabajo estándar: varios pasos conocidos, orden parcial,
iteraciones esperadas, un resultado. Cotizar, contratar, publicar un artículo, resolver un
cambio de configuración.

**Instancia** — La aplicación de esa plantilla a un caso concreto: *la* cotización al
Colegio San Marcos, *la* contratación de agosto.

### 1.1 Por qué hace falta

Hay objetos de negocio que **no son ni tarea ni entidad**. Una cotización tiene estados
propios —enviada, ajustada, aceptada—, iteraciones que son el mayor punto de fricción de la
operación, y un ciclo de vida de días. Modelarla como tarea colapsa el objeto con la acción;
como entidad, llena el árbol de cosas efímeras que nacen y mueren cada semana.

**No se agrega una primitiva de almacenamiento.** Una instancia de proceso no tiene archivo
propio ni estado guardado: **es un grupo de tareas relacionadas**, y su estado es qué tareas
del grupo siguen abiertas. Toda la información ya está en `tareas/tareas.md`; lo único nuevo
es el vínculo que las agrupa.

### 1.2 Qué gana el sistema

El proceso se vuelve **medible sin instrumentación adicional**: cuántas iteraciones tuvo cada
cotización, cuánto tardó cada paso, dónde se atasca siempre. Es diagnóstico operacional que
sale gratis del mismo registro.

---

## 2. La plantilla

Vive junto a los demás procesos del perfil o del motor, en Markdown ejecutable por un humano
disciplinado o por un agente de inteligencia media (P2). La parte declarativa va en
comentario canónico, igual que las cadencias:

```markdown
<!-- procesos/cotizacion.md -->
---
id: proc-cotizacion
type: proceso
ambito: negocio
applies_to: [cliente]        # tipos de entidad sobre los que se puede instanciar
---
# Cotización

<!-- tuku:proceso
prefix: cot
steps:
  - id: precios
    text: "Pedir precios a proveedores"
    effort: 1h
  - id: armar
    text: "Armar el documento de cotización"
    effort: 1h
    deps: [precios]
  - id: enviar
    text: "Enviar la cotización"
    effort: 0.5h
    deps: [armar]
  - id: seguimiento
    text: "Revisar si respondieron"
    effort: 0.5h
    deps: [enviar]
    followup: "+2d"
  - id: ajuste
    text: "Ajustar la cotización según observaciones"
    effort: 0.5h
    deps: [enviar]
    repeatable: true          # cero o más veces
  - id: cierre
    text: "Cerrar: aceptada o rechazada"
    effort: 0.5h
    deps: [enviar]
    closes_instance: true
-->

## Cómo se hace a mano
1. Pedir precios a los proveedores del rubro correspondiente.
2. Armar el documento con los márgenes vigentes.
3. Enviar y anotar la fecha.
4. Si el cliente pide cambios, repetir el ajuste tantas veces como haga falta.
5. Cerrar registrando el resultado.
```

El cuerpo en prosa **no es decoración**: es la versión operable a mano del mismo proceso, y
lo que permite ejecutarlo sin agente (P2).

### 2.1 Campos de un paso

| Campo | Obligatorio | Notas |
|---|---|---|
| `id` | sí | único dentro de la plantilla |
| `text` | sí | se convierte en el texto de la tarea |
| `effort` | no | por defecto `1h`, como toda tarea |
| `deps` | no | ids de pasos previos del mismo proceso |
| `followup` | no | desfase relativo, se resuelve al instanciar |
| `repeatable` | no | el paso puede emitirse varias veces (§4) |
| `closes_instance` | no | al completarse, la instancia termina |

---

## 3. Instanciación

```
tuku proceso cotizacion --entidad colegio-san-marcos
```

o, en la práctica, conversando: *"hazme una cotización para el Colegio San Marcos"*.

El motor:

1. Asigna un identificador de instancia: `<prefix>-NNNN` → `cot-0042`.
2. Emite **todas** las tareas del grupo, con `entity` = la entidad destino.
3. Traduce `deps` de pasos a `deps` entre `id` de tareas concretas.
4. Escribe `process` y `step` en el comentario de cada tarea.

```markdown
- [ ] 2026-08-04 1h colegio-san-marcos - - - proc-cotizacion Pedir precios a proveedores ^t-2026-0101
      <!-- tuku: process=cot-0042 step=precios -->
- [ ] 2026-08-04 1h colegio-san-marcos - - - proc-cotizacion Armar el documento de cotización ^t-2026-0102
      <!-- tuku: process=cot-0042 step=armar deps=t-2026-0101 -->
- [ ] 2026-08-04 0.5h colegio-san-marcos - - - proc-cotizacion Enviar la cotización ^t-2026-0103
      <!-- tuku: process=cot-0042 step=enviar deps=t-2026-0102 -->
```

`originator` es el `id` del proceso, igual que sería el `id` de una cadencia. Un `originator`
colgante no viola invariantes: **la regla muere, lo emitido sobrevive**
(`spec/entidad.md` §6.1).

**Las tareas bloqueadas por `deps` no aparecen como accionables** en el plan del ciclo
(`spec/tarea.md` §5). Una instancia recién creada muestra un solo pendiente real, no cinco.

---

## 4. Pasos repetibles

`repeatable: true` es lo que distingue un proceso real de una lista de pasos. La iteración de
ajustes no ocurre un número conocido de veces: ocurre las que el cliente pida.

- El paso repetible **no se emite** en la instanciación inicial.
- Se emite cuando algo lo dispara: el usuario lo pide, o una entrada con el marcador
  correspondiente lo activa.
- Cada emisión lleva sufijo: `step=ajuste#1`, `step=ajuste#2`.
- El conteo de repeticiones es exactamente la métrica de fricción del proceso.

---

## 5. Estado y cierre

**No hay campo de estado.** El estado de una instancia se deduce:

| Situación | Estado |
|---|---|
| Hay tareas abiertas del grupo | en curso |
| Se completó un paso `closes_instance` | terminada |
| Todas cerradas sin `closes_instance` | terminada por agotamiento |
| Todas con `outcome` distinto de `done` | abandonada |

Al completarse un paso con `closes_instance`, el motor resuelve las tareas restantes del
grupo con `outcome=superseded` y razón *"instancia cerrada en el paso <id>"*. Los pasos
repetibles no emitidos simplemente no existen.

---

## 6. Relación con cadencias

Una cadencia puede instanciar un proceso: `emit: { kind: proceso, proceso: proc-cotizacion }`.

Ejemplo: *cada renovación anual de contrato, iniciar el proceso de propuesta*. Se aplican las
mismas reglas de emisión —idempotencia por ocurrencia, `origin` blando, no recuperar
disparos perdidos— sin excepción.

---

## 7. Qué NO es un proceso

- **Una tarea con subtareas.** Si los pasos no se repiten entre casos, es una tarea con
  `deps`, no un proceso. El proceso se justifica por la **plantilla reutilizable**.
- **Un ciclo.** Un ciclo es temporal y contiene todo lo que pasa en un período; un proceso es
  un trabajo concreto sobre una entidad y puede cruzar varios ciclos.
- **Una entidad.** No tiene página, ni bitácora, ni cadencias propias. Si necesita todo eso,
  probablemente sea un proyecto y merece ser entidad.

---

## 8. Invariantes

| # | Regla | Garante |
|---|---|---|
| P1 | Todo `process` referencia una instancia con al menos una tarea | janitor |
| P2 | `step` pertenece a la plantilla del proceso indicado en `originator` | janitor |
| P3 | El grafo de `deps` dentro de una instancia es acíclico | janitor |
| P4 | Una plantilla solo se instancia sobre tipos declarados en `applies_to` | janitor |
| P5 | Un `originator` de proceso colgante **no** es violación | — |
| P6 | Toda plantilla tiene cuerpo en prosa ejecutable a mano | janitor (advertencia) |

---

## 9. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | Cómo se dispara un paso `repeatable`: ¿solo a pedido, o también por marcador en una entrada? |
| 2 | Si una instancia puede cambiar de entidad destino a mitad de camino |
| 3 | Si conviene una proyección "instancias en curso" por entidad, o basta con agrupar las tareas por `process` en la vista existente |
| 4 | Métricas de proceso —iteraciones, duración por paso— ¿son RADAR, informe de cierre, o ninguna de las dos por ahora? |
