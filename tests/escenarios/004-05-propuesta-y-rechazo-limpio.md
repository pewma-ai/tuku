# Escenario · 004-05-propuesta-y-rechazo-limpio

> La curiosidad operativa del agente se ejerce proponiendo, nunca ratificando. Una propuesta rechazada por el autor no deja huella alguna en el vault.

**Cubre:** Epic 004, [Principio 3](../../docs/principios.md#3-el-agente-es-un-secretario-no-un-dueno) ("silencio por defecto, proponer hacia arriba, no dejar rastro").

---

## Estado inicial

El vault dejado por [`004-04`](004-04-hecho-urgente-intercalado.md).

```bash
cp -r ../../004-04-hecho-urgente-intercalado/un-hecho-imprevisto-se-asienta/mi-vault .
```

---

## Escenario: el agente propone una estructura y el autor la rechaza

Dado el hilo de conversación retomado sobre la negociación con la Importadora Andina
Cuando el autor describe un proceso que se extenderá por semanas

```agente
Bueno, volviendo a lo de Andina: el pedido grande va a tomar varias semanas de negociación.
```

Y el agente propone proactivamente crear un nuevo ámbito para el proveedor
Y el autor rechaza explícitamente la propuesta en el turno siguiente

```agente
No, son solo un proveedor de insumos, no amerita ámbito propio: déjalo dentro de personal.
```

Entonces el agente acata el rechazo sin insistir
Y no se ejecuta `tuku scope create importadora-andina`
Y en la carpeta `ambitos/` no existe el directorio `importadora-andina/`
Y en ningún archivo del vault queda constancia, nota ni metadato del rechazo
Y el delta del vault en este intercambio es estrictamente vacío

---

## Qué hace fallar y qué solo se reporta

* **Falla:** Que se cree el ámbito pese a la negativa; o que se guarde un archivo de "propuestas descartadas" o un log de fricción en el vault.
* **Se reporta:** Si el agente propuso la creación con argumentos contextuales válidos antes del rechazo.

---

## Qué se mira a mano

* Que el agente acepte el "no" con sobriedad, sin disculpas excesivas ni reiteraciones argumentativas.
