# Escenario · 004-06-ratificacion-compuesta

> Al concluir una conversación deliberativa, el autor emite una ratificación de cierre. El agente destila únicamente los compromisos netos acordados sin arrastrar borradores.

**Cubre:** Epic 004, regla "Registra el hecho, no la conversación" y traducción neta de intenciones acordadas.

---

El turno del agente declara `TUKU_NOW="2026-08-12 10:00"` en el fence ```agente```: el `tuku` que el agente ejecuta usa esa fecha como hoy y la anuncia por `stderr`. Así el agente y el escenario viven en el mismo día.

## Estado inicial

El vault resultante tras el rechazo limpio en [`004-05`](004-05-propuesta-y-rechazo-limpio.md).

```bash
cp -r ../../004-05-propuesta-y-rechazo-limpio/el-agente-propone-una-estructura/mi-vault .
```

---

## Escenario: el resumen de cierre se traduce en compromisos en firme

Dado el final de una sesión de conversación con acuerdos decantados
Cuando el autor sintetiza la decisión final en un solo turno de ratificación

```agente TUKU_NOW="2026-08-12 10:00"
Ya, en resumen: anota que el viernes a las diez voy al banco a firmar la ampliación de la línea, y que después de eso llamo a Andina para cerrar el pedido.
```

Entonces el agente ejecuta las llamadas de registro correspondientes para el viernes

```text
tuku todo open --due "2026-08-14 10:00" --scope personal \
  --body "ir al banco a firmar la ampliación de la línea"
tuku todo open --due 2026-08-14 --scope personal \
  --body "llamar a Importadora Andina para cerrar el pedido después del banco"
```

Y en `PENDIENTES.md` aparecen los dos compromisos fechados
Y en `AHORA.md` no se incluye ninguna referencia a "pedir la mitad del pedido" ni a dudas bancarias
Y la redacción de los pendientes conserva la literalidad necesaria para ser cerrados en el futuro

---

## Qué hace fallar y qué solo se reporta

* **Falla:** Registrar pendientes derivados de la deliberación anterior que no formaron parte del resumen de cierre; o no asignar la fecha del viernes a los nuevos compromisos.
* **Se reporta:** Si el agente agrupa ambos compromisos en una sola respuesta o si emite confirmaciones separadas.

---

## Qué se mira a mano

* Que el agente confirme el asentamiento de los acuerdos con sobriedad y sin repetir la historia de la conversación.
