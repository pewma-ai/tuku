"""Comandos de TUKU: pasos deterministas que reaccionan a lo escrito en el vault.

La especificación en prosa de cada uno vive en `reglas/comandos.tuku.md` del
vault del autor (para que sobreviva aunque este código no); acá está la
implementación de referencia que usan los escenarios de `tests/`. Un módulo
por `noun` del CLI (`entry`, `todo`, `scope`, ...); cada comando es una función
`verb` importable, y su nombre canónico es el comando `tuku <noun> <verb>`.
"""
