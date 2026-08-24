# ADR 0012 — `blocked_until` en entidad carga dos causas bajo un campo

## Contexto

Una entidad puede estar temporalmente inactiva por dos razones distintas:

1. **Espera de un tercero**: se envió algo, se delegó algo, y la acción depende de que otro
   responda. El usuario no puede avanzar aunque quisiera.
2. **Decisión propia del ciclo**: el usuario movió la entidad a "No entra" al corregir el
   plan, y el motor escribe `blocked_until: <cycle_end>` automáticamente.

Estas dos razones tienen distinto origen y potencialmente distinta narrativa en el informe de
cierre: "esperé a un tercero" no es lo mismo que "decidí no tocarlo". Tener un campo único
oculta esa distinción.

La alternativa es separar causa y efecto: `status: paused`, `paused_until: <fecha>`,
`paused_reason: espera-terceros | decision-propia | no-entra-ciclo`.

## Decisión

**Se usa un solo campo `blocked_until`** para ambas causas. Es una simplificación aceptada.

El efecto en el motor es idéntico en los dos casos —silenciar las cadencias por ausencia
hasta la fecha indicada— y distinguir la causa no cambia ningún cálculo determinista. La
distinción importa solo para la narrativa del cierre, que es de familia semántica y puede
inferirla el agente del contexto si hace falta.

La separación en `paused_reason` queda disponible como decisión futura si la evidencia de
uso muestra que la distinción importa en la práctica.

## Consecuencias

**A favor.**

- Un campo menos en el front matter de cada entidad.
- La regla de silenciado es simple: si `blocked_until >= hoy`, no dispara. Sin lógica
  condicional por tipo de causa.

**En contra, y aceptado.**

- El informe de cierre no puede distinguir automáticamente entre "esperé a un tercero" y
  "decidí no tocarlo". El agente puede intentar inferirlo del contexto, pero sin garantía.
- Si en el futuro se necesita la distinción —por ejemplo, para métricas de cuánto tiempo se
  pasa esperando a terceros vs. pausando por decisión propia— el campo tendrá que partirse y
  será una migración.

## Estado

`aceptado`
