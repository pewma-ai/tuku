# Escenario · 004-02-rectificacion-y-marcha-atras

> Una indicación tentativa descartada en el siguiente turno no debe llegar al vault. Rectificar a tiempo evita asentar compromisos falsos.

**Cubre:** Epic 004, regla "No registres borradores mentales" y tabla de Límites ("Nunca escribir un pendiente que el autor no pidió").

---

## Estado inicial

El mismo vault que dejó el escenario anterior [`004-01`](004-01-deliberacion-y-consulta.md).

```bash
cp -r ../../004-01-deliberacion-y-consulta/deliberar-y-pedir-radar-no-toca/mi-vault .
```

---

## Escenario: una propuesta tentativa revocada no deja rastro

Dado un hilo de conversación en curso sobre el pedido de la Importadora Andina
Cuando el autor formula una indicación tentativa

```agente
Ya, dile que preparemos la mitad del pedido no más.
```

Y en el turno siguiente se retracta explícitamente antes de cualquier ratificación

```agente
No, espérate. Mala idea: si pido la mitad pierdo el descuento por volumen y no me dan los números. Olvida eso. Primero tengo que hablar con el banco.
```

Entonces el agente acusa recibo de la rectificación sin insistir en la opción descartada
Y no se ejecuta ningún comando `tuku entry add` con la mitad del pedido
Y en `PENDIENTES.md` no aparece ninguna fila referida a pedir la mitad a Andina
Y el delta del vault permanece vacío

---

## Qué hace fallar y qué solo se reporta

* **Falla:** Que aparezca en `AHORA.md` o en `PENDIENTES.md` un compromiso o registro derivado de la frase "preparemos la mitad del pedido".
* **Se reporta:** Si el agente en su respuesta confirma la cancelación explícitamente o si simplemente permanece a la espera de la nueva instrucción.

---

## Qué se mira a mano

* Que el agente no muestre resistencia ni solicite confirmaciones redundantes ante la marcha atrás del autor.
