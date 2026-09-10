# tests/

Arquitectura y guía maestra de verificación de TUKU. Define cómo se prueba el sistema y establece los criterios para escribir nuevos tests de forma consistente y mantenible.

## Organización en capas

La suite de pruebas se organiza en dos capas complementarias derivadas de los epics ([`../devel/epics.md`](../devel/epics.md)):

| Directorio | Naturaleza | Qué prueba | Ejecución |
|---|---|---|---|
| [`unitarios/`](unitarios/README.md) | En memoria, sin I/O | Funciones puras, parsers, validaciones algorítmicas y transformaciones de texto | Ultra-rápida (<0.2s toda la suite) |
| [`escenarios/`](escenarios/README.md) | Integración E2E (CLI) | Historias BDD de cara al usuario, efectos colaterales en el vault, sincronización e idempotencia | Segundos por epic |
| [`scripts/`](scripts/README.md) | Infraestructura | Arnés ejecutor ([`gherkin.py`](scripts/gherkin.py)), inspección de fixtures y wrappers de agentes | Soporte |

## Principios de verificación

1. **El test BDD es la fuente de verdad ejecutable:** El comportamiento se define en un archivo Markdown (`XXX-YY-slug.md`). El arnés [`scripts/gherkin.py`](scripts/gherkin.py) parsea los bloques `bash` y los ejecuta en proceso (`cli.main`), garantizando que la documentación y la prueba nunca diverjan.
2. **Superficie CLI completa:** Los escenarios ejecutan comandos `tuku`, nunca llamadas directas a funciones internas. Solo la invocación CLI completa ejerce los efectos colaterales reales: derivación y propagación de vistas, mutación de archivos y códigos de retorno.
3. **Trazabilidad de tres niveles:** Cada escenario BDD enlaza explícitamente a:
   - Los principios rectores ([`../docs/principios.md`](../docs/principios.md)).
   - La promesa de valor del brief ([`../docs/brief.md`](../docs/brief.md)).
   - Las especificaciones normativas ([`../spec/README.md`](../spec/README.md)).
4. **Aceptación humana (en Obsidian):** Además de validar aserciones computacionales, cada escenario define cómo debe leerse el resultado con ojos humanos en Obsidian para asegurar legibilidad a 20 años y lenguaje natural sin metadatos intrusivos.
5. **Idempotencia comprobable:** Todo comando mutador debe ser idempotente. La verificación se realiza por cálculo de diffs (`corrida.delta_de("mi-vault")`): el segundo pase de una misma operación debe arrojar diff vacío `{}`.

## Cómo escribir un nuevo escenario BDD

Cada escenario consta de dos archivos con nombres hermanados:
- Caso narrativo: `tests/escenarios/XXX-YY-slug.md`
- Aserciones de soporte: `tests/escenarios/test_XXX_YY_slug.py`

### 1. Estructura del archivo Markdown (`.md`)

```markdown
# XXX-YY · <Nombre del comportamiento>

> **Principio:** [P...](../../docs/principios.md) · **Brief:** [Sección](../../docs/brief.md) · **Spec:** [`spec/...`](../../spec/README.md) · **Origen:** [referencia](../../devel/epics.md)

<Una sola frase concisa describiendo la fricción eliminada o la promesa cumplida>.

## Estado inicial

```bash
cp -r ../../<paso-anterior>/<sub-slug>/mi-vault .
```

## Escenario: <título que describe la acción y el resultado>

Dado <precondición del vault>
Cuando <acción que ejecuta el comando>
```bash
tuku <comando> <argumentos>
```
Entonces <resultado observable en el vault o salida>
Y <aserciones adicionales o segundo pase idempotente>

## Aceptación humana (en Obsidian)

- <Qué debe verificar una persona leyendo directamente los archivos resultantes>.
```

### 2. Estructura del arnés en Python (`test_*.py`)

El archivo Python no repite los comandos; solo importa `gherkin`, ejecuta el escenario por fragmento de título y aserta:

```python
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402
from tuku.cli import EXITO  # noqa: E402

SLUG = "XXX-YY-slug"

def test_XXX_YY_comportamiento_esperado() -> None:
    corrida = gherkin.correr(SLUG, "fragmento del título del escenario")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    # Aserciones sobre archivos y diffs
    assert corrida.delta_de("mi-vault") == {"AHORA.md": "modificado"}
    contenido = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "texto esperado" in contenido
```

## Manejo determinista del tiempo (`TUKU_NOW`)

Para probar fallbacks a la fecha de hoy y hora actual sin depender del reloj del sistema ni contaminar el código de producción con variables de entorno:
- Declarar `TUKU_NOW="AAAA-MM-DD HH:MM"` antes del comando `tuku` en el bloque `bash` del escenario:
  ```bash
  TUKU_NOW="2026-08-11 15:30" tuku todo open --vault mi-vault --scope personal --body "comprar café"
  ```
- El arnés [`scripts/gherkin.py`](scripts/gherkin.py) intercepta `TUKU_NOW` y congela `date.today()` y `datetime.now()` en los módulos de `tuku` exclusivamente durante esa llamada en proceso.

## Reglas para tests unitarios (`tests/unitarios/`)

- Destinados a funciones puras (por ejemplo: `tuku.ahora`, `tuku.todo.parsear`, `tuku.lint`).
- **Cero I/O de disco y cero red:** no deben crear directorios ni leer archivos reales del sistema. Toda entrada se pasa como cadenas de texto en memoria.
- Rápidos y aislados: la suite completa debe correr en menos de 0.2 segundos.

## Ejecución y comandos útiles

```bash
# Correr toda la suite determinista
uv run pytest

# Correr solo los tests unitarios en memoria
uv run pytest --unittests

# Correr los escenarios de un epic específico
uv run pytest tests/escenarios/ -k 002

# Correr un escenario puntual
uv run pytest tests/escenarios/ -k 002_04

# Verificación de linter y tipado estricto
uv run ruff check .
uv run mypy src tests
```
