# Escenario · 003-04-un-hecho-con-consecuencia

**Cubre:** epic 003, cuarto peldaño. Gemelo determinista: [`002-04-abrir-pendiente`](002-04-abrir-pendiente.md).

El escenario central del epic. Todo lo anterior se podía resolver con una sola llamada; este no.

`tuku entry add` escribe el registro y nada más. Es `tuku todo open` el que abre el pendiente. Un agente que hace la primera y se olvida de la segunda deja los dos archivos bien formados y el vault a medias, y hasta hace poco nada lo detectaba: el `AGENTS.md` del vault dedica un párrafo entero a esto porque es el modo de falla más caro que tiene el sistema.

## Estado inicial

El que dejó [`003-03-un-hecho-un-comando`](003-03-un-hecho-un-comando.md): un registro escrito y ningún pendiente abierto.

```bash
cp -r ../../003-03-un-hecho-un-comando/un-hecho-que-no-deja-nada/mi-vault .
```

## Escenario: lo que queda por hacer se escribe y además se abre

Dado un vault con un registro escrito y la tabla de pendientes vacía
Cuando el autor dicta algo que queda por hacer

```agente
A las dos y veinte, hay que avisarle de los gastos comunes a la administradora.
```

Entonces queda un registro a las 14:20 con la marca `**pendiente**`
Y la tabla de `PENDIENTES.md` gana una fila con el mismo cuerpo, carácter por carácter
Y la fila entra en el primer escalón de la escalera del autor, que es el del ciclo en curso
Y no queda ninguna marca sin su consecuencia: la bitácora y la tabla dicen lo mismo
Y el delta es el mismo que deja el gemelo determinista

La cuarta es la que da nombre al escenario. Las otras tres pueden cumplirse a medias y esa no: o el agente hizo las dos llamadas, o no las hizo.

## Qué hace fallar y qué solo se reporta

**Falla:** que falte la marca, que falte la fila, que el cuerpo de la fila no sea el del registro, que el horizonte no salga de la escalera del autor, o que algo del vault haya cambiado por fuera de `tuku`.

**Se reporta:** cómo redacte el cuerpo. El vault del 002 dice "avisar de los GGCC a la administradora" y el dictado dice "gastos comunes"; que el agente abrevie o no es suyo. Lo que sí se exige es que el registro y la fila digan **lo mismo**, porque de eso depende poder cerrarlo después repitiendo el texto.

## Qué se mira a mano

`turno-1.md`. En particular el orden: el `AGENTS.md` pide escribir primero el registro y aplicar la consecuencia después, releyendo lo escrito y no lo conversado. Si la traza muestra el `todo open` antes del `entry add`, el vault igual queda bien hoy, pero el agente está trabajando desde la conversación y eso se rompe en cuanto haya deliberación de por medio (epic 004).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k "003_0[1234]" -m "not red and not pendiente"
```
