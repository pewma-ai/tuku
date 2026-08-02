# docs/ — Cómo leer esta documentación

Este directorio contiene el **porqué** de TUKU. El **qué** exacto de cada formato vive en
[`../spec/`](../spec/), y el **cómo** del código vive en `../src/`.

La regla que ordena todo: cada documento se justifica por referencia a los anteriores. Si
algo no puede derivarse de lo que está aguas arriba, o falta una premisa o hay un error.

---

## Orden de lectura

| # | Documento | Qué contiene | Léelo si… |
|---|---|---|---|
| 1 | [`brief.md`](brief.md) | Qué es TUKU, para quién, el modelo conceptual, los principios y los criterios de éxito | …quieres entender el proyecto. Es el documento fundacional |
| 2 | [`principios.md`](principios.md) | Los seis principios de diseño desarrollados: implicaciones, cómo se violan, cómo se verifican | …vas a tomar una decisión de diseño |
| 3 | [`arquitectura.md`](arquitectura.md) | La forma del sistema: motor y perfil, canónico y proyección, grafo de derivaciones, coherencia | …vas a escribir código o specs |
| 4 | [`deployment.md`](deployment.md) | Instalación, `~/.tuku/`, versionado de esquema, migraciones, camino a servidor | …vas a instalar, empaquetar o desplegar |
| 5 | [`glosario.md`](glosario.md) | Vocabulario preciso del proyecto | …dudas de un término. Consúltalo en cualquier momento |
| 6 | [`decisiones/`](decisiones/) | ADR: decisiones tomadas, con su contexto y sus consecuencias | …quieres saber por qué algo es como es |

Lectura mínima para contribuir: **brief → principios → arquitectura**. Lo demás es
consulta.

---

## Qué va en cada lugar

| Si estás escribiendo… | Va en… |
|---|---|
| Una razón, una intención, un principio | `docs/` |
| El formato exacto de un archivo o campo | [`../spec/`](../spec/) — ver su [README](../spec/README.md) |
| Una decisión que cerró una alternativa viable | `docs/decisiones/NNNN-titulo.md` |
| Instrucciones ejecutables por humano o agente | `src/tuku/procesos/` |
| Lo que se siembra en el perfil de un usuario | `src/tuku/templates/` |

**No dupliques.** Si un formato aparece en `spec/`, `docs/` lo menciona y enlaza, no lo
repite. La duplicación en documentación se desincroniza igual que en código.

---

## Decisiones (ADR)

Un ADR se escribe cuando una decisión **cierra una alternativa que era viable**. El índice
de las decisiones tomadas está en [`decisiones/`](decisiones/); cómo se escribe una, en
[`decisiones/INSTRUCCIONES.md`](decisiones/INSTRUCCIONES.md).

Las decisiones que aún **no** se toman no viven ahí: viven como issues o en la sección
correspondiente de [`arquitectura.md`](arquitectura.md), marcadas como abiertas.

---

## Idioma

Toda la documentación en español. El código, los nombres de campos de front matter y los
identificadores internos en inglés. Los nombres de las primitivas del dominio —entrada,
tarea, entidad, cadencia, ciclo— en español, tanto en documentación como en la interfaz
que ve el usuario.
