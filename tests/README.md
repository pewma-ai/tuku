# tests/ — Cómo se prueba TUKU

> Estrategia razonada en [`../devel/plan-implementacion.md`](../devel/plan-implementacion.md)
> §3. Este documento es el mapa operativo.

---

## Estado

`uv run pytest` pasa en verde **hoy**, antes de que exista el motor. Lo que ya se verifica no
es código, sino el corpus documental del que come el desarrollo asistido: enlaces,
anonimización y cobertura de invariantes.

Los tests que necesitan el motor se **saltan** (`skip`) mientras `tuku init` no exista. Un
`skip` masivo es la señal de que F0 sigue abierta; no es un fallo silencioso.

---

## Los cuatro niveles

| Nivel | Marcador | Qué prueba | Tokens |
|---|---|---|---|
| 1 | `spec` | los ejemplos normativos de `spec/`, uno a uno | no |
| 2 | `invariante` | cada invariante numerada, violándola a propósito | no |
| 3 | `aceptacion` | las simulaciones de `corpus/simulaciones/` | no |
| 4 | `replay` | reconstrucción con diff exactamente cero | no |
| — | `agentic` | lo que invoca un modelo | **sí** |

Los agénticos están excluidos por defecto en `pyproject.toml`. Para pedirlos:
`uv run pytest -m agentic`.

---

## Archivos

| Archivo | Qué hace |
|---|---|
| `conftest.py` | fixtures: `perfil_tmp`, `hermes_efimero`, `assert_diff_cero` |
| `specref.py` | lee los bloques normativos y las invariantes **directamente de `spec/`** |
| `test_coherencia_docs.py` | enlaces, anonimización, prefijos de invariante |
| `test_cobertura_specs.py` | qué invariantes tienen test y cuáles faltan |

---

## Los ejemplos salen de las specs, no de copias

`spec/README.md` declara que los ejemplos son normativos. `specref.py` los lee del Markdown
en vez de copiarlos a `fixtures/`, por la misma razón por la que TUKU no duplica datos: **una
copia se desincroniza**. Si alguien corrige un ejemplo en la spec y eso rompe el parser, es
exactamente lo que hay que enterarse.

Un bloque se marca como caso ejecutable con un comentario antes:

```markdown
<!-- tuku:caso id=tarea-minima tipo=tarea -->
```

Los bloques sin marca se ignoran: no todo bloque de una spec es un caso (hay árboles de
directorios y YAML ilustrativo).

---

## Un test por invariante

El nombre codifica la invariante: `test_T6_tarea_en_dos_archivos_canonicos`. Ese prefijo es
lo que permite a `test_cobertura_specs.py` saber, sin lista escrita a mano, qué está cubierto.

Al implementar una invariante, **borrar su entrada de `PENDIENTES`**. Si se olvida, el test
`test_la_lista_de_pendientes_no_miente` lo dice. Es deliberado que la lista falle en las dos
direcciones: impide que se convierta en un cementerio de excusas.

Las invariantes negativas (garante `—`: K7, C3, P5) no llevan test — declaran que algo *no*
es violación.

---

## Diff cero

`assert_diff_cero(perfil)` es el criterio del nivel 4 para todo lo producido por janitors. No
es "parecido": es idéntico, medido con Git.

Y la regla que lo convierte en instrumento de diseño y no solo en prueba de regresión:

> **Si algo que debería ser determinista solo pasa el test semántico, hay juicio del agente
> donde debería haber una regla.**

---

## Escribir un test nuevo

1. Busca la regla en `spec/`. Si no está escrita, **no la inventes en el test**: escríbela
   primero en la spec.
2. Marca el nivel (`@pytest.mark.invariante`, etc.).
3. Si necesita perfil, usa `perfil_tmp`. Nunca toques datos reales ni `~/.tuku`.
4. Si necesita fecha, inyéctala. Nada de `date.today()`.
