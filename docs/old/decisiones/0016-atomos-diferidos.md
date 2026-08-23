# ADR 0016 — Promoción de secciones a átomos: diferida hasta evidencia de necesidad

## Contexto

Las páginas de entidad pueden crecer: una sección de recursos de un proyecto grande puede
superar las dos páginas; un directorio médico puede necesitar aparecer en varios lugares a la
vez. Para esos casos, una sección podría "promoverse" a un archivo propio —un átomo— con
transclusión desde la entidad original.

Implementar átomos desde el principio tiene ventajas: las secciones grandes son manejables,
la transclusión evita duplicación, y la promoción es más limpia si el mecanismo existe desde
el principio.

## Decisión

**La promoción de secciones a átomos se difiere** hasta que haya evidencia concreta de que
una entidad real necesita esa capacidad.

El gancho está puesto sin costo: toda sección tiene un `id` estable en su marca
`<!-- tuku:editable id=descripcion -->`. Cuando la promoción sea necesaria, el archivo
propio puede recibir el mismo `id` y la transclusión se implementa sin tocar ninguna
referencia existente.

Lo que se evita ahora es la complejidad operacional de los átomos: un invariante extra
(átomos huérfanos detectables), un mecanismo de transclusión que los tres renderizadores
deben entender, y el riesgo documentado en el PRD de que el directorio `.atoms/` se
convierta en un cajón de sastre.

## Consecuencias

**A favor.**

- El motor de la primera versión no implementa transclusión, lo que simplifica los janitors
  de build.
- Si nunca aparece una entidad que lo necesite de verdad, la complejidad se evitó por
  completo.
- El `id` por sección ya resuelve la mitad del problema: identificar de qué sección se habla
  en una referencia.

**En contra, y aceptado.**

- Si una entidad crece mucho antes de que se implemente la promoción, la única opción es
  partirla en dos entidades distintas, lo que puede no tener sentido semánticamente.
- La transclusión diferida significa que quien implemente la feature en el futuro tendrá que
  entender el modelo de secciones marcadas, que para entonces puede llevar meses de uso y
  ser más difícil de cambiar.

## Estado

`aceptado`
