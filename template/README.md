# template

> Estructuras iniciales en Markdown. Un directorio por variante. Esto no es documentación ni código: es el producto que recibe el autor, tal cual se copia.

Lo que hay dentro de una variante se copia tal cual. Nada de lo que está en este `README.md` viaja al vault del autor.

El mecanismo que copia una variante y resuelve sus fechas es código, no template: vive en [`../src/install_test_scenario.py`](../src/install_test_scenario.py).

## Variantes

| Variante | Para quién |
| --- | --- |
| [`vanilla/`](vanilla/) | Cualquiera. El mínimo operable a mano desde el primer día, y el más adaptable porque casi no supone nada sobre la vida de quien lo usa. |

Las variantes futuras se agregan como hermanas de `vanilla/`, nunca como capas encima. Si dos variantes comparten un archivo, se duplica: un template que hay que componer deja de ser copiable a mano y rompe el principio 1.

## Instalar a mano

Copiar el contenido de la variante a un directorio vacío y hacer tres cosas:

1. En `reglas/config.tuku.md`, poner la zona horaria.
2. En `AHORA.md`, escribir `desde` y `hasta` con las fechas del primer ciclo. Por defecto es semanal, que es el ritmo menos sorprendente para quien nunca ha usado esto.
3. En `AHORA.md`, reemplazar los encabezados de día por los días reales de ese rango.

Después de eso ya se puede escribir. Todo lo demás emerge del uso.

## Por qué se instala a mano

Porque tiene que poder hacerse sin TUKU. Un vault que solo se puede crear ejecutando un programa es un vault que dentro de veinte años no se puede crear. Cuando exista un instalador, hará exactamente estos tres pasos y ninguno más.
