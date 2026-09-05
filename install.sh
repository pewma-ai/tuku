#!/bin/sh
# Instalador de una línea para un vault de TUKU.
#
#   curl -fsSL https://raw.githubusercontent.com/pewma-ai/tuku/devel/install.sh | sh -s -- mi-vault
#
# No instala ningún programa: baja el repositorio en un tarball temporal,
# copia template/vanilla/ al destino y resuelve las fechas de AHORA.md con
# src/install_test_scenario.py. Requiere curl, tar y python3, nada más.
#
# Si el destino ya existe y no está vacío, pregunta antes de sobrescribir.
# install_test_scenario.py, en cambio, sobrescribe sin preguntar a propósito:
# es la herramienta de prueba que se invoca desde playground/ para pisar un
# escenario a cada corrida. Este script es el único camino para un usuario
# final, y ahí sobrescribir en silencio es justo lo que no debe pasar.
#
# Variables de entorno opcionales:
#   TUKU_REPO   dueño/repo en GitHub (default: pewma-ai/tuku)
#   TUKU_REF    rama o tag (default: devel)
#   TUKU_VARIANTE  variante de template/ a instalar (default: vanilla)
#   TUKU_FORCE  si es "1", sobrescribe sin preguntar (para uso automatizado)

set -eu

REPO="${TUKU_REPO:-pewma-ai/tuku}"
REF="${TUKU_REF:-devel}"
VARIANTE="${TUKU_VARIANTE:-vanilla}"
DESTINO="${1:?uso: install.sh <directorio-destino> [AAAA-MM-DD]}"
DESDE="${2:-}"

for bin in curl tar python3; do
  command -v "$bin" >/dev/null 2>&1 || { echo "falta '$bin', no se puede instalar" >&2; exit 1; }
done

if [ -e "$DESTINO" ] && [ -n "$(ls -A "$DESTINO" 2>/dev/null)" ] && [ "${TUKU_FORCE:-}" != "1" ]; then
  printf '%s ya existe y no está vacío. ¿Sobrescribir? [s/N] ' "$DESTINO" >&2
  RESPUESTA="$( { read -r r < /dev/tty && printf '%s' "$r"; } 2>/dev/null )" || RESPUESTA=""
  case "$RESPUESTA" in
    s|S|si|Si|SI|sí|Sí) ;;
    *) echo "cancelado, nada se tocó." >&2; exit 1 ;;
  esac
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "bajando ${REPO}@${REF}..." >&2
curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${REF}.tar.gz" | tar -xz -C "$TMP"

# El tarball de GitHub crea una sola carpeta, <repo>-<ref>/
ORIGEN="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n1)"
if [ -z "$ORIGEN" ]; then
  echo "no se pudo extraer el repositorio" >&2
  exit 1
fi

if [ -n "$DESDE" ]; then
  python3 "$ORIGEN/src/install_test_scenario.py" --variante "$VARIANTE" --destino "$DESTINO" --desde "$DESDE"
else
  python3 "$ORIGEN/src/install_test_scenario.py" --variante "$VARIANTE" --destino "$DESTINO"
fi

echo "listo. abre $DESTINO/AHORA.md y escribe tu primera línea." >&2
