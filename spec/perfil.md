# spec/perfil.md — Perfil y Estrategia

> Define la estructura del repositorio del perfil y la especificación de `estrategia/capacidad.md`.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §2 y [`spec/entidad.md`](entidad.md).

---

## 1. Definición del Perfil

El **Perfil** es el repositorio Git propiedad del usuario que almacena su historial canónico, entidades, cadencias, planes e informes.

---

## 2. Estrategia y Capacidad (`estrategia/capacidad.md`)

`estrategia/capacidad.md` define los recursos, ritmos y restricciones del usuario.

### 2.1 Front Matter Estructurado

Combina metadatos leídos deterministamente por el motor con un cuerpo en prosa libre leído por agentes y humanos para estimar capacidad:

```yaml
---
id: capacidad
type: capacidad
notify_window: "07:00-14:00"     # opcional; fuera de esta franja no se notifica
timezone: America/Santiago
---

# Capacidad del usuario

El cuerpo sigue siendo texto libre: ritmos, energía, restricciones, lo que sea que ayude a estimar. Nada de esto se parsea de forma mecánica.
```

- **`notify_window`**: Franja horaria para el envío de avisos/notificaciones emitidos con `notify: window` por las cadencias (`spec/cadencia.md` §5).
- **Un archivo, dos lectores**: El front matter lo lee el motor de forma determinista (scheduler); el cuerpo lo lee quien estima la capacidad.

---

## 3. Invariantes

| # | Regla | Garante |
|---|---|---|
| P1 | `notify_window` debe tener formato `HH:MM-HH:MM` válido si está presente | janitor |
| P2 | El perfil contiene sólo datos y punteros a procesos, nunca código ejecutable vendorizado | janitor |
