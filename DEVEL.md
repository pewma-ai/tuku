# Desarrollo de TUKU

Guía de desarrollo, arquitectura y estrategia de implementación para el motor de software de TUKU.

---

## 1. Estructura del espacio de desarrollo

- **[`devel/`](devel/)** — Especificaciones técnicas maestras, notas de arquitectura y diseño:
  - [`que_implementar.md`](devel/que_implementar.md): Documento maestro de implementación en 10 fases y estrategia de pruebas.
  - [`technical_stack.md`](devel/technical_stack.md): Stack técnico formal, decisiones de dependencias y herramientas.
  - [`entorno-devel.md`](devel/entorno-devel.md): Configuración del entorno de desarrollo local.
  - `VAULT/`: Vaults de referencia y fixtures para pruebas.
- **[`tests/`](tests/)** — Suite de pruebas automatizadas y fixtures de transición de estado.
- **[`corpus/`](corpus/)** — Datos de prueba, grabaciones y ground truth para evaluar formateo de entrada.
- **[`playground/`](playground/)** — Prototipado rápido de janitors, scripts y experimentación con comandos del CLI.

---

## 2. Plan Maestro de Implementación (10 Fases)

El desarrollo sigue estrictamente las 10 fases definidas en [`devel/que_implementar.md`](devel/que_implementar.md). **Cada fase concluye con un vault plenamente funcional** que una persona puede operar a mano:

| Fase | Nombre | Qué se puede hacer al terminarla | LLM | Fixture |
|:---:|---|---|:---:|---|
| **0** | El vault que se puede abrir | Empezar a escribir a mano en estado cero | No | `vacio` |
| **1** | La entrada | Dictar y formatear a línea de bitácora canónica | Sí | `primer-dia` |
| **2** | Pendientes | Mantener `PENDIENTES.md` de forma determinista | No | `ciclo-en-curso` |
| **3** | El árbol de ámbitos | Resolver reglas por cercanía y organizar frentes | No | `ciclo-en-curso` |
| **4** | Cadencias | Resolver y sembrar recurrencias con idempotencia | No | `ciclo-en-curso` |
| **5** | Notas y enlaces | Zettelkasten, notas tipadas y tejido de enlaces | No | `ciclo-en-curso` |
| **6** | El ciclo | Apertura y cierre de ciclo con aplanado de texto | No | `ciclo-por-cerrar` |
| **7** | Plan y resumen | Cálculo de capacidad neta, plan y resumen | Sí | `ciclo-por-cerrar` |
| **8** | Endurecimiento | Reconstrucción completa e idempotencia global | No | `historico` |
| **9** | Inferencia semántica | Detección de patrones y destilado en contexto aislado | Sí | `historico` |

---

## 3. Estrategia de Pruebas y Fixtures

### Cada prueba es una transición de estado
Toda prueba evalúa una transición determinista:
```text
fixtures/<nombre>/
  inicial/          # Estado del vault antes de la operación
  operacion.txt     # Línea a inyectar en bitácora o janitor a invocar
  esperado/         # Estado exacto del vault después
```

### Principios de verificación:
- **Diff byte a byte:** Toda operación de janitor debe coincidir exactamente con el estado esperado.
- **Idempotencia estricta:** Ejecutar cualquier janitor o conjunto de operaciones dos veces seguidas no debe modificar nada ni generar duplicados.
- **Escalera de fixtures:** `vacio` $\to$ `primer-dia` $\to$ `ciclo-en-curso` $\to$ `ciclo-por-cerrar` $\to$ `historico`. Generar la escalera por reproducción es en sí misma la prueba de integración del sistema.

---

## 4. Entorno Técnico y Convenciones

- **Lenguaje:** Python 3.12+ gestionado con `uv`.
- **CLI:** Punto de entrada `tuku` (para instalación de vaults, apertura/cierre de ciclos y linting).
- **Janitors:** 
  - Especificación en el repositorio: `reglas/janitors.tuku.md`.
  - Código instalado: `~/.tuku/janitors/` (aislado del vault del autor).
- **Higiene de código:** `ruff`, `pre-commit`, typing estricto con `mypy` / `pyright`.