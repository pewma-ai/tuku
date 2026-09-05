# Reglas de este repositorio

Este es un vault de TUKU: una bitácora de la vida de su autor, en archivos de texto que se pueden leer y editar sin ningún programa especial.

Estas reglas valen para cualquiera que opere el vault, sea una persona o un agente.

## Qué es cada archivo

| Archivo | Qué guarda |
| --- | --- |
| `AHORA.md` | El ciclo en curso. Aquí se escriben las entradas del día. |
| `PENDIENTES.md` | Todo lo que está abierto y sin cerrar. |
| `LIBRO-DE-ESTILO.md` | Cómo se escribe aquí. Es tuyo y crece con el uso. |
| `ambitos/` | Los frentes de tu vida, uno por carpeta o archivo. |
| `notas/` | Ideas y notas que no pertenecen a un día. |
| `reglas/` | Configuración y reglas de las automatizaciones. |
| `bitacoras/` | Los ciclos ya cerrados. Aparece cuando cierres el primero. |

**MAYÚSCULAS es de TUKU, minúsculas es tuyo.** Sirve para saber de un vistazo qué puedes renombrar.

## Lo que nunca se toca

`AHORA.md`, `bitacoras/`, `PENDIENTES.md`, `ambitos/` y `notas/` son el conjunto canónico: lo que escribiste tú. Nada los regenera y nada los sobreescribe sin que lo apruebes.

Todo lo demás se puede borrar y volver a generar desde ellos.

## Cómo se escribe una entrada

```text
- HH:MM - [[ambito]] **clasificacion**: cuerpo
```

La hora y el cuerpo son obligatorios. El ámbito y la clasificación se ponen cuando aportan algo.

Tres marcas tienen efecto mecánico y conviene no usarlas para otra cosa:

| Marca | Qué hace |
| --- | --- |
| `**pendiente**` | Abre un pendiente. Su cuerpo se copia tal cual a `PENDIENTES.md`. |
| `~~(Hecho)~~` | Cierra un pendiente. Repite el mismo cuerpo, sin reescribirlo. |
| `**cadencia**` | Da de alta algo que se repite. |

Todo lo demás que escribas entre `**` es vocabulario tuyo y está en `LIBRO-DE-ESTILO.md`.

## Si eres un agente

- Propón, no ratifiques. Nada se escribe ni se archiva sin aprobación del autor.
- Registra el hecho, no la conversación. "Recuérdame" y "anota" van dirigidos a ti, no son parte de lo ocurrido.
- Escribe primero la entrada en `AHORA.md`. Recién después aplica sus consecuencias, releyendo lo escrito y no lo conversado.
- No preguntes lo que las últimas entradas ya responden.
- Silencio por defecto: no narres el mecanismo.

## Dónde vive el código

Este vault no contiene código. Las automatizaciones (janitors) se instalan aparte, en `~/.tuku/janitors`, y cada una documenta cómo hacer a mano lo que ella hace.

Si no están instaladas, el vault funciona igual. Cuesta más trabajo, y eso es todo.
