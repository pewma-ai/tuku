# Proceso: registro conversacional

> Ejecutable por un humano con un editor de texto, o por un agente de inteligencia media
> (P2). Convierte lenguaje natural en entradas de bitácora o tareas canónicas.

## Cuándo

Cuando el usuario quiere registrar algo sin preocuparse por el formato exacto: una reunión,
una decisión, un hito, una tarea nueva. El motor convierte la descripción a forma canónica.

## Formas de entrada aceptadas

El texto puede mezclar varios elementos en una sola frase:

```
Reunión con [colegio-san-marcos](../entidades/trabajo/colegio-san-marcos.md):
acordamos enviar propuesta esta semana #hito

Hay que llamar a Juan sobre el contrato — 1h, antes del viernes

Decidí no renovar la suscripción a X: muy poco uso #decision
```

## Pasos (modo `--sin-agente`)

1. **Detectar el tipo de primitiva.** Heurísticas simples:
   - Contiene verbo de acción urgente o fecha → **tarea**.
   - Describe un hecho pasado o una decisión → **entrada de bitácora**.

2. **Extraer la entidad.** Si el texto contiene `[id](ruta)`, usarla directamente.
   Verificar que el `id` existe en `entidades/` del perfil (**verificación factual**).

3. **Extraer clasificación.** Si el texto contiene `#hito`, `#decision`, `#senal` o `#msg`,
   mapear al valor canónico de `config.yaml → clasificaciones`.

4. **Construir la primitiva canónica:**
   - Entrada: `- (<hora>) [<id>](<ruta>) **<Clasificación>:** <texto> #<tags>`
   - Tarea: `- [ ] <hoy> 1h <entidad> - - - tuku-registrar <texto> ^t-<id>`

5. **Verificar que todos los ids citados existen.** Si alguno no existe en `entidades/`,
   el registro se rechaza con mensaje claro — no se inventa ni se silencia (capa factual).

6. **Escribir al canónico:**
   - Entradas → `entradas/YYYY-MM.md` del mes actual.
   - Tareas → `tareas/tareas.md`.

## Pasos adicionales (modo con agente)

Con agente, el paso 1 (detección de tipo) y la redacción final se resuelven por el LLM,
usando el tesauro vivo como contexto para sugerir ids de entidades existentes.

## Verificación

- La entrada/tarea escrita pasa el parser (`Entry.parse_line` / `TukuTask.parse_line`).
- Todos los ids de entidad citados existen en `entidades/`.
- `tuku janitor` no reporta violaciones E1–E7 / T1–T8.

## Equivalente manual

Abrir `entradas/YYYY-MM.md` o `tareas/tareas.md` y escribir directamente en formato
canónico. El proceso `registro-conversacional.md` es solo un atajo de conveniencia.
