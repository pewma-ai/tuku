# Escenario · 004-04-hecho-urgente-intercalado

> Un hecho fortuito que interrumpe una deliberación se registra de inmediato sin desarmar el hilo de conversación anterior.

**Cubre:** Epic 004, regla "Un hecho dictado ya viene aprobado: escríbelo" frente a un contexto conversacional vivo.

---

## Estado inicial

El vault resultante de la aclaración en [`004-03`](004-03-desambiguacion-en-dos-turnos.md).

```bash
cp -r ../../004-03-desambiguacion-en-dos-turnos/el-agente-pregunta-en-el-turno-1/mi-vault .
```

---

## Escenario: un hecho imprevisto se asienta sin perder el contexto

Dado un diálogo donde se venía discutiendo el pedido de marzo con la Importadora Andina
Cuando el autor interrumpe abruptamente con un hecho urgente ocurrido en el momento

```agente
Espérate, me acaba de timbrar el flete con las cajas de témperas. Llegaron tres cajas rotas y manchadas, voy a tener que reclamar al proveedor.
```

Entonces el agente traduce el hecho inmediato a comando de bitácora

```text
tuku entry add --day 2026-08-12 --hour <hora> --scope personal \
  --body "**pendiente**: reclamar al proveedor por tres cajas de témperas rotas y manchadas"
```

Y queda registrado el hecho con su hora en `AHORA.md`
Y queda abierto el compromiso en `PENDIENTES.md`
Y en el turno posterior el agente está en condiciones de retomar la conversación sobre Andina sin mezclar ambos frentes

---

## Qué hace fallar y qué solo se reporta

* **Falla:** No registrar el reclamo de las témperas por considerarlo parte de la charla previa; o registrarlo mezclado en el ámbito de Andina si no correspondía.
* **Se reporta:** La clasificación abierta asignada al hecho y la redacción del cuerpo del reclamo.

---

## Qué se mira a mano

* Que el agente confirme brevemente el registro del hecho urgente sin sermones ni diagnósticos innecesarios.
