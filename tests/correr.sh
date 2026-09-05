#!/usr/bin/env bash
# Correr tests/escenarios/, la única suite activa hoy: completa, por epic
# (tres dígitos) o por escenario (XXX-YYY). Sin argumentos, corre todo.
#
# Args extra se reenvían a pytest tal cual (-v, --tb=short, -k "...").
#
# La suite antigua bajo tests/ (test_*.py sueltos, diseño anterior) no se
# toca acá: no levanta con pytest hoy, se rehace en el epic 2
# (ver ../devel/entorno-devel.md).
#
# Ejemplos:
#   tests/correr.sh                    # todo
#   tests/correr.sh 001                # epic 001
#   tests/correr.sh 001-002            # un escenario
#   tests/correr.sh instalacion_local  # por nombre, cualquier substring
set -euo pipefail
cd "$(dirname "$0")/.."

if [ $# -eq 0 ]; then
  exec uv run pytest tests/escenarios/
fi

patron="${1//-/_}"
shift
exec uv run pytest tests/escenarios/ -k "$patron" "$@"
