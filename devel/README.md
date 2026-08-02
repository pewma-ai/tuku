# devel/ — Cómo se construye TUKU

> `devel/README.md` · Punto de entrada para quien —persona o agente— va a escribir código.
> El **porqué** vive en [`../docs/`](../docs/), el **qué exacto** en [`../spec/`](../spec/),
> y las decisiones cerradas en [`../docs/decisiones/`](../docs/decisiones/).

---

## Los cuatro documentos

| Documento | Responde | Cuándo se lee |
|---|---|---|
| [`entorno-devel.md`](entorno-devel.md) | Cómo se ejecuta y se verifica | antes del primer comando |
| [`plan-implementacion.md`](plan-implementacion.md) | Por qué las fases van en ese orden | una vez, al empezar |
| [`checklist-implementacion.md`](checklist-implementacion.md) | Qué toca ahora y cómo se comprueba | en cada sesión de trabajo |
| [`../tests/README.md`](../tests/README.md) | Cómo se prueba lo que se escribe | al escribir cualquier test |

Si solo vas a leer uno, lee el **checklist**: cada ítem enlaza a su spec y declara su
verificación. El plan explica el porqué del orden; el checklist es el orden.

---

## El contrato de este repositorio

TUKU se construye **spec-driven**. La consecuencia práctica, y es dura:

> El código en `src/` no inventa reglas. Implementa lo que dice `spec/`, y cuando código y
> spec discrepan, **el defecto está en el código** — salvo que la spec no se derive de
> `docs/arquitectura.md`, en cuyo caso el defecto está en la spec.

Nadie debería escribir una función cuyo comportamiento no esté escrito antes en `spec/`. Si
al implementar aparece un caso que la spec no cubre, el paso correcto **no** es decidirlo en
el código: es abrir una decisión en la spec, y si descarta una alternativa viable, un
[ADR](../docs/decisiones/INSTRUCCIONES.md).

Este contrato existe porque el desarrollo es asistido por LLM. Un agente al que se le pide
"implementa el parser de tareas" rellenará con plausibilidad cualquier hueco que encuentre, y
lo hará con una prosa convincente. La spec es lo que convierte esa plausibilidad en algo
verificable.

---

## Arranque en frío y prueba local

```bash
uv venv && uv pip install -e ".[dev]"
uv run pytest          # suite determinista
uv run ruff check .
uv run mypy src
```

### Probar el CLI manualmente

```bash
uv run tuku --help                        # ayuda general
uv run tuku init /tmp/mi-perfil           # sembrar perfil de prueba
uv run tuku -p /tmp/mi-perfil doctor      # verificar salud del perfil
uv run tuku -p /tmp/mi-perfil sync        # sincronizar assets
```

O instalar en el sistema para usar `tuku` directo: `pipx install -e . --force`.

---

## Reglas que no se negocian

1. **Nada de LLM en F0–F4.** Parsers, janitors, derivaciones, cadencias y CLI se prueban con
   `pytest` determinista. Un test que necesite un modelo para pasar en esas fases señala
   agencia mal ubicada (P3), no falta de modelo.
2. **Round-trip exacto.** Leer un archivo canónico y volver a escribirlo no cambia un byte.
   No es purismo: los ADR 0013 y 0014 ponen datos canónicos dentro de comentarios HTML, así
   que un serializador descuidado destruye información real.
3. **Ningún test toca datos reales.** Todo perfil de prueba vive en `tmp_path`.
4. **Los tests agénticos no corren por defecto.** Van marcados `agentic` y se excluyen salvo
   que se pidan explícitamente.
5. **Una invariante nueva en una spec exige test o entrada en `PENDIENTES`.** La suite lo
   comprueba sola; no depende de que alguien se acuerde.

---

## Para agentes de codificación

Antes de tocar `src/`:

1. Lee la spec del artefacto que vas a implementar, entera. Son cortas.
2. Busca en [`../docs/decisiones/`](../docs/decisiones/) si el punto ya está cerrado. Varias
   decisiones descartan explícitamente el camino que parece más obvio —el ADR 0016 se
   implementa **no** construyendo transclusión, el 0008 **no** declarando `parent`.
3. Escribe el test antes que el código, tomándolo del ejemplo normativo de la spec.
4. Si algo no está especificado, **pregunta o escribe la spec**; no lo resuelvas en el código.

Lo que nunca debe hacerse: ampliar el alcance de una fase porque "ya que estamos". El orden
de las fases no es una preferencia estética, está justificado en el plan §1.1.
