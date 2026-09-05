# spec · cadencias

> Una cadencia es una regla que emite algo con regularidad. Se justifica por el principio 7 de `../docs/principios.md`: vive donde aplica, no en un archivo central.

Vive **donde aplica**: en el ámbito o subdirectorio al que pertenece. Una cadencia de conversaciones individuales vive en `jefatura`; una de pagos mensuales vive en `personal`. La más cercana prevalece (ver `ambitos.md`).

Poner el alcance en la carpeta evita declararlo dentro de cada cadencia. El árbol ya lo dice.

Un janitor recorre el árbol y colecta las cadencias vigentes del autor en una vista única. Esa vista es **derivada**: la fuente son los archivos por ámbito.

## Formato de `CADENCIAS.md`

Uno por directorio. Contiene solo las cadencias de esa carpeta.

```markdown
## Gastos comunes del arriendo

**Cuándo:** día exacto 10, mensual
**Emite:** pendiente con fecha
**Texto:** pagar y enviar comprobante de gastos comunes a [[carmen-navarro]]

### Procedimiento
Pagar en el portal y enviar el comprobante por WhatsApp.

### Historia
- 2026-08-09: el comprobante se envía el mismo día. Dos veces quedó sin enviar y hubo cobro duplicado.
```

Tres campos son de máquina y dos son de persona:

| Campo | Para quién | Qué hace |
| --- | --- | --- |
| `Cuándo` | máquina | La condición que dispara |
| `Emite` | máquina | Qué tipo de cosa produce |
| `Texto` | máquina | El cuerpo literal a inyectar, sin redactar nada |
| `Procedimiento` | persona | Cómo se hace, con el detalle que haga falta |
| `Historia` | persona | Reglas aprendidas, fechadas. Por qué la cadencia es así |

`Texto` es literal a propósito: emitir no necesita LLM, igual que abrir un pendiente.

`Historia` es lo que evita que una cadencia se simplifique por parecer arbitraria. Una línea con fecha explicando qué salió mal vale más que la regla sola.

## Ciclo de vida

**Al abrir un ciclo** se colectan las cadencias vigentes y lo que emiten cae en el día que corresponde de `AHORA.md`.

**Al especificar una cadencia nueva**, tres cosas:

1. Se registra como entrada `**cadencia**` en la bitácora.
2. Se escribe la cadencia en el ámbito que corresponde.
3. Se verifica la bitácora actual y **se modifica si es necesario**, para incluir lo que la cadencia nueva emite en el día que corresponde del ciclo en curso.

## Un solo destino de emisión

Una cadencia emite un **pendiente con fecha**, y aparece en el día correspondiente de `AHORA.md` por la transclusión que ya existe (ver `pendientes.md`). No hay un segundo destino de emisión distinto de los pendientes.

## El trigger no es solo calendario

Varias cadencias reales dependen del tipo de ciclo, no solo de la fecha: *"jueves de la semana de descanso"*, *"semana de descanso que incluya algún día entre el 15 y el 31"*. Así que resolver cadencias necesita conocer el ciclo, no basta con un almanaque.

Dos trampas conocidas: los rangos que cruzan el borde de mes (*"entre el 31 y el 4"*, y no todos los meses tienen 31), y que varias cadencias caigan el mismo día. Emisiones múltiples en un día son normales, no anomalía.

## Dos consecuencias de implementación

**Escribe hacia atrás.** El paso 3 del ciclo de vida es el único lugar del diseño donde una consecuencia modifica un ciclo ya abierto. Todo lo demás avanza hacia adelante. La modificación alcanza desde HOY hasta el fin del ciclo: los días ya transcurridos no se tocan, porque a un día que ya pasó no se le puede agregar algo por hacer.

**Obliga a idempotencia.** Como una cadencia puede inyectarse al abrir el ciclo y otra vez al especificarse, sembrar tiene que ser idempotente: inyectar dos veces la misma cadencia no puede duplicar lo emitido.

## No entra

- **Inferir cadencias implícitas del histórico.** Eso es inferencia semántica y pertenece a una fase posterior de implementación (ver `../devel/que_implementar.md`), no al modelo aquí especificado.
- **Las alertas sobre pendientes críticos.** Sigue abierto si son un janitor propio o una forma de implementar una cadencia.
