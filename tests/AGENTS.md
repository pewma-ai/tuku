# Reglas de tests/

Cómo se escribe un escenario y cómo se corre la suite, en detalle: [`README.md`](README.md).

## Lenguaje

- Un escenario y su test dicen **qué verifican**, nada más. Concisos, directos, sin voseo.
- **Sin historia:** nada de "antes era", "se fundió", "venía del", fechas de cambios ni escenarios borrados. La historia va en [`../devel/iteraciones/`](../devel/iteraciones/) y en el commit.
- **Sin justificar de más:** una sección "Por qué existe" o "Qué prueba, y qué no" sobra si los pasos ya lo dicen. Se deja una nota solo si sin ella el test no se entiende.
- **El docstring de módulo no repite el `.md`:** qué afirma, en una a tres líneas, y cómo se corre.
- **Un docstring de test** solo cuando la aserción no se explica sola.

## Sin tests de más

- Cada test afirma algo que ningún otro afirma. Si dos se solapan, se funden.
- Lo determinista va en `unitarios/`: funciones puras, parsers, regex y validaciones, con caso nominal, vacío y malformado. Un escenario prueba solo lo que ve quien invoca `tuku`: códigos de salida, archivos y delta.
- Un escenario con agente no va en la base de una cadena: hereda de un vault determinista.

## Capas

| Capa | Dónde | Qué |
|---|---|---|
| Unitarios | [`unitarios/`](unitarios/README.md) | En memoria, sin disco. Toda la capa corre en menos de 0,2 s y es la única del hook de pre-commit |
| Escenarios | [`escenarios/`](escenarios/README.md) | Gherkin en `.md` ejecutado por `tuku` (CLI o `main(argv)`), nunca por funciones internas |

## Cómo se corre

```bash
uv run pytest                          # toda la suite determinista
uv run pytest --unittests              # solo unitarios
uv run pytest tests/escenarios/ -k 002 # un epic
uv run pytest -m agentic -k 003        # con agente: cuesta tokens y no es determinista
uv run pytest -m red                   # instalación real desde la red
```

`ruff check .` y `mypy src tests` limpios antes de cerrar.
