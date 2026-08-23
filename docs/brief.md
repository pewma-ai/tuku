# TUKU: brief

> Documento fundacional. Las especificaciones en `spec/` y las decisiones en `decisiones/` se justifican por referencia a este documento y a `principios.md`. Si una decisión futura no puede derivarse de lo que aquí se afirma, o este brief está incompleto, o la decisión está equivocada. Ambos casos merecen un ADR.

## 1. Qué es

TUKU es un sistema de gestión personal para una persona que pertenece a múltiples organizaciones a la vez. Registra lo que hace, recuerda lo que olvida, sostiene lo que concluye, y convierte esa acumulación en planes, alertas y reportes.

Gestionar una vida así ocurre casi entera dentro de la cabeza: recordar, comparar y decidir qué toca ahora es el sistema 2 de Kahneman, trabajo deliberado y caro del que no hay mucho al día. TUKU baja esa carga a archivos para devolver la atención a lo que sí la merece.

El nombre viene de *tukulpan*, en mapudungun: recordar, traer a la memoria. Esa es la promesa exacta: **lo que entró a TUKU vuelve solo cuando corresponde**, sin que nadie tenga que acordarse de acordarse.

TUKU implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal. Producto y metodología se versionan por separado: la metodología describe cómo se gestiona; TUKU es una herramienta que la ejecuta.

## 2. Para quién

Una persona con vida multidimensional: trabajo formal, emprendimientos paralelos, familia, responsabilidades cívicas. Cada dimensión tiene sus ritmos, compromisos y vocabulario, y ninguna herramienta que usa en una ve a las demás.

El **autor** de referencia puede ser un desarrollador que opera todo por terminal o alguien como la dueña de una PyME de insumos escolares, con clientes que tienen sus propios ciclos (vendí lápices hoy, ofrecer reposición en tres meses) y hoy todo vive en su cabeza y en cuadernos. Ninguno de los dos es el centro del diseño: el sistema se piensa para ambos por igual.

El sistema habla el idioma del autor. La primera lengua es el español, y el vocabulario del día a día va siendo recordado.

**Nomenclatura.** La persona dueña del sistema es el *autor*: escribe un libro, no opera un software.

## 3. Archivos de texto y agentes que los mantienen

TUKU son archivos Markdown, y nada más. Son del autor, se leen con cualquier editor, viajan en un pendrive y siguen siendo legibles cuando esta herramienta ya no exista. Se ven en Obsidian, local o por web, y siempre se pueden corregir a mano.

Sobre esos archivos trabajan agentes de inteligencia artificial, y ahí se juega que el sistema se use: uno les cuenta lo que hizo y ellos ordenan, clasifican, recuerdan y redactan borradores. Mantener el sistema (que es justamente lo que hace abandonar todos los sistemas) deja de ser trabajo del autor.

Eso es lo que TUKU ofrece: cualquiera queda gestionando como un project manager disciplinado, sin haber estudiado gestión ni haberse vuelto una persona ordenada.

Lo esencial no depende de los agentes: todo lo que importa queda escrito en un archivo, no en su memoria, y el sistema entero se puede operar sin ellos.

## 4. El marco conceptual

Gestionar tiene la misma forma siempre, en un observatorio y en un almacén:

```
objetivos generales → recursos → capacidad → plan → acciones → aprendizajes
```

Los aprendizajes alimentan los objetivos del ciclo siguiente. TUKU existe para sostener ese lazo: sin sistema, las acciones se registran mal, los aprendizajes se pierden y cada ciclo empieza de cero.

Este lazo es el **porqué** del sistema, no una capa de artefactos. TUKU no pretende hoy generalizar la estrategia a todos los casos de uso; lo que sí sostiene, con experiencia de campo, es el ciclo y sus cadencias (ver `spec/cadencias.md`).

Lo que sostiene un lazo así son insumos bien elegidos, como en la escritura o la música: un puñado de signos, y todo lo demás sale de cómo se combinan. La riqueza no está en cuántos elementos hay, sino en cuántas relaciones admiten entre sí.

## 5. El modelo, en una página

**La bitácora es la primitiva única.** Hechos con fecha y hora, inmutables. Lo que ya ocurrió no se corrige: si hace falta enmendar, se escribe otra entrada. Todo lo demás se deriva de aquí.

**`PENDIENTES.md` es lo que falta.** Un pendiente nace de una entrada de bitácora y muere en otra. Es la fuente de verdad *operativa* (donde se consulta y se trabaja) mientras la bitácora sigue siendo la fuente *de origen*. Mientras un pendiente espera, pesa, y ese peso es información.

**Las notas son lo que se entendió.** El espacio mental del sistema, donde una idea se desarrolla y queda una conclusión. Sin ritmo impuesto: surgen como en una conversación.

**Las entidades son el objeto de trabajo**: el cliente, el proyecto, la persona. Lo que uno hace con un cliente se parece a lo que hace con el siguiente, y eso se guarda como **prácticas** asociadas a la entidad: un cliente nuevo llega con una forma conocida de gestionarlo.

**El ciclo es el período** que uno está viviendo (por defecto la semana). Abre con una **intención** y cierra con un **reporte**. El reporte es la memoria: nadie va a releer diez años de entradas sueltas, y la pregunta por 2016 se responde leyendo lo que se escribió al cerrar 2016. El detalle crudo no se borra nunca.

**Las cadencias** hacen aparecer tareas cuando corresponde, sin que nadie se acuerde: abrir la semana, cerrarla, pagar los impuestos el día 1. Cuelgan del calendario, de un hecho de la bitácora, o de las prácticas de una entidad. La más valiosa es la que se dispara **porque no pasó nada** (un cliente sin contacto hace cuatro semanas, un proyecto detenido). Nadie recuerda aquello que dejó de hacer, y ningún cuaderno lo tiene. De ahí sale el mejor momento del producto: abrir un ciclo y encontrarse con lo que uno había olvidado que se había prometido.

Y entonces conversan entre sí. Un hecho que se repite termina pidiendo una explicación, y ahí aparece una nota. Una conclusión que no produce ningún compromiso rara vez era una conclusión. Una tarea que se cierra vuelve a la bitácora convertida en hecho. Una venta de hoy es el aviso de una llamada en tres meses. Ninguna de esas relaciones hubo que inventarla.

## 6. El primer día

Un repositorio recién creado no tiene historia, y el valor de TUKU crece con la historia. La respuesta no es un asistente de configuración: es invertir la carga.

El primer día el autor ve los días restantes de su ciclo y un chat que pregunta **¿qué anotaremos hoy?**. Registra, por texto o por voz. La estructura emerge: los agentes ven nombres que se repiten y proponen entidades, ven pagos que se repiten y proponen cadencias, y el autor aprueba con una palabra.

El onboarding no es una feature: es el sistema funcionando sobre un repositorio vacío.

Las **cadencias de sistema** (apertura, cierre, higiene) vienen propuestas y son editables, de modo que el primer cierre de ciclo ocurre solo aunque el autor no haya configurado nada. Lo mismo con el **libro de estilo por defecto**: se parte con uno y se corrige con el uso (`plantillas/libro-de-estilo-por-defecto.md`).
