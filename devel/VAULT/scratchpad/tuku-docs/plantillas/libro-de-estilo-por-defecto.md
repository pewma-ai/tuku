---
titulo: Libro de estilo
autor: (tu nombre)
version: 1
---

# Libro de estilo

> Este es el documento que gobierna tu libro. Lo escribes tú; los agentes solo **proponen** cambios y tú los ratificas. Todo lo demás del sistema —las reglas que siguen los agentes, la configuración de los procesos automáticos— se genera desde aquí.
>
> Viene con valores por defecto. Corrígelos con el uso: es lo que se espera.

## Parte I — Reglas de TUKU

Estas reglas son del sistema y conviene no cambiarlas.

### Cómo se escribe en la bitácora

Una línea por hecho, con esta forma:

```
HH:mm [[área]]: **tipo** — lo que pasó
```

Ejemplo:

```
ventas: progreso — despaché el pedido de la [[Escuela San Marcos]], quedó pendiente la factura
```

Los hechos llevan fecha y hora, y **no se corrigen**. Si algo quedó mal escrito o cambió, se escribe otra línea.

### Tipos de entrada

| Tipo | Cuándo usarlo |
|---|---|
| `señal` | Algo que notaste y todavía no significa nada |
| `fricción` | Algo que costó más de lo que debía |
| `progreso` | Avance sobre algo en curso |
| `decisión` | Una elección tomada, con su motivo |
| `nota` | Cuando ninguno de los anteriores calza |

Si empiezas a usar un tipo que no está en esta lista, el sistema lo va a aceptar igual y en algún momento te va a preguntar qué quisiste decir, para agregarlo aquí.

### Cómo se enlaza

- `[[nombre]]` para mencionar a alguien o algo que tiene su propia página.
- `![[nombre]]` para **traer** el contenido de otra página adentro de esta. Se usa para no escribir lo mismo dos veces.

### Ver además

Al pie de las páginas que vas a volver a leer —una entidad, un ámbito, una nota tuya— va una lista de enlaces **con el motivo de cada uno**. El motivo importa tanto como el enlace: dentro de unos años eso es lo que te va a devolver la idea.

No lleva "ver además" nada que se genere solo: pendientes, resúmenes, ni las entradas de bitácora.

### Archivos EN MAYÚSCULAS

Son los de consulta rápida, y los mantiene el sistema, no tú:

| Archivo | Qué contiene |
|---|---|
| `PENDIENTES.md` | Todo lo que falta, y solo lo que falta |
| `CONTEXTO_RECIENTE.md` | Qué está pasando ahora |
| `RADAR.md` | Lo que conviene tener a la vista |

Cada uno empieza explicando qué es y quién lo actualiza, para que cualquiera que llegue nuevo —una persona o un agente— entienda de inmediato.

### El ciclo

Por defecto, la semana. Abre con una **intención** —qué corresponde hacer— y cierra con un **reporte** —qué pasó—. El reporte es lo que vas a leer dentro de años; el detalle queda igual guardado, pero nadie relee detalle.

---

## Parte II — Tus convenciones

Esta parte es tuya. Es lo que hace que el sistema hable tu idioma.

### Sobre ti

Ver `SOBRE-EL-AUTOR.md`: quién eres, a qué te dedicas y cómo prefieres que te hablen. Se edita conversando con un agente. Si el sistema nota que en la práctica haces algo distinto de lo declarado, te lo va a advertir — no lo va a cambiar solo.

### Tipos de entidad

Los objetos sobre los que gestionas. Por defecto:

<!-- transcluir aquí el fragmento correspondiente de tuku.yaml -->
![[tuku.yaml#entidades]]

Empiezas con `persona`, `proyecto` y `ámbito`. Si gestionas clientes, agrégalos; si trabajas por casos, también. Se amplía con el uso.

### Ámbitos y áreas

<!-- transcluir aquí el fragmento correspondiente de tuku.yaml -->
![[tuku.yaml#ambitos]]

### Prácticas por tipo de entidad

Lo que sueles hacer con un cliente, un proyecto o una persona. Cuando aparece uno nuevo, llega con esta forma ya puesta, incluidas sus cadencias.

<!-- transcluir aquí el fragmento correspondiente de tuku.yaml -->
![[tuku.yaml#practicas]]

---

## Parte III — Mantención del corpus

Enlaces a los procesos que sostienen el sistema. No necesitas operarlos, pero sí saber que existen y para qué son.

| Proceso | Propósito |
|---|---|
| [Configuración (`tuku.yaml`)](configuracion.md) | Un solo archivo con los valores de este libro de estilo. No se edita directo: se edita aquí y el sistema lo verifica. |
| [Janitors](janitors.md) | Procesos automáticos que ordenan, proyectan pendientes, generan resúmenes y avisan de inconsistencias. |
| [Agentes](devel/VAULT/scratchpad/tuku-docs/plantillas/procesos/agentes.md) | Quiénes son, qué hace cada uno y qué pueden hacer sin preguntarte. |
| [Autoría](autoria.md) | Cómo el sistema distingue lo que escribiste tú de lo que redactó una IA. |

### Reglas de coherencia

Las convenciones de este libro, escritas de forma que se puedan verificar. Cada una declara si la revisa un proceso automático o un agente.

| Regla | Quién la aplica |
|---|---|
| Toda entrada de bitácora tiene fecha, hora, área y tipo | Janitor |
| Todo pendiente en `PENDIENTES.md` tiene una entrada de bitácora que lo originó | Janitor |
| Todo wikilink apunta a una página existente | Janitor |
| Las páginas curadas tienen "ver además" con motivo | Agente |
| Un pendiente cerrado corresponde efectivamente al que se abrió | Agente |
