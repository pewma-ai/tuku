# spec · entidades y prácticas

Las entidades son **el objeto de trabajo**: el cliente, el proyecto, la persona, el asunto sobre el que se gestiona. Las entradas de bitácora las referencian con wikilinks.

## Tipos definidos por el autor

Los tipos de entidad **son propios de cada autor** y viven en su libro de estilo, no en el spec general. Para uno serán `persona` / `proyecto` / `ámbito`; para otro, `persona` / `cliente` / `empresa`.

**Sin wizard inicial** — eso es configuración disfrazada. Se parte con un set mínimo predefinido y se amplía con el uso.

## La página en blanco

Quien escribe en un cuaderno se da cuenta de que cierta entidad ya merece su propia página, y la aparta. Los agentes hacen lo mismo: leen entre líneas y **proponen**.

Patrón **sembrar y corregir**: el agente propone un borrador desde el texto crudo; el autor valida o corrige con una palabra.

Nunca se menciona la palabra *entidad* al autor. La conversación es natural: *veo que mencionas seguido a la ferretería del centro, ¿le abro una página?*

## Prácticas

Lo que uno hace con un cliente se parece a lo que hace con el siguiente. Eso se guarda como **prácticas** asociadas al tipo de entidad: un cliente nuevo llega con una forma conocida de gestionarlo, incluidas sus cadencias.

Las prácticas son la mejor fuente de contexto organizacional porque son **soberanas**: destiladas de lo que el autor efectivamente hizo, no del conocimiento general de un modelo. Cuando ambas fuentes coexisten, se distinguen por su marca de procedencia (ver `corpus.md`).

## Estructura del archivo

Un archivo por entidad, con secciones tipadas. El frontmatter declara al menos el tipo y el estado; el cuerpo acumula lo que se sabe, y el pie lleva "ver además".

Las vistas —pendientes abiertos, últimas entradas de bitácora que la mencionan— son generadas por janitor, no escritas a mano.
