# Checklist de Implementación (Spec-Driven Development)

> `devel/checklist-implementacion.md` · Lista de control trazable para la construcción de TUKU fase por fase.

---

## 🏗️ Fase 0 — Cimientos y Tooling

- [ ] **F0.1** Configurar `pyproject.toml` con `uv`, `pytest`, `ruff`, `mypy`.
- [ ] **F0.2** Implementar `core/config.py`: lectura de `.tuku/config.yaml` y validación de `schema_version` (ADR 0003).
- [ ] **F0.3** Implementar `tuku init`: creación del árbol de directorios y siembra de `.gitignore` excluyendo `tuku.log` y `.tuku/cache/` (ADR 0015).
- [ ] **F0.4** Implementar `tuku sync`: generación de punteros a procesos y `AGENTS.md` por nivel (ADR 0002).
- [ ] **F0.5** Implementar `tuku doctor`: reporte de versión, commit, rama Git y validación de perfil.

---

## 🔤 Fase 1 — Parsers y Serializadores (Round-Trip Exacto)

- [ ] **F1.1** Implementar parser/serializador de Front Matter YAML (`spec/frontmatter.md`).
- [ ] **F1.2** Implementar parser/serializador posicional de tareas: `<created> <effort> <entity|-> <deadline|-> <followup|-> <blockuntil|-> <originator> <texto> ^t-<id>` + `<!-- tuku: ... -->` + `>` (ADR 0014).
- [ ] **F1.3** Implementar parser/serializador de entradas: hora opcional, `[entidad](ruta)`, clasificación y `#marcadores` (`spec/entradas.md`).
- [ ] **F1.4** Implementar parser de gramática temporal: precisa, rango, difusa, `next:<tipo>`.
- [ ] **F1.5** Preservar delimitadores HTML (`<!-- tuku:editable -->`, `<!-- tuku:derived -->`, `<!-- tuku:cadencias -->`) (ADR 0013).
- [ ] **F1.6** Tests de Round-Trip byte-a-byte con fixtures de las specs en `tests/`.

---

## 🛡️ Fase 2 — Janitors e Invariantes

- [ ] **F2.1** Invariantes de Entidad (N1–N9).
- [ ] **F2.2** Invariantes de Entradas (E1–E7).
- [ ] **F2.3** Invariantes de Tarea (T1–T8).
- [ ] **F2.4** Invariantes de Cadencia (K1–K9).
- [ ] **F2.5** Invariantes de Ciclo (C1–C7).
- [ ] **F2.6** Invariantes de Proceso (R1–R6).
- [ ] **F2.7** Invariantes de Nota (O1–O8).
- [ ] **F2.8** Invariantes de Perfil (F1–F2).
- [ ] **F2.9** CLI `tuku janitor [--fix]` (idempotente).

---

## 📊 Fase 3 — Grafo de Derivaciones y Builders

- [ ] **F3.1** Grafo de derivaciones en `config.yaml` y chequeo de aciclicidad.
- [ ] **F3.2** Builder `bitacora_entidad`.
- [ ] **F3.3** Builder `tareas_del_ciclo`.
- [ ] **F3.4** Builder `cadencias-legibles`.
- [ ] **F3.5** Builder `indice_notas` y `notas_entidad`.
- [ ] **F3.6** Hash de fuentes y detección de divergencia antes de sobrescribir (ADR 0005).
- [ ] **F3.7** Build sobre diff (recomputación incremental).

---

## ⏱️ Fase 4 — Cadencias, Ciclos, Procesos y RADAR

- [ ] **F4.1** Colector de cadencias con cache `.tuku/cache/cadencias-resueltas.yaml`.
- [ ] **F4.2** Evaluador de disparos: `calendar`, `event`, `absence`, `completion`.
- [ ] **F4.3** Registro de ocurrencias para idempotencia (K4).
- [ ] **F4.4** Resolución de `next:<tipo>` mediante grep sobre `ciclos/` (ADR 0007).
- [ ] **F4.5** `tuku abrir` / `tuku cerrar` (sin LLM por defecto).
- [ ] **F4.6** Módulo RADAR (consulta en vivo sobre el perfil).
- [ ] **F4.7** Instanciador de Procesos (`spec/proceso.md`, ADR 0011).

---

## 🤖 Fase 5 — Integración Agéntica (Hermes)

- [ ] **F5.1** Redactar markdown ejecutables de procesos en `src/tuku/procesos/`.
- [ ] **F5.2** `tuku registrar` (captura conversacional -> canónico).
- [ ] **F5.3** Siembra asistida por LLM en `tuku abrir` / `tuku cerrar`.
- [ ] **F5.4** Inyección del Tesauro Vivo en contexto.
- [ ] **F5.5** Test Harness de Hermes (perfiles efímeros limpios).

---

## ⏰ Fase 6 — Scheduler Proactivo

- [ ] **F6.1** Lazo de evaluación periódica (cron) para cadencias, `followup` y franjas de notificación (`notify_window`).
