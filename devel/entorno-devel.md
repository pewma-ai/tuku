# Entorno de Desarrollo y Restricciones de Ejecución

> `devel/entorno-devel.md` · Normas de desarrollo, aislamiento de entorno y herramientas.

---

## 1. Aislamiento con `uv`

Para garantizar reproducibilidad y evitar contaminación del entorno Python global o del sistema:

1. **Gestión de Entorno Virtual y Dependencias**:
   - Se utiliza **`uv`** para la gestión de dependencias y creación del entorno virtual Python.
   - Creación del venv: `uv venv`
   - Sincronización de dependencias: `uv pip sync` o `uv sync`

2. **Ejecución de Comandos y Tests**:
   - Todo comando de desarrollo (`pytest`, `ruff`, `mypy`, `tuku`) debe ejecutarse dentro del entorno de `uv`:
     ```bash
     uv run pytest
     uv run ruff check .
     uv run mypy src
     uv run tuku doctor
     ```

---

## 2. Restricciones y Principios de Desarrollo

- **No gastar tokens en F0–F4**: Todo el desarrollo de parsers, janitors, derivaciones, cadencias y comandos CLI se prueba de forma determinista mediante `pytest` sin invocar modelos/LLM.
- **Spec-Driven**: El código en `src/` no inventa reglas; implementa exactamente lo especificado en `spec/`, `docs/` y validado por los ADR.
- **Round-Trip Byte-a-Byte**: Los parsers y serializadores deben ser capaces de leer un archivo canónico y volverlo a escribir sin alterar ni un solo byte de espaciado o comentarios.
- **Aislamiento de Tests Agénticos (F5)**: Cuando se ejecuten pruebas de integración con Hermes, cada test instanciará un perfil de Hermes desde cero (entorno efímero aislado).
