# TUKU, Project Brief

2026-08-01, jpgil & Claude Fable

> `docs/brief.md` · Documento fundacional. Las especificaciones en `spec/` y las decisiones
> en `docs/decisiones/` se justifican por referencia a este documento. Si una decisión
> futura no puede derivarse de lo que aquí se afirma, o este brief está incompleto, o la
> decisión está equivocada. Ambos casos merecen un ADR.

---

## 1. Qué es

TUKU es un sistema de gestión personal para una persona que pertenece a múltiples organizaciones a la vez. Registra lo que la persona hace, recuerda lo que la persona olvida, sostiene lo que la persona concluye, y convierte la acumulación de las tres cosas en planes, alertas y reportes.

Gestionar una vida así ocurre casi entera dentro de la cabeza. Recordar, comparar, decidir qué toca ahora es trabajo deliberado y caro, el sistema 2 de Kahneman, y de ese no hay mucho al día. TUKU baja esa carga a archivos para devolver la atención a lo que sí la merece.

El nombre viene de *tukulpan*, en mapudungun, recordar, traer a la memoria. Esa es la promesa exacta del sistema: **lo que entró a TUKU vuelve solo cuando corresponde**, sin que nadie tenga que acordarse de acordarse.

TUKU implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal. Producto y metodología son cosas distintas y se versionan por separado: la metodología describe cómo se gestiona; TUKU es una herramienta que la ejecuta.

### 1.1 Para quién

Para una persona con vida multidimensional: trabajo formal, emprendimientos paralelos, familia, responsabilidades cívicas. Cada dimensión tiene sus propios ritmos, compromisos y vocabulario, y ninguna herramienta de las que usa en una dimensión ve a las demás.

El usuario de referencia no es un desarrollador. Es alguien como la dueña de una PyME de insumos escolares: gestiona clientes, cada cliente tiene sus ciclos ("vendí lápices hoy, ofrecer reposición en tres meses"), y hoy todo eso vive en su cabeza y en cuadernos. El desarrollador que puede operar todo por terminal es un caso particular bienvenido, no el centro del diseño.

El sistema habla el idioma del usuario. La primera lengua es el español, y el vocabulario del día a día va siendo recordado.

### 1.2 Archivos de texto y un agente que los mantiene

TUKU son archivos Markdown, y nada más. Son del usuario, se leen con cualquier editor, viajan en un pendrive y siguen siendo legibles cuando esta herramienta ya no exista. Se ven en Obsidian, local o por web, y siempre se pueden corregir a mano.

Sobre esos archivos trabaja un agente, y ahí se juega que el sistema se use. Uno le cuenta lo que hizo y él ordena, clasifica, recuerda y redacta borradores. El trabajo de mantener un sistema, que es justamente lo que hace abandonar todos los sistemas, deja de ser del usuario.

Eso es lo que TUKU ofrece de verdad: cualquiera queda gestionando como un project manager disciplinado, sin haber estudiado gestión ni haberse vuelto una persona ordenada. La disciplina la pone el sistema.

Lo esencial, con todo, no depende del agente. Todo lo que importa queda escrito en un archivo y no en su memoria, y el sistema entero se puede operar sin él.

## 2. El modelo

### 2.1 El ciclo de gestión

Gestionar tiene la misma forma siempre, en un observatorio y en un almacén:

```
objetivos generales → recursos → capacidad → plan → acciones → aprendizajes
```

Los aprendizajes alimentan los objetivos del ciclo siguiente. TUKU existe para sostener ese lazo: sin sistema, las acciones se registran mal, los aprendizajes se pierden y cada ciclo empieza de cero.

Lo que sostiene un lazo así son insumos bien elegidos. Ocurre lo mismo con la escritura o con la música: un puñado de signos, y todo lo demás sale de cómo se combinan. La riqueza no está en cuántos elementos hay, sino en cuántas relaciones admiten entre sí y las conclusiones que se desprenden. 

### 2.2 Elementos principales
Cada uno responde una pregunta que los otros dos no saben responder.

**La bitácora guarda lo que pasó.** Una entrada es un hecho con fecha: vendí, llamé, viajé, me dijeron que no. Se escribe en el momento o al final del día, cuesta una línea. Lo que ya ocurrió no se corrige: si hace falta enmendar, se escribe otra entrada. El pasado no cambia.

**Las tareas guardan lo que falta.** Una tarea es un camino hacia un objetivo, pertenece a algo, y le corresponde un momento. Es el único de los tres que tiene una vida propia, nace, espera, se hace o se abandona. Mientras tanto pesa, y ese peso es información.

**Las notas guardan lo que se entendió.** Son el espacio mental del sistema: donde una idea se desarrolla y donde queda una conclusión. Pensar, el rodeo, los caminos descartados, la conversación con uno mismo no queda registrado en ninguna parte, en la nota se escribe solo lo que hará falta para retomar la idea más adelante y evita tener que volver a pensar lo ya pensado.

**La bitácora es el insumo**, lo que se hace todos los días. **Las tareas son el movimiento**, lo que el sistema empuja y vigila. **Las notas van en paralelo**, sin ritmo impuesto y surgen de manera natural, como en una conversación.

Y entonces empiezan a conversar. Un hecho que se repite termina pidiendo una explicación, y ahí aparece una nota. Una conclusión que no produce ningún compromiso rara vez era una conclusión. Una tarea que se cierra vuelve a la bitácora convertida en hecho. Una venta de hoy es el aviso de una llamada en tres meses. Ninguna de esas relaciones hubo que inventarla: estaban ya contenidas en tener estas tres piezas y no otras.

### 2.3 Dónde y cuándo

**El ciclo es el período** en que uno está viviendo, la semana de trabajo, las vacaciones. Todo lo que se registra pertenece a algo y ocurre en algún momento y situación. Cada ciclo comienza con una **intención**, qué debo hacer en base a mi realidad, y termina con un **reporte** de lo ocurrido. Pensar en ciclos genera introspecciones que llevan al aprendizaje.

El **reporte es la memoria**. Nadie va a releer diez años de entradas sueltas, lo que se conserva de un período largo no es su detalle sino su relato, y ese relato hay que escribirlo mientras se recuerda. Por eso cada ciclo se cierra con un **reporte**, y los reportes son la memoria de largo plazo. El detalle crudo no se borra nunca, pero la pregunta por el año 2016 se responde leyendo lo que se escribió al cerrar 2016.

**Las entidades son el objeto de trabajo**: el asunto, el cliente, el proyecto, la persona sobre la que se gestiona. Las entradas en la bitácora hacen referencia a las entidades: *hoy llamé al proveedor del norte, su envío está retrasado.* Las entidades no son todas distintas entre sí. Hay clientes, hay proyectos, hay personas, y lo que uno hace con un cliente se parece bastante a lo que hace con el siguiente. Esto se guarda como **prácticas** asociadas a una entidad y cuando se ingresa otro cliente ya hay una forma conocida de gestionarlo.

Las **cadencias** son tareas recurrentes que aparecen cuando corresponde, sin que nadie tenga que acordarse: abrir la semana con su plan, cerrarla con un reporte, pagar los impuestos los días 1. Pueden colgarse del calendario, de un hecho de la bitácora, o de las prácticas de una entidad, y en ese caso llegan solas con cada cliente nuevo.

La más valiosa es la que se dispara **porque no pasó nada**: un cliente al que no se le habla hace cuatro semanas, un proyecto que dejó de moverse. Nadie recuerda aquello que dejó de hacer, y ningún cuaderno lo tiene. De ahí sale el mejor momento del producto, abrir un ciclo y encontrarse con lo que uno había olvidado que se había prometido.

## 3. Principios

### P1, La arquitectura Markdown es el diseño; todo lo demás la sigue

Primero se diseña cómo viven los archivos: qué es canónico, qué es derivado, qué front
matter llevan, cómo se anidan. GUI, motor, deployment y agentes son consecuencias. Prueba
operativa: si la interfaz necesita lógica propia para que los archivos tengan sentido, la
arquitectura de archivos está mal.

La elección de Markdown es deliberada: texto plano legible a 1, 5 y 20 años,
versionable con Git, independiente de todo proveedor. Los datos del usuario deben
sobrevivir al motor, a PEWMA.AI y a la industria entera de LLMs.

### P2, Operable a mano; los agentes toman lo tedioso

Un usuario suficientemente disciplinado debe poder operar el sistema completo con un
editor de texto. Los procesos se escriben para ser ejecutables por un humano **o por un
agente de inteligencia media**, sin trucos de prompting, sin razonamiento de frontera.
Lo que se delega a agentes es lo tedioso o intensivo en tiempo, nunca lo esencial.

### P3, Determinismo primero, agencia al final

Todo lo que puede garantizarse con un script, se garantiza con un script (janitors). La coherencia del sistema se divide en tres familias con garante y costo distintos:

| Familia | Qué garantiza | Garante | Costo |
|---|---|---|---|
| **Invariante** | el repo cumple propiedades verificables | janitor | barato |
| **Derivación** | un derivado es función de sus fuentes: `D = f(A…)` | janitor de build | barato |
| **Semántica** | una propagación preserva sentido y legibilidad | agente LLM | caro |

El agente escribe reglas cuando el usuario habla y las interpreta al abrir el ciclo, pero
**nunca es quien las recuerda**. Un recordatorio que depende de la memoria de un modelo no
es un recordatorio.

### P4, La autoría es del usuario

Todo lo que el sistema guarda lo firma el usuario, lo haya tecleado o no. El agente redacta borradores, un plan, un reporte, una clasificación, y el usuario corrige con una línea o una palabra. Corregir es barato justamente para que la autoría no se ceda por comodidad: un texto que nadie revisó sigue siendo del usuario, y por eso conviene revisarlo.

### P5, La gobernanza es del usuario

Hay dos niveles: lo que ocurrió, entradas, tareas, movimiento de cada entidad, y lo que el usuario decidió, sus objetivos, su capacidad, las reglas que quiso darse. Abajo el sistema escribe sin pedir permiso, porque registrar un hecho no compromete a nadie. Arriba nunca escribe solo: puede advertir que un compromiso lleva un mes sin moverse, pero cambiar un objetivo o una regla exige que el usuario lo apruebe. El sistema propone hacia arriba; nunca decide hacia arriba.

### P6, Estructura mínima cerrada, interpretación abierta

El sistema valida muy poco: identidad estable, fechas, pertenencia, el estado de una
tarea. Todo lo demás, qué tipos de entidad existen, qué campos llevan, qué significa
"cliente grande", es territorio del usuario y del agente. Un tipo de entidad es una
plantilla más una lista de cadencias declaradas en Markdown; no hay editor de esquemas ni
catálogo cerrado.

### P7, De la lengua natural a la estructura

Un editor de texto ya es natural: se abre, se escribe una línea, se cierra. Esa línea suelta es entrada válida, se haya dictado, tecleado en la app o dejado a mano en un archivo, y el trabajo de TUKU es convertirla en lo que el sistema necesita, fecha, entidad, clasificación, tarea si la había. Nadie tiene que aprender comandos ni sintaxis para que su nota quede bien guardada. Prueba operativa: si contarle algo al sistema cuesta más que anotarlo en cualquier parte, el agente sobra.

## 4. Forma del sistema

### 4.1 Motor y perfil

Dos artefactos con ciclos de vida distintos, nunca mezclados:

- El **motor**: código, janitors, procesos, plantillas. Se instala vía pipx, se versiona
 por PEWMA.AI, vive fuera de los datos.
- El **perfil**: un repositorio Git por usuario con sus bitácoras, tareas, entidades y
 notas. Propiedad del usuario, portable, con su versión de esquema declarada.

Un motor sirve N perfiles. El diseño local es el diseño del servidor: pasar de la máquina del usuario a una VM multiusuario cambia dónde viven los perfiles, no el modelo.

### 4.2 Por dónde se toca

El perfil es un repositorio de archivos, y por eso admite varias puertas sin que ninguna sea la verdadera. Sentado frente al computador, la puerta es **Obsidian** sobre la carpeta del usuario: se lee, se enlaza y se corrige a mano, sin intermediarios. Servido por web, los mismos archivos se publican con **Quartz**, que da acceso desde cualquier parte a quien no quiere instalar nada. Y en el bolsillo está **Telegram**, para el caso más común de todos, contar algo en una línea mientras se camina.

La conversación la sostiene **Hermes**, un agente preconfigurado que llega sabiendo las reglas de TUKU y leyendo el repositorio del usuario. Es el mismo agente detrás de las tres puertas: la caja de chat de la web y el bot de Telegram hablan con él, no con tres implementaciones distintas.

Hermes no calcula: escribe lo que el usuario le cuenta y deja que los **janitors** del comando `tuku` hagan lo determinista, las derivaciones, las proyecciones, la higiene del repositorio. Esa división es la que permite cambiar de agente sin perder nada, porque lo que el sistema garantiza no depende de él.

Ninguna de estas piezas es TUKU. La verdad vive en los archivos de texto, y por eso Obsidian, Quartz, Telegram y Hermes se pueden reemplazar de a uno, en cualquier orden, sin migración.

### 4.3 Lo que el sistema produce solo

El usuario escribe poco. TUKU deriva mucho, porque casi todo lo que uno querría tener escrito ya está implicado en lo que contó.

Ciertos momentos disparan consecuencias. Cerrar un ciclo produce su reporte, mueve lo que quedó pendiente al ciclo siguiente y deja a la vista lo que se prometió y no ocurrió. Completar una tarea la devuelve a la bitácora convertida en hecho y despierta lo que dependía de ella. Registrar una venta agenda el seguimiento que la práctica del cliente exige. Cambiar el estado de una entidad reordena lo que el usuario verá mañana.

Nada de eso se pidió. Se sigue de lo que el usuario ya había dicho, en otro momento y sin pensar en esto: qué tipo de cosa es este cliente, cómo se gestiona, cuándo se abre y se cierra un ciclo. Escribir la regla una vez y cosechar sus consecuencias durante años es el trato que ofrece el sistema.

Una desviación tampoco se declara. Nadie rotula sus propios fracasos mientras trabaja, así que se descubren al cerrar, contrastando lo que cada entidad esperaba con lo que efectivamente quedó registrado.

Los derivados se pueden borrar sin perder nada, porque se vuelven a construir desde lo que el usuario escribió. Es la garantía de que el sistema puede generar todo lo que quiera sin volverse dueño de nada.

### 4.4 Las reglas viven junto a lo que rigen

Cómo se gestiona algo se escribe en un archivo, `AGENTS.md`, guardado en la carpeta de aquello que rige. Lo que dice ese archivo vale para todo lo que cuelga de ahí hacia abajo: qué se espera en ese terreno, cómo se lo trata, qué no se hace. Un nivel más adentro puede afinar la regla para su caso sin repetir lo que ya dijo el de arriba, y así la carpeta de un cliente sabe cosas que la de los clientes en general no tiene por qué saber.

Esto no es configuración, es el sistema mismo. Las prácticas de §2.3 viven aquí: mover una carpeta se lleva sus reglas consigo, copiarla las replica, y un cliente nuevo nace sabiendo cómo se lo gestiona porque cuelga de donde eso está escrito.

Lo que se escribe ahí es la filosofía de TUKU vuelta instrucción concreta: cómo se lleva un cliente, qué hace falta anotar de una reunión para que sirva en tres meses, cuándo algo merece una nota y no una entrada. Todo con un solo fin, que al final del día el estado de los archivos describa fielmente lo que está pasando en la vida del usuario. Está escrito en prosa y sin destinatario técnico, porque quien lo sigue puede ser tanto el agente como el propio usuario un domingo por la tarde. El mismo texto sirve a los dos, y esa es la prueba de que la regla estaba bien escrita.

Los **janitors** son la otra mitad, y no comparten naturaleza. No juzgan ni interpretan: ordenan, archivan lo vencido, reconstruyen lo derivado, revisan que los enlaces resuelvan. Un humano paciente podría hacer ese trabajo a mano, y por eso el sistema sigue siendo suyo, pero no hay razón para gastarle el tiempo en algo que una máquina hace igual de bien y sin equivocarse. Lo que exige criterio queda escrito para que alguien lo lea; lo que solo exige constancia se automatiza y se olvida.

También es lo que mantiene honesta la promesa de que la verdad está en los archivos. La lógica no está escondida en el código del motor ni en la memoria del agente: está en Markdown, en el repositorio del usuario, a la vista y editable por él. Cambiar cómo se comporta el sistema es escribir una frase donde corresponde.

### 4.5 El primer día

Un perfil recién creado no tiene historia, y el valor de TUKU crece con la historia. La
respuesta no es un asistente de configuración: es invertir la carga. El primer día el
usuario ve los días restantes de su ciclo y un chat que pregunta **"¿qué quieres registrar
hoy?"**. Registra, por texto o por voz. La estructura emerge: el agente ve nombres que se
repiten y propone entidades; ve pagos que se repiten y propone cadencias; el usuario
aprueba con una palabra. El onboarding no es una feature: es el sistema funcionando sobre
un perfil vacío.

Las cadencias de sistema (apertura, cierre, higiene) vienen propuestas y son editables,
de modo que el primer cierre de ciclo ocurre solo, aunque el usuario no haya configurado
nada.

## 5. Lo que TUKU no es

- **No es un segundo cerebro genérico.** La nota importa tanto como la bitácora y la tarea, pero existe para gestionar y no para coleccionar: se escribe para poder seguir pensando, no para llenar un archivo. Ninguna cadencia despierta una nota y nada entra al calendario sin que alguien lo convierta en tarea.
- **No es un visor de notas.** Obsidian y Quartz muestran los archivos; TUKU aporta el modelo, las reglas y la memoria que hace que esos archivos signifiquen algo. Por eso no compite con ellos, los usa.
- **No es una plataforma de esquemas configurables.** No hay editor de tipos, ni validación fuerte de campos, ni UI de configuración. Un tipo de entidad se declara escribiendo, como todo lo demás.
- **No es un producto cerrado.** Los archivos son texto plano en un repositorio Git, así que cualquier herramienta que sepa leerlos entra sin permiso de nadie, incluidas las que todavía no existen. El sistema se diseña contando con que el usuario traiga las suyas.
- **No es un almacén de secretos.** Contactos y contexto, sí; credenciales y contraseñas, jamás. Cada perfil es visible solo por su dueño.
- **No separa por sí solo lo que no debe mezclarse.** Una vida multidimensional junta en un mismo repositorio cosas que pertenecen a organizaciones distintas, y el sistema ofrece la jerarquía para mantenerlas aparte, pero qué se escribe y qué no es criterio del usuario. TUKU no sabe qué le debe confidencialidad a quién.
- **No decide.** Registra sin preguntar y deriva lo que se sigue de lo ya escrito, pero cambiar un objetivo, una regla o lo que uno se propuso pasa siempre por el usuario, y corregirlo cuesta una línea.

## 6. Criterios de éxito

Primero, si le sirvió a alguien:

1. **Permanencia**: una persona que nunca fue ordenada sigue usándolo al tercer mes, y no porque se lo haya propuesto.
2. **Recuerdo**: abrir un ciclo le devuelve algo que había olvidado que se prometió. Es la promesa del nombre y es el momento en que el producto se gana su lugar.
3. **Sin fricción**: contarle algo al sistema no cuesta más que anotarlo en un papel. Si cuesta más, el usuario lo anota en el papel y tiene razón.

Después, si el diseño está bien hecho:

4. **Reconstrucción**: borrar todo lo derivado y volver a construirlo desde lo que el usuario escribió devuelve el mismo sistema. Lo que producen los janitors debe volver idéntico; lo que redacta el agente, equivalente en sentido. Si algo que debía ser idéntico solo resulta equivalente, hay juicio del agente donde correspondía una regla.
5. **Operación manual**: una persona ejecuta un ciclo completo, apertura, registro y cierre, siguiendo solo lo escrito en Markdown, sin agente, y el resultado es válido.
6. **Memoria fuera del modelo**: una cadencia declarada meses atrás produce su tarea en el ciclo correcto sin que ningún LLM haya tenido que acordarse.
7. **Una regla, dos lectores**: lo escrito en un `AGENTS.md` lo puede seguir igual el agente que el usuario un domingo por la tarde. Si hay que traducirlo para uno de los dos, está mal escrito.
8. **Frugalidad**: una sesión normal de registro no invoca ningún modelo caro. El juicio, que se paga, aparece en la apertura, en el cierre y cuando el usuario lo pide.

## 7. Por dónde se empieza

Esto es un prototipo hecho por una persona con poco tiempo, así que lo único que se arriesga de verdad es tiempo. Ante la duda gana la opción que reduce superficie, y nada se construye antes de que algo lo pida.

El primer incremento es el más delgado que ya hace verdadera la promesa del nombre. **Hermes es la interfaz**, no hay otra: se le habla y él escribe en el repositorio. **Obsidian es el visor**, y con eso se acaba la discusión sobre interfaces por ahora. Entre medio, los **`AGENTS.md`** llevan las reglas y los **janitors** del comando `tuku` sostienen lo determinista. Nada más.

Lo demás está pensado y espera su turno: la web con Quartz, el canal de Telegram, el audio, el servidor multiusuario, la federación entre perfiles. Ninguna de esas piezas cambia el modelo, y esa es justamente la razón para no construirlas todavía.

El costo de operación cabe en unos diez dólares al mes con un modelo barato, lo que hace que el proyecto pueda existir sin depender de que alguien lo financie.
