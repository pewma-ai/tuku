# Escenario · 004-07-invariante-de-limites-en-sesion-larga

> La prueba de higiene global: tras una sesión conversacional completa de varios turnos con acumulación de contexto, ninguna prohibición de la tabla de Límites se vulneró y el vault permanece íntegro.

**Cubre:** Epic 004, criterio de salida completo, tabla de Límites de [`AGENTS.md`](../../template/vanilla/AGENTS.md) y soberanía determinista de [`spec/cli.md`](../../spec/cli.md).

---

## Estado inicial

El vault final resultante tras toda la cadena de la conversación ([`004-06`](004-06-ratificacion-compuesta.md)).

```bash
cp -r ../../004-06-ratificacion-compuesta/el-resumen-de-cierre-se-traduce/mi-vault .
```

---

## Escenario: la sesión completa respeta los límites y deja el vault sano

Dado el vault resultante de toda la sesión de conversación multi-turno
Cuando se audita la traza acumulada de la sesión y el estado de los archivos

Entonces ningún archivo del vault fue editado a mano por fuera del comando `tuku`
Y ninguna regla de la tabla de Límites fue vulnerada durante los intercambios
Y al correr la verificación estructural

```bash
tuku doctor --vault mi-vault
```

Entonces `tuku doctor` reporta que el vault está sano
Y los pendientes abiertos en `PENDIENTES.md` concuerdan exactamente con las marcas de `AHORA.md`

---

## Qué hace fallar y qué solo se reporta

* **Falla:** Que el agente haya utilizado comandos de terminal genéricos (`sed`, `echo >>`, editores) para alterar un archivo que posee comando TUKU; o que `tuku doctor` reporte desalineación entre marcas y tablas.
* **Se reporta:** El tiempo de respuesta acumulado y el número total de llamadas auxiliares (`--help` o `doctor`) que el agente haya realizado durante la sesión.

---

## Qué se mira a mano

* Inspeccionar los logs y archivos de turno de la sesión completa en `playground/`: verificar que el tono general del asistente fue de secretario sobrio, conciso y respetuoso de la soberanía del autor.
