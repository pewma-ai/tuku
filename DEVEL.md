# Desarrollo de TUKU

Índice del espacio de desarrollo. Este repositorio es el **software**; el libro del autor (su vault) vive en otro lado y es lo que TUKU instala y mantiene.

Cada documento carga un solo tipo de información, y por eso acá no se repite ninguno: esto solo dice dónde está cada cosa.

## Por dónde empezar

[`devel/epics.md`](devel/epics.md). Tiene el estado del trabajo, qué epic está en curso y qué falta para cerrarlo.

## Por dónde terminar

Regla de buena educación, para quien trabaje acá, persona o agente: **al cerrar una sesión de trabajo, deja el resumen del día en [`devel/iteraciones/AAAA-MM-DD.md`](devel/iteraciones/README.md)**, con qué se hizo, qué se decidió y qué queda pendiente.

Cuesta dos minutos y es lo que permite que la siguiente sesión retome sin depender de que alguien se acuerde de la conversación. Una decisión que solo existe en un chat es una decisión perdida.

## Dónde vive cada cosa

| Directorio | Qué contiene | Naturaleza |
|---|---|---|
| [`docs/`](docs/README.md) | El porqué: brief, principios, glosario, libro de estilo | Marco rector |
| [`spec/`](spec/README.md) | Qué hace el sistema, un archivo por primitiva | Normativo, y provisional entre epics |
| [`devel/`](devel/epics.md) | Cómo se construye: epics, plan de fases, entorno, diario | Plan |
| [`template/`](template/README.md) | Estructuras iniciales en Markdown que se copian al vault | Producto |
| `src/` | El código | Implementación |
| [`corpus/`](corpus/README.md) | Dictado de referencia, real e imaginado: fuente de fechas y de ideas de proceso | Dato |
| [`tests/`](tests/README.md) | El caso narrativo (Dado/Cuando/Entonces) y su arnés, uno junto al otro | Verificación |
| `playground/` | Corridas desechables. Ignorado por git, se pisa al recrear | Descartable |

Dentro de `devel/`: [`epics.md`](devel/epics.md) es el estado, [`que_implementar.md`](devel/que_implementar.md) el plan de fases y su justificación, [`iteraciones/`](devel/iteraciones/README.md) el diario por día, [`entorno-devel.md`](devel/entorno-devel.md) el entorno.

Cómo se relacionan estos cuatro: un epic da el número y la meta; un escenario lo cubre y, si necesita dictado o fechas reales, las toma de `corpus/`; el escenario y el test que lo verifica viven juntos en `tests/escenarios/`; lo que produce correrlo queda en `playground/`, que se pisa cada vez.

`devel/VAULT/` es **historia**: el diseño y el código anteriores a la reescritura de agosto de 2026. No es base para nada nuevo. Se rescata algo puntual solo cuando un epic lo necesita.

## Instalar un vault

Una línea, sin `git clone` y sin instalar ningún programa:

```bash
curl -fsSL https://raw.githubusercontent.com/pewma-ai/tuku/devel/install.sh | sh -s -- mi-vault
```

El procedimiento a mano equivalente está en [`template/README.md`](template/README.md), y debe seguir funcionando siempre: si el vault solo se puede crear ejecutando algo, se rompió el principio 1.

## Probar

Los escenarios son narrativos (Dado/Cuando/Entonces), no unitarios, porque buena parte del sistema depende de un agente y no da un resultado único. El caso y su arnés viven juntos en `tests/escenarios/`, y lo que solo se puede juzgar leyendo queda escrito en el propio escenario bajo "Qué se mira a mano".

```bash
uv run pytest tests/escenarios/            # todo
uv run pytest tests/escenarios/ -k 001      # un epic
```

Determinista, sin depender de un agente. `tests/` se construye solo desde los epics: la suite del diseño anterior se borró entera en vez de arrastrarla a medio migrar.

## Entorno

Python 3.14 con `uv`. Higiene con `ruff` y `mypy`, y las tres invariantes de determinismo, en [`devel/entorno-devel.md`](devel/entorno-devel.md).

Los janitors se especifican en prosa dentro del vault del autor (`reglas/janitors.tuku.md`) y su código se instala aparte, en `~/.tuku/janitors`. La especificación sobrevive, la implementación se reemplaza.
