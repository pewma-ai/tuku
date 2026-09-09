# Escenario · 003-01-el-vault-dice-a-donde-va

**Cubre:** epic 003, primer peldaño de los dos ejes de [`003-00`](003-00-el-dia-uno-dictado.md): ningún agente, y la aserción más barata que existe.

Sin este escenario los otros cinco no significan nada. El `AGENTS.md` del vault es lo único que hace que un arnés cualquiera opere igual, y si nombra un comando que no existe, ningún modelo lo arregla: lo corre, recibe un error de uso e improvisa, casi siempre editando el archivo a mano, que es lo único que el vault prohíbe.

No gasta un token y entra en la corrida por defecto.

## Estado inicial

Un vault recién sembrado por `tuku init`. Es el primer paso del epic, así que no hereda de nadie.

```bash
tuku init mi-vault --date 2026-08-11
```

## Escenario: el vault nace con su tabla de despacho y el doctor la aprueba

Dado un vault recién sembrado
Cuando se corre

```bash
tuku doctor --vault mi-vault
```

Entonces el vault está sano
Y la revisión `despacho` dice cuántos comandos nombra el `AGENTS.md` y que todos existen

Es la misma forma que ya tiene `reglas/types.md`: una tabla escrita en prosa que el comando verifica. La diferencia es a quién le habla. `types.md` le habla al vault; esta le habla a quien lo opera.

## Escenario: un comando que no existe en la tabla es un error

Dado un `AGENTS.md` que nombra un comando inventado

```bash
sed -i.bak 's/`tuku scope create`/`tuku scope crear`/' mi-vault/AGENTS.md
rm mi-vault/AGENTS.md.bak
```

Cuando se corre

```bash
tuku doctor --vault mi-vault
```

Entonces el doctor lo reporta, nombra el comando que sobra y dice las dos formas de corregirlo
Y no toca el archivo, porque verificar y corregir son operaciones distintas

Es el caso que da todo el valor. Una tabla que envejece no avisa: sigue leyéndose bien.

## Escenario: sin AGENTS.md no hay despacho

Dado un vault al que le falta su `AGENTS.md`

```bash
cp mi-vault/AGENTS.md agents-respaldo.md
rm mi-vault/AGENTS.md
```

Cuando se corre

```bash
tuku doctor --vault mi-vault
```

Entonces el doctor lo reporta y dice qué se pierde sin él

```bash
cp agents-respaldo.md mi-vault/AGENTS.md
```

El vault sigue operable a mano: lo que falta no es una pieza del sistema, es la instrucción para quien lo opera.

## Qué no se afirma

**Que el CLI no tenga comandos fuera de la tabla.** Los tiene, y está bien: la tabla enruta lo que el autor dice, no documenta la superficie ([`spec/despacho.md`](../../spec/despacho.md)). Afirmarlo obligaría a tocar el `AGENTS.md` cada vez que crece el CLI, que es justo lo que el diseño evita.

**Que el agente la siga.** Eso es el `003-02` y cuesta un turno. Acá solo se afirma que la tabla no miente.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 003_01
```
