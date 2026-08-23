# ADR 0005 — Las zonas derivadas no se hacen read-only: se detecta la divergencia

## Contexto

Las zonas derivadas dentro de un compuesto —página de entidad, plan del ciclo— son generadas
por el motor y en principio no deberían editarse a mano: si el usuario las edita y el janitor
las regenera después, el trabajo se pierde en silencio.

La solución obvia es proteger esas zonas haciéndolas read-only a nivel de sistema de
archivos (`chmod 444`). Funciona sin instrumentación adicional, es determinista, y el sistema
operativo se encarga de impedir la edición accidental.

Su costo es que contradice el contexto de uso. El usuario principal trabaja en Obsidian,
donde read-only a nivel de sistema de archivos hace el archivo inutilizable en el editor.
Más en general, el principio de operabilidad manual (P2,
[`docs/brief.md`](../brief.md#3-principios)) exige que el sistema funcione con un editor de
texto cualquiera: un archivo que no se puede abrir y editar rompe ese principio. Y el hábito
de edición directa —corregir una línea de redacción en la zona derivada porque se ve mal—
es legítimo y no debería prohibirse.

## Decisión

**Las zonas derivadas no se hacen read-only.** En cambio, cada zona derivada lleva un hash
de las fuentes que la produjeron:

```
<!-- tuku:derived id=bitacora-entidad hash=a1b2c3 -->
…contenido generado…
<!-- /tuku:derived -->
```

Antes de regenerar una zona, el janitor de build compara el contenido actual contra el hash
registrado. Si divergen —porque el usuario editó dentro de la zona— el motor **pregunta
antes de sobrescribir**. El usuario puede conservar su edición manual o aceptar la
regeneración.

Editar ortografía o redacción dentro de una zona derivada es válido y no rompe nada. Solo
significa que la próxima corrida del janitor pedirá confirmación. **La única acción que el
motor nunca hace en silencio es sobrescribir contenido que el usuario modificó.**

## Consecuencias

**A favor.**

- El flujo de trabajo en Obsidian no cambia. El usuario edita donde quiera, sin pensar en
  qué zonas son derivadas.
- La pérdida de trabajo por regeneración accidental es imposible sin confirmación explícita.
  La pregunta del motor es la única intervención necesaria.
- Un `git commit` antes de cualquier corrida de janitor es la red de seguridad definitiva.
  `tuku doctor` puede listar las zonas con hash divergente como información de estado, no
  como error bloqueante.

**En contra, y aceptado.**

- **El usuario puede editar una zona derivada sin saber que lo es**, especialmente si no lee
  los comentarios HTML —que son invisibles en Obsidian—. La primera vez que el motor pregunta
  puede ser sorpresiva. Se mitiga con el estilo visual que cada renderizador puede aplicar
  a las zonas derivadas, pero el riesgo de confusión no desaparece.
- **La detección por hash añade complejidad al janitor de build**: no es solo "generar y
  escribir", sino "leer, comparar, preguntar si hace falta, escribir". Es complejidad
  necesaria y justificada, pero complejidad al fin.
- **El hash puede fallar si el formato de la zona cambia** entre versiones del motor: el
  contenido sería "el mismo" semánticamente pero diferente en bytes, lo que dispararía la
  pregunta en cada perfil existente tras una actualización. Se mitiga normalizando el
  contenido antes de calcular el hash (espacios finales, saltos de línea), pero requiere
  atención en las migraciones.

## Estado

`aceptado`
