# Escenario · 001-02-init-siembra-el-estado-cero

**Cubre:** epic 001, decisiones 3 y 9.

## Escenario: `tuku init` produce el estado cero, byte a byte y sin red

Dado un directorio vacío, y el módulo `socket` parchado para que abrir un socket, conectar o resolver un nombre lance
Cuando se corre

```bash
tuku init mi-vault --variant vanilla
```

Entonces el árbol sembrado es idéntico a `template/vanilla/` salvo `AHORA.md`, `reglas/config.tuku.md` y `reglas/comandos.tuku.md`, sin que sobre ni falte ningún archivo
Y `reglas/comandos.tuku.md` dice, por cada comando, lo mismo que su `-h`
Y `AHORA.md` es `reglas/plantilla/AHORA.md`: el foco y ningún día
Y `PENDIENTES.md` trae la tabla con la columna `Creado` y ninguna fila
Y ningún archivo del vault conserva un placeholder fuera de un bloque de código
Y nada de esto intentó tocar la red

## Escenario: el vault sembrado está sano

Dado el vault sembrado

```bash
tuku init mi-vault
cd mi-vault
```

Cuando se revisa

```bash
tuku doctor
```

Entonces `tuku doctor` dice que el vault está sano

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_02
```

Deja el vault en `playground/001-02-init-siembra-el-estado-cero/`, a la vista.

## Qué se mira a mano

- Abrir el resultado en Obsidian: sin cajas de error ni archivos que no sepa mostrar.
- Que el foco de `AHORA.md` invite a escribir y que `ambitos/personal/personal.md` se explique solo como el único ámbito de partida.
