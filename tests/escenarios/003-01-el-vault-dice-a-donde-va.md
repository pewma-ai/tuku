# 003-01 · El vault dice a dónde va

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33), [P5 (reglas en prosa)](../../docs/principios.md#L47) · **Brief:** [El agente y las herramientas](../../docs/brief.md#L60) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/cli.md`](../../spec/cli.md)

`AGENTS.md` gobierna el despacho del agente. `tuku doctor` comprueba deterministamente que la tabla de despacho sembrada por `tuku init` no nombre comandos inexistentes, reportando desalineaciones sin mutar el archivo.

## Estado inicial

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
Y la revisión `despacho` confirma que todos los comandos existen

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
Entonces el doctor lo reporta, nombra el comando que sobra y dice cómo corregirlo
Y no toca el archivo en disco

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

## Aceptación humana (en Obsidian)

- Al consultar `AGENTS.md` o ejecutar `tuku doctor`, la tabla de despacho debe reflejar únicamente comandos existentes en el CLI, con diagnósticos claros y no destructivos.
