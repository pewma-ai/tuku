# Checklist de Implementación (Spec-Driven Development)

> `devel/checklist-implementacion.md` · Lista de control trazable, fase por fase. El porqué
> del orden está en [`plan-implementacion.md`](plan-implementacion.md) §1.1; cómo se ejecuta,
> en [`../../entorno-devel.md`](entorno-devel.md).

---

## Cómo se usa

Cada ítem declara tres cosas: **qué** se implementa, **de dónde sale** la regla (spec o ADR),
y **cómo se verifica**. Un ítem sin verificación no se marca como hecho.

La columna *Verificación* nombra el test que debe existir. Esa es la definición de terminado:

> **Definición de terminado.** El código existe, su test existe y nombra la regla que
> comprueba, `uv run pytest` pasa en verde, `ruff` y `mypy` no protestan, y ningún ítem
> posterior tuvo que modificarse para acomodarlo.

Antes de marcar cualquier casilla de F1 en adelante, los tres **bloqueantes** de abajo deben
estar cerrados.

---

## 🚧 Bloqueantes — antes de F1

Consolidación de decisiones ya tomadas y dispersas. Ninguno exige diseño nuevo.

- [x] **B1** Escribir [`spec/frontmatter.md`](../../../spec/frontmatter.md) (creado ligero y compatible con `spec/*`).
      *Verificación:* `test_frontmatter_campos_minimos` pasa ✅.
- [x] **B2** Completar [`spec/perfil.md`](../../../spec/perfil.md) con el formato real de `.tuku/config.yaml`.
      *Verificación:* `test_config_perfil_valida` pasa ✅.
- [x] **B3** Resolver la **colisión del prefijo `P`** entre `proceso.md` y `perfil.md` (resuelto: `spec/proceso.md` usa `R1`–`R6`).
      *Verificación:* `test_prefijos_de_invariante_no_colisionan` pasa ✅.

---

## 🏗️ Fase 0 — Cimientos y tooling

| | Ítem | Fuente | Verificación |
|---|---|---|---|
| [x] | **F0.1** `pyproject.toml` con `uv`, `pytest`, `ruff`, `mypy` | — | `uv run pytest` arranca ✅ *hecho* |
| [x] | **F0.2** `core/config.py`: lee `.tuku/config.yaml`, valida `schema_version` | [ADR 0003](../../../docs/decisiones/0003-version-de-esquema.md), B2 | esquema fuera de rango → error claro, no traceback ✅ *hecho* |
| [x] | **F0.3** `tuku init`: árbol de directorios + `.gitignore` con `tuku.log` y `.tuku/cache/` | [ADR 0015](../../../docs/decisiones/0015-tuku-log-no-versionado.md) | `tuku init` + `git status` limpio; `notas/` sembrado con índice y `AGENTS.md` ✅ *hecho* |
| [x] | **F0.4** `tuku sync`: punteros a procesos y `AGENTS.md` por nivel | [ADR 0002](../../../docs/decisiones/0002-motor-fuera-del-perfil.md) | idempotente: dos corridas → diff cero ✅ *hecho* |
| [x] | **F0.5** `tuku doctor`: versión, commit, rama, validación de perfil | `deployment.md` §2.3 | reporta commit real, no `unknown` ✅ *hecho* |
| [x] | **F0.6** Verificación de ayuda CLI (`tuku --help`) | `deployment.md` §2 | test automatizado verifica ayuda y descripción por cada subcomando ✅ *hecho* |

> **Por qué `init` va antes que todo:** casi toda la suite depende de la fixture `perfil_tmp`,
> que llama a `tuku init`. Mientras no exista, los tests de F1–F4 se saltan solos (`skip`) en
> vez de fallar. Ese `skip` masivo es el indicador de que F0 no está cerrada.

---

## 🔤 Fase 1 — Parsers y serializadores (round-trip exacto)

| | Ítem | Fuente | Verificación |
|---|---|---|---|
| [x] | **F1.1** Front matter YAML | B1 | round-trip byte a byte, incluido el orden de claves ✅ *hecho* |
| [x] | **F1.2** Línea posicional de tareas | [ADR 0014](../../../docs/decisiones/0014-formato-posicional-tareas.md), [`tarea.md`](../../../spec/tarea.md) | cada campo por separado + placeholder `-` obligatorio ✅ *hecho* |
| [x] | **F1.3** Entradas: hora opcional, `[entidad](ruta)`, clasificación, `#marcadores` | [`entradas.md`](../../../spec/entradas.md) | los cuatro valores de clasificación y ninguno más ✅ *hecho* |
| [x] | **F1.4** Gramática temporal: precisa, rango, difusa, `next:<tipo>` | [`tarea.md`](../../../spec/tarea.md) §4 | una fecha inválida se rechaza con posición ✅ *hecho* |
| [x] | **F1.5** Delimitadores HTML (`tuku:editable`, `tuku:derived`, `tuku:cadencias`) | [ADR 0013](../../../docs/decisiones/0013-cadencias-en-comentario.md) | comentario preservado íntegro tras reescribir ✅ *hecho* |
| [x] | **F1.6** Round-trip sobre **todos** los ejemplos normativos de `spec/` | [`spec/README.md`](devel/VAULT/spec/README.md) | `test_roundtrip.py` parametrizado por `specref.casos()` ✅ *hecho* |

> **La asimetría que hay que tener presente antes de escribir una línea.** En el canónico de
> tareas la entidad es un **`id` plano** (`nucleo-datos`); en las entradas es un **enlace
> Markdown** (`[nucleo-datos](../entidades/...)`). Son dos parsers con reglas distintas para
> el mismo concepto. No unificarlos por instinto: cada forma está justificada en su spec.

> **El round-trip no es purismo.** Los ADR 0013 y 0014 guardan datos canónicos dentro de
> comentarios HTML. Un serializador que "normaliza" espacios destruye información real.

---

## 🛡️ Fase 2 — Janitors e invariantes

Un test por invariante, con el nombre `test_<ID>_<qué_viola>`. El test **viola la invariante
a propósito** y exige que el janitor la detecte.

| | Ítem | Invariantes | Spec |
|---|---|---|---|
| [x] | **F2.1** Entidad | N1–N9 | [`entidad.md`](../../../spec/entidad.md) ✅ *hecho* |
| [x] | **F2.2** Entradas | E1–E7 | [`entradas.md`](../../../spec/entradas.md) ✅ *hecho* |
| [x] | **F2.3** Tarea | T1–T8 | [`tarea.md`](../../../spec/tarea.md) ✅ *hecho* |
| [x] | **F2.4** Cadencia | K1–K6, K8, K9 | [`cadencia.md`](../../../spec/cadencia.md) ✅ *hecho* |
| [x] | **F2.5** Ciclo | C1, C2, C4–C7 | [`artefactos-ciclo.md`](../../../spec/artefactos-ciclo.md) ✅ *hecho* |
| [x] | **F2.6** Proceso | P1–P4, P6 | [`proceso.md`](../../../spec/proceso.md) ✅ *hecho* |
| [x] | **F2.7** Nota | O1–O8 | [`nota.md`](../../../spec/nota.md) ✅ *hecho* |
| [x] | **F2.8** Perfil | F1, F2 | [`perfil.md`](../../../spec/perfil.md) ✅ *hecho* |
| [x] | **F2.9** CLI `tuku janitor [--fix]` | — | **idempotente**: dos corridas seguidas → diff cero ✅ *hecho* |

> K7, C3 y P5 no llevan test: son invariantes **negativas** (declaran que algo *no* es
> violación) y su garante es `—`. La suite las excluye sola.

Marcar cada invariante implementada borrando su entrada de `PENDIENTES` en
[`../tests/test_cobertura_specs.py`](test_cobertura_specs.py). Si se olvida, el test
`test_la_lista_de_pendientes_no_miente` avisa.

---

## 📊 Fase 3 — Grafo de derivaciones y builders

| | Ítem | Fuente | Verificación |
|---|---|---|---|
| [x] | **F3.1** Grafo en `config.yaml` + chequeo de aciclicidad | B2 | un ciclo declarado → error al arrancar, no en mitad del build ✅ *hecho* |
| [x] | **F3.2** Builder `bitacora_entidad` | [`entradas.md`](../../../spec/entradas.md) | borrar derivadas y regenerar → **diff cero** ✅ *hecho* |
| [x] | **F3.3** Builder `tareas_del_ciclo` | [`tarea.md`](../../../spec/tarea.md) | ídem ✅ *hecho* |
| [x] | **F3.4** Builder `cadencias-legibles` | [`cadencia.md`](../../../spec/cadencia.md) | ídem ✅ *hecho* |
| [x] | **F3.5** Builders `indice_notas` y `notas_entidad` | [`nota.md`](../../../spec/nota.md) O8 | ídem ✅ *hecho* |
| [x] | **F3.6** Hash de fuentes y detección de divergencia | [ADR 0005](../../../docs/decisiones/0005-derivadas-no-readonly.md) | editar a mano una zona derivada → el motor pregunta, no sobrescribe ✅ *hecho* |
| [x] | **F3.7** Build sobre diff (recomputación incremental) | — | mismo resultado que el build completo ✅ *hecho* |

> **La trampa que el propio ADR 0005 advierte.** Si el hash se calcula sobre bytes crudos, un
> cambio de formato dispara la pregunta de divergencia en todos los perfiles a la vez. La
> consecuencia: **la función de normalización es parte del contrato de esquema**, y cambiarla
> es una migración ([ADR 0003](../../../docs/decisiones/0003-version-de-esquema.md)), no un refactor.

---

## ⏱️ Fase 4 — Cadencias, ciclos, procesos y RADAR

| | Ítem | Fuente | Verificación |
|---|---|---|---|
| [x] | **F4.1** Colector con cache `.tuku/cache/cadencias-resueltas.yaml` | [`cadencia.md`](../../../spec/cadencia.md) §3.1 | borrar el cache y regenerar → idéntico ✅ *hecho* |
| [x] | **F4.2** Evaluador de disparos: `calendar`, `event`, `absence`, `completion` | [`cadencia.md`](../../../spec/cadencia.md) §5 | con `TZ=UTC` y fecha inyectada, nunca `date.today()` ✅ *hecho* |
| [x] | **F4.3** Registro de ocurrencias (idempotencia K4) | K4 | correr dos veces el mismo día no emite dos veces ✅ *hecho* |
| [x] | **F4.4** `next:<tipo>` resuelto por **grep sobre `ciclos/`** | [ADR 0007](../../../docs/decisiones/0007-plan-es-calendario.md) | crear un plan excepcional → las tareas se re-resuelven solas ✅ *hecho* |
| [x] | **F4.5** `tuku abrir` / `tuku cerrar`, **sin LLM por defecto** | [`artefactos-ciclo.md`](../../../spec/artefactos-ciclo.md) | `--sin-agente` produce el artefacto con insumos y sin redacción ✅ *hecho* |
| [x] | **F4.6** RADAR: consulta en vivo, sin archivo | `arquitectura.md` §11 | no escribe nada en disco ✅ *hecho* |
| [x] | **F4.7** Instanciador de procesos | [ADR 0011](../../../docs/decisiones/0011-proceso-sin-almacenamiento.md) | no agrega primitiva de almacenamiento: son tareas ✅ *hecho* |

> **Sin planes futuros sembrados, `next:<tipo>` no resuelve.** Es consecuencia directa del
> ADR 0007 y el motor debe avisarlo explícitamente, no fallar en silencio ni inventar una
> fecha.

---

## 🤖 Fase 5 — Integración agéntica (Hermes)

Primera fase que gasta tokens. Todo test aquí lleva el marcador `agentic` y **no** corre por
defecto.

| | Ítem | Verificación |
|---|---|---|
| [x] | **F5.0** `tuku init` provisiona `.hermes/` por perfil con symlinks a credenciales ([ADR 0018](../../../docs/decisiones/0018-hermes-subproceso-por-perfil.md)) | `test_init_crea_hermes_dir`, `test_init_hermes_enlaza_credenciales`, `test_gitignore_contiene_hermes` ✅ *hecho* |
| [x] | **F5.1** Procesos ejecutables en `src/tuku/procesos/` | `alta-entidad.md`, `apertura-ciclo.md`, `cierre-ciclo.md`, `registro-conversacional.md` completos ✅ *hecho* |
| [x] | **F5.2** `tuku registrar` (captura conversacional → canónico) | capa factual activa: `test_registrar_verifica_entidad_inexistente`; heurísticas: `test_registrar_detecta_*` ✅ *hecho* |
| [x] | **F5.3** Siembra asistida en `tuku abrir` / `tuku cerrar` | `test_abrir_ciclo_secciones_obligatorias`, `test_cerrar_ciclo_secciones_c7`, `test_cerrar_ciclo_marca_plan_closed` ✅ *hecho* |
| [x] | **F5.4** Inyección del tesauro vivo | `test_tesauro_respeta_limite_chars`, `test_tesauro_excluye_archivadas`, `test_tesauro_incluye_vigentes` ✅ *hecho* |
| [x] | **F5.5** Harness de Hermes con perfiles efímeros | fixture `hermes_efimero` usa `.hermes/` del `perfil_tmp`; tests agénticos (`@pytest.mark.agentic`) en gemelo ✅ *hecho* |

> **Todo test agéntico tiene un gemelo sin agente**, y ese camino se testea siempre. Si un
> proceso solo funciona con un modelo de frontera, **el proceso está mal escrito** (P2) — por
> eso la suite corre con el modelo económico y no con el mejor disponible.

---

## ⏰ Fase 6 — Scheduler proactivo

| | Ítem | Verificación |
|---|---|---|
| ☐ | **F6.1** Lazo periódico: cadencias, `followup`, `notify_window` | con reloj inyectado; ningún test espera tiempo real |

---

## Salud permanente de la suite

Estos corren desde hoy y deben seguir en verde en cada commit:

- [x] Enlaces relativos de `docs/`, `spec/`, `devel/` y `corpus/` resuelven.
- [x] Ninguna referencia a specs eliminadas.
- [x] Sin identificadores del contexto real en el repositorio público.
- [x] Toda invariante de `spec/` tiene test o entrada declarada en `PENDIENTES`.
- [x] Toda invariante declara garante reconocible.
