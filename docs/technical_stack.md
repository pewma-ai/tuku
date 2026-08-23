# Stack Técnico (Technical Stack)

> `docs/technical_stack.md` · Definición del stack tecnológico, dependencias, herramientas de calidad y arquitectura de ejecución de TUKU. Se deriva de [`brief.md`](brief.md), [`arquitectura.md`](arquitectura.md), [`deployment.md`](deployment.md) y las decisiones de diseño del proyecto.

---

## 1. Tesis y Principios Técnicos

El stack de TUKU está subordinado a una regla fundamental: **la información vive en archivos de texto plano (Markdown)** y sobrevive a cualquier motor, visor o proveedor de LLM. La arquitectura de archivos es el diseño central y todo lo demás la sigue.

- **Determinismo primero**: Todo lo que pueda resolverse con código determinista se ejecuta con scripts y janitors en Python puro; los LLMs se reservan exclusivamente para síntesis y juicio semántico.
- **Dos artefactos desacoplados**: El **Motor** (código en `site-packages`) evoluciona e interactúa de forma independiente del **Perfil** (datos en un repositorio Git del usuario).
- **Cero vendorización innecesaria**: Dependencias mínimas, estrictas y probadas en producción.

---

## 2. Lenguaje y Runtime

| Componente | Tecnología | Versión / Especificación | Justificación |
|---|---|---|---|
| **Lenguaje Core** | Python | `>=3.14` | Soporte nativo para tipado estricto avanzado, rendimiento optimizado y ciclo de vida moderno. |
| **Gestor de Entorno / Paquetes** | `uv` | Última versión estable | Resolución ultrarrápida de dependencias en desarrollo (`uv venv`, `uv pip`, `uv.lock`). |
| **Aislamiento de CLI para Usuario** | `pipx` | Estándar | Ejecución e instalación aislada del CLI `tuku` sin contaminar el Python del sistema operativo. |
| **Build Backend** | `setuptools` + `setuptools-scm` | `setuptools>=68`, `setuptools_scm>=8` | Empaquetado estándar con estampado dinámico de versión desde tags/commits Git. |

---

## 3. Modelo de Persistencia y Almacenamiento

TUKU no utiliza bases de datos relacionales ni embebidas para la verdad del dominio.

- **Formato Canónico**: Archivos Markdown (`.md`) UTF-8 legibles por humanos y agentes.
- **Metadatos y Estructuras**:
  - Front Matter en YAML delimitado por `---` para identidad, tipos y ciclos de vida.
  - Comentarios HTML invisibles para renderizadores (`<!-- tuku:editable -->`, `<!-- tuku:derived hash=... -->`, `<!-- tuku:cadencias ... -->`) para delimitar bloques mutables, proyecciones derivadas y metadatos posicionales de tareas.
- **Configuración del Perfil**: `.tuku/config.yaml` versionado en el repositorio de datos, con declaración explícita de `schema_version`.
- **Configuración Global de Sistema**: `~/.tuku/config.toml` (registro de múltiples perfiles).
- **Control de Versiones**: Repositorio Git por perfil para auditoría, diffs e inmutabilidad de la bitácora.

---

## 4. Dependencias del Motor (Core Dependencies)

Definidas en [`pyproject.toml`](../pyproject.toml) bajo la premisa de dependencia mínima:

| Dependencia | Versión | Rol en el Sistema |
|---|---|---|
| `pydantic` | `>=2.0` | Definición de modelos (`ProfileConfig`, `TukuTask`, `Entry`), validación estricta de esquemas e invariantes, y deserialización masiva de alta velocidad mediante núcleo en Rust (`pydantic-core`). |
| `PyYAML` | `>=6.0` | Parsing y serialización de Front Matter YAML y configuración `.tuku/config.yaml`. |

---

## 5. Integración Agéntica (LLMs y Clientes)

TUKU concibe al agente como un **cliente reemplazable** y no como el núcleo del sistema.

| Componente | Enfoque Técnico | Detalles de Implementación |
|---|---|---|
| **Clientes Soportados** | Hermes, Claude Code, Antigravity | Operan sobre el mismo perfil sin capas de abstracción propietarias. |
| **Instrucciones del Repositorio** | `AGENTS.md` + symlink `CLAUDE.md` | Instrucciones distribuidas y anidadas jerárquicamente en el árbol de carpetas. |
| **Invocación Agéntica Interna** | Subproceso CLI: `hermes chat` | Invocación desacoplada (`hermes chat -z <prompt> --continue`). |
| **Aislamiento de Estado LLM** | Variable de entorno `HERMES_HOME` | Cada perfil TUKU posee su propio `<perfil>/.hermes/` (sesiones, memoria, logs) sin contaminar `~/.hermes`. Credenciales enlazadas vía symlinks. |
| **Modo Offline / Sin Inferencia** | Flag `--sin-agente` | Toda la lógica de negocio y janitors opera sin LLM ni conexión a red. |

---

## 6. Herramientas de Desarrollo y Calidad (Tooling & QA)

Configuración rigurosa para garantizar reproducibilidad y tipado estricto:

| Herramienta | Versión / Configuración | Uso en el Proyecto |
|---|---|---|
| **Test Runner** | `pytest>=8.0`, `pytest-cov>=5.0` | Suite de pruebas automatizadas con `--strict-markers`, `--strict-config` y `filterwarnings = ["error"]`. |
| **Marcadores de Test (`pytest`)** | `spec`, `invariante`, `aceptacion`, `replay`, `agentic`, `lento` | Jerarquía de pruebas de 4 niveles + aislamiento de pruebas con gasto de tokens (`-m "not agentic"` por defecto). |
| **Linter / Formatter** | `ruff>=0.6` | Chequeo estático y formateo con longitud de línea 96 (`E`, `F`, `I`, `UP`, `B`, `SIM`, `RUF`). Se ignoran `RUF001`-`RUF003` para admitir tipografía y puntuación en prosa española. |
| **Type Checker** | `mypy>=1.11` | Chequeo estático de tipos en modo estricto (`strict = true`, `python_version = "3.14"`), apoyado por `types-PyYAML`. |
| **Git Hooks** | `pre-commit>=3.8` | Validación previa al commit de formato, linting y tipos. |

---

## 7. Interfaces de Usuario, Visores y Canales de Entrada

| Nivel de Interfaz | Tecnología | Rol | Estado |
|---|---|---|---|
| **CLI** | `src/tuku/cli.py` (`tuku`) | Superficie principal de interacción por terminal (`init`, `registrar`, `abrir`, `cerrar`, `radar`, `janitor`, `doctor`, `migrate`). | Activo (V1) |
| **Visor Local de Escritorio** | [Obsidian](https://obsidian.md) | Interfaz gráfica local. Lee archivos Markdown puros y respeta marcado en comentarios HTML. | Activo (V1) |
| **Visor Web Estático** | [Quartz 5](https://quartz.jzhao.xyz) (Quartz5) | Publicación y consulta web en modo solo lectura sobre el repositorio Markdown. | Planificado (Fase 2) |
| **Gateway de Mensajería** | [Intergram](https://github.com/idoco/intergram) (o bot Telegram dedicado) | Canal de entrada móvil para captura rápida de bitácora y tareas vía chat de Telegram hacia el motor. | En evaluación |
| **Servidor Centralizado** | Python + Quartz5 + Hermes Gateway | Despliegue multiusuario en VM (Oracle Cloud) con aislamiento POSIX por perfil. | Planificado (Fase 2) |

---

## 8. Entorno de Ejecución y Despliegue

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USUARIO / AGENTE                              │
│  Obsidian (GUI) │ tuku CLI │ Hermes / Claude / AGY │ Telegram/Intergram │
└──────────────┬──────────────────┬─────────────────┬─────────────────────┘
               │                  │                 │
┌──────────────▼──────────────────▼─────────────────▼─────────────────────┐
│                             MOTOR TUKU                                  │
│                (Python 3.14 / Pydantic v2 / PyYAML)                     │
│  - Janitors (jntr.*) deterministas                                      │
│  - Pipeline de Derivaciones (build por diff de hash)                    │
│  - Consultas efímeras (RADAR)                                           │
│  - Migraciones de esquema (src/tuku/migrations/)                        │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                          PERFIL DE DATOS                                │
│          (Repositorio Git del Usuario: Markdown + YAML)                 │
│  - entradas/ (inmutable)      - tareas/ (mutable)                       │
│  - ciclos/ (planes/reportes)  - ambitos/ (entidades)                    │
│  - AGENTS.md (instrucciones)  - .tuku/config.yaml                       │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Ejecución Local**: Motor instalado en el entorno aislado del usuario vía `pipx`, operando sobre perfiles en el sistema de archivos local.
- **Automatización**: Ejecución de janitors y reevaluación de cadencias mediante `cron` o invocación manual con `tuku janitor`.
- **Evolución de Esquema**: Migraciones secuenciales declarativas en `src/tuku/migrations/` ejecutadas mediante `tuku migrate` en commits atómicos e independientes.

---

## 9. Decisiones Técnicas Fundamentales

| Decisión Técnica | Impacto en el Stack |
|---|---|
| **ID estable independiente del path** | Entidades indexadas por `id` único (`ent_...`), eliminando dependencias de reescritura masiva de rutas al mover carpetas. |
| **Motor desacoplado del perfil** | Distribución mediante paquete Python independiente (`pipx`), sin vendorización de código en repositorios de datos del usuario. |
| **Versionado explícito de esquema** | Declaración de `schema_version` y módulo interno de migraciones (`src/tuku/migrations/`) para garantizar supervivencia de datos a largo plazo. |
| **Detección de divergencia por hash** | Control de integridad de secciones derivadas mediante hashes SHA/CRC en comentarios HTML sin requerir bloqueos de permisos a nivel sistema operativo (`chmod 444`). |
| **Cadencias en comentarios HTML** | Metadatos de automatización y recurrencia integrados dentro del Markdown sin requerir archivos YAML adicionales. |
| **Formato posicional para tareas** | Tareas como listas Markdown compactas con metadatos del motor (`id`, `created`, `scheduled`) incrustados en comentarios. |
| **`tuku.log` excluido de Git** | Registro de operaciones en `.tuku/tuku.log` añadido al `.gitignore` del perfil para no ensuciar el historial de datos. |
| **Pydantic v2 como motor de esquemas** | Incorporación de `pydantic>=2.0` como dependencia principal para tipado y validación de alto rendimiento con núcleo en Rust. |
| **Subproceso CLI para Hermes** | Invocación de Hermes vía CLI con aislamiento de perfiles vía variable de entorno `HERMES_HOME`. |
