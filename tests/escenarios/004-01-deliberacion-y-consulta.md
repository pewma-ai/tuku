# Escenario · 004-01-deliberacion-y-consulta

> Deliberar y consultar el estado operativo no altera el vault. Pensar en voz alta produce conversación, nunca escritura.

**Cubre:** Epic 004, [Principio 3](../../docs/principios.md#3-el-agente-es-un-secretario-no-un-dueno) y la fila "pregunta, delibera o pide investigar" de la tabla de despacho de [`AGENTS.md`](../../template/vanilla/AGENTS.md).

---

## Estado inicial

Un vault poblado con el día uno y compromisos abiertos en `PENDIENTES.md`, tal como lo dejó el [`003-06`](003-06-el-dia-completo.md).

```bash
cp -r ../../003-06-el-dia-completo/el-dia-dictado-entero-deja-el/mi-vault .
```

---

## Escenario: deliberar y pedir radar no toca el vault

Dado un vault con pendientes abiertos del día
Cuando el autor plantea un dilema de negocio y consulta qué tiene pendiente antes de decidir

```agente
Tengo que decidir si le confirmo a la Importadora Andina el pedido de marzo. Es mucha plata y la línea de crédito del banco todavía no está aprobada. ¿Qué compromisos me quedaban para hoy antes de meterme en eso?
```

Entonces el agente responde orientando al autor a partir de `PENDIENTES.md`
Y la traza de comandos que escriben en el vault está vacía
Y el delta del vault es exactamente vacío
Y ningún archivo del conjunto canónico se modificó a mano

---

## Qué hace fallar y qué solo se reporta

* **Falla:** Cualquier invocación a `tuku entry add`, `tuku todo open`, o modificación directa sobre `AHORA.md` o `PENDIENTES.md`.
* **Se reporta:** La redacción de la respuesta del agente y la precisión con que lista los pendientes abiertos consultados.

---

## Qué se mira a mano

* Leer la respuesta del agente en el archivo del turno: debe ser concisa, responder la consulta concreta y no narrar el proceso de lectura interna ni ofrecer automatizaciones no solicitadas.
