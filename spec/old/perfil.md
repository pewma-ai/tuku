# spec/perfil.md — Perfil y Configuración (.tuku/config.yaml)

> Define la estructura del perfil de usuario y la especificación normativo del archivo `.tuku/config.yaml`.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §2 y [`spec/entidad.md`](entidad.md).

---

## 1. Definición del Perfil

El **Perfil** es el repositorio Git propiedad del usuario que almacena su historial canónico, entidades, cadencias, tareas, planes e informes.

---

## 2. Configuración del Perfil (`.tuku/config.yaml`)

El archivo `.tuku/config.yaml` declara la versión del esquema, clasificaciones por defecto y el **grafo de derivaciones** recomputable ([ADR 0003](../docs/decisiones/0003-version-de-esquema.md), [ADR 0004](../docs/decisiones/0004-canonico-no-es-vista.md)).

### 2.1 Ejemplo Normativo Completo

```yaml
schema_version: 0               # versión de esquema del perfil (entero)
profile_name: "personal"        # nombre del perfil

clasificaciones:
  - hito
  - decision
  - senal
  - msg

task_archive_delay: 7d          # plazo de retención antes de archivar tareas cerradas

derivations:
  - target: "ciclos/plan_{fecha}_{tipo}.md#tareas-del-ciclo"
    sources: ["tareas/tareas.md", "estrategia/cadencias.md"]
    build: "tareas_del_ciclo"

  - target: "entidades/{ruta}/{entidad}.md#bitacora-entidad"
    sources: ["entradas/entradas.md"]
    filter: "entidad == {entidad}"
    build: "proyeccion_entidad"

  - target: "notas/notas.md"
    sources: ["notas/**/*.md"]
    build: "indice_notas"
```

---

## 3. Estrategia y Capacidad (`estrategia/capacidad.md`)

`estrategia/capacidad.md` define los recursos, ritmos y restricciones del usuario.

### 3.1 Front Matter Estructurado

```yaml
---
id: capacidad
type: capacidad
notify_window: "07:00-14:00"     # opcional; fuera de esta franja no se notifica
timezone: America/Santiago
---

# Capacidad del usuario

El cuerpo sigue siendo texto libre: ritmos, energía, restricciones. Nada de esto se parsea mecánicamente.
```

- **`notify_window`**: Franja horaria para el envío de avisos emitidos con `notify: window` (`spec/cadencia.md` §5).

---

## 4. Invariantes

| # | Regla | Garante |
|---|---|---|
| F1 | `schema_version` es un entero no negativo compatible con la versión soportada por el motor | janitor / motor |
| F2 | `notify_window` debe tener formato `HH:MM-HH:MM` válido si está presente en `capacidad.md` | janitor |
| F3 | El perfil contiene sólo datos y punteros a procesos, nunca código ejecutable vendorizado ([ADR 0002](../docs/decisiones/0002-motor-fuera-del-perfil.md)) | janitor |
| F4 | El grafo de derivaciones en `derivations` es acíclico | janitor / motor |
