# Reglas de tests/

Las capas, sus límites y cómo se corre la suite están en [`README.md`](README.md): léelo antes de escribir un test.

## Lenguaje

- Un escenario y su test dicen **qué verifican**, nada más. Concisos, directos, sin voseo.
- **Sin historia:** nada de "antes era", "se fundió", "venía del", fechas de cambios ni escenarios borrados. La historia va en [`../devel/iteraciones/`](../devel/iteraciones/) y en el commit.
- **Sin justificar de más:** una sección "Por qué existe" o "Qué prueba, y qué no" sobra si los pasos ya lo dicen. Se deja una nota solo si sin ella el test no se entiende.
- **El docstring de módulo no repite el `.md`:** qué afirma, en una a tres líneas, y cómo se corre.
- **Un docstring de test** solo cuando la aserción no se explica sola.

## Sin tests de más

- Cada test afirma algo que ningún otro afirma. Si dos se solapan, se funden.
- Lo determinista va en `unitarios/`: funciones puras, parsers, regex y validaciones, con caso nominal, vacío y malformado. Un escenario prueba solo lo que ve quien invoca `tuku`: códigos de salida, archivos y delta.
- Un escenario con agente no va en la base de una cadena: hereda de un vault determinista.
