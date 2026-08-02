# spec/frontmatter.md — Front Matter Canónico

> Define los campos obligatorios y opcionales en el Front Matter YAML de cada tipo de archivo.
> Especificación transversal consumida por los parsers (F1) e invariantes (F2).
> Consulta [`docs/decisiones/0009-type-string-libre.md`](../docs/decisiones/0009-type-string-libre.md).

---

## 1. Regla General

Todo documento `.md` canónico en TUKU (salvo notas sueltas en borrador) comienza con un bloque de Front Matter YAML delimitado por `---`:

<!-- tuku:caso id=frontmatter-base tipo=frontmatter -->
```yaml
---
id: identificador-unico
type: tipo_de_documento
created: YYYY-MM-DD
modified: YYYY-MM-DD
---
```

### Campos Comunes

| Campo | Obligatorio | Formato | Notas |
|---|---|---|---|
| `id` | sí | `string` kebab-case | Identificador estable ([ADR 0001](../docs/decisiones/0001-id-estable.md)) |
| `type` | sí | `string` | Tipo de artefacto. Libre, no restringido a enum cerrado ([ADR 0009](../docs/decisiones/0009-type-string-libre.md)) |
| `created` | opcional | `YYYY-MM-DD` | Fecha de creación canónica |
| `modified` | opcional | `YYYY-MM-DD` | Fecha de última modificación |

---

## 2. Campos Específicos por Tipo Artefacto

### 2.1 Entidades (`spec/entidad.md`)
```yaml
---
id: sw-responsible
type: proyecto                 # string libre (área, proyecto, cliente, etc.)
lifecycle: vigente            # vigente | archivada (default: vigente)
status: active                # active | blocked_until: YYYY-MM-DD
alineamiento: Objetivo clave  # opcional
keywords: [sw, dev]           # opcional
---
```

### 2.2 Entradas de Bitácora (`spec/entradas.md`)
```yaml
---
id: entradas-2026-08
type: entradas
period: 2026-08               # opcional en entradas.md activo, obligatorio en archivados
---
```

### 2.3 Backlog de Tareas (`spec/tarea.md`)
```yaml
---
id: tareas                    # o tareas-YYYY-MM en archivados
type: tareas
period: 2026-08               # solo en archivados YYYY-MM
---
```

### 2.4 Planes de Ciclo (`spec/artefactos-ciclo.md` §2.1)
```yaml
---
id: plan-2026-08-10-viaje
type: plan
cycle_type: viaje            # turno, descanso, semana, viaje, etc.
parent_cycle: plan-2026-08-03-semana  # opcional; indica plan anidado
place: Santiago              # opcional
cycle_start: 2026-08-10
cycle_end: 2026-08-16
status: open                 # open | closed
---
```

### 2.5 Resultados de Ciclo (`spec/artefactos-ciclo.md` §3.1)
```yaml
---
id: res-2026-08-04-turno
type: resultados
cycle_type: turno
cycle_start: 2026-08-04
cycle_end: 2026-08-11
entities: [jefatura, soporte-sw]
---
```

### 2.6 Procesos (`spec/proceso.md`)
```yaml
---
id: proc-cotizacion
type: proceso
ambito: negocio              # ámbito de aplicación
applies_to: [cliente]         # tipos de entidad compatibles
---
```

### 2.7 Notas (`spec/nota.md`)
```yaml
---
id: nota-patron-arquitectura
type: nota
summary: "Resumen obligatorio de la nota en una línea"  # vacio "" si es stub
entity: entidad-asociada     # opcional
tags: [arquitectura, mac]     # opcional
---
```

### 2.8 Capacidad / Estrategia (`spec/perfil.md`)
```yaml
---
id: capacidad
type: capacidad
notify_window: "07:00-14:00"  # opcional, franja de notificaciones
timezone: America/Santiago    # opcional
---
```

---

## 3. Invariantes

| # | Regla | Garante |
|---|---|---|
| M1 | Todo Front Matter abre y cierra con `---` en la primera línea del archivo | janitor |
| M2 | `id` y `type` son obligatorios en todo Front Matter canónico | janitor |
| M3 | Las fechas `created`, `modified`, `cycle_start`, `cycle_end` cumplen ISO 8601 (`YYYY-MM-DD`) | janitor |
