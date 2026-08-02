# Guía rápida — primeros pasos con TUKU

> Para quien nunca usó TUKU y solo quiere empezar a registrar su semana. No necesitas
> saber Markdown ni entender la arquitectura interna: basta con escribir lo que te pasa.

---

## 0. Instalación

TUKU se instala con [`pipx`](https://pipx.pypa.io/), que lo deja disponible como comando
`tuku` en cualquier directorio, aislado del resto de tu Python. No hace falta clonar nada.
Si no tienes `pipx`:

```bash
brew install pipx      # macOS
pipx ensurepath
```

Mientras no exista release en PyPI, TUKU se instala directo desde la rama `devel` del
repositorio:

```bash
pipx install "git+https://github.com/pewma-ai/tuku@devel"
```

Verifica que quedó disponible:

```bash
tuku --help
```

**Para actualizar** más adelante, `pipx upgrade` no siempre detecta commits nuevos en una
rama móvil. El comando confiable es:

```bash
pipx install --force "git+https://github.com/pewma-ai/tuku@devel"
```

---

## 1. Crea tu perfil

Un perfil es tu repositorio personal de TUKU: tus entradas, tareas, entidades y ciclos.
Créalo en el directorio donde quieras guardarlo (fuera del repo del motor):

```bash
tuku init ~/mi-tuku
cd ~/mi-tuku
```

Esto siembra la estructura mínima:

```
mi-tuku/
├── .tuku/config.yaml        # configuración del perfil
├── AGENTS.md
├── entradas/entradas.md     # tu bitácora, vacía al empezar
├── tareas/tareas.md         # tu backlog, vacío al empezar
├── entidades/personal/
├── estrategia/{cadencias.md, capacidad.md}
└── notas/
```

No hay que elegir plantillas ni configurar nada más. El perfil crece por acumulación a
medida que registras cosas.

Verifica que quedó sano:

```bash
tuku doctor
```

---

## 2. Registra lo que te pasa

El comando `registrar` convierte una frase en lenguaje natural en una entrada de bitácora
o una tarea, según corresponda:

```bash
tuku registrar "Llamé al Colegio San Marcos, quieren cotización de 200 cuadernos. Se las mando mañana."
```

Si mencionas una entidad que TUKU no conoce (un cliente, un proveedor, una persona), no
falla: la da de alta al vuelo. No necesitas crear nada de antemano.

`registrar` es tan frecuente que tiene atajo: si escribes `tuku` seguido de un texto que
no coincide con ningún subcomando, se interpreta como `tuku registrar`.

```bash
tuku "Llamé al Colegio San Marcos, quieren cotización de 200 cuadernos."
```

Para ver qué generaría un texto sin escribirlo todavía, usa `--dry-run`:

```bash
tuku registrar "El Liceo del Valle no me contesta hace meses" --dry-run
```

Registra cada cosa relevante del día: compromisos, ventas, avisos, problemas. Entre más
constante seas, más útil se vuelve TUKU.

---

## 3. Abre el ciclo de la semana

Un ciclo agrupa tu trabajo en un período (semana, mes, turno, viaje). Al empezar la
semana, ábrelo:

```bash
tuku abrir 2026-W32 --tipo semana
```

Esto siembra `ciclos/plan_2026-W32.md` con las secciones de Intención, restricciones y
contexto. Puedes editarlo a mano para declarar qué te propones esa semana.

---

## 4. Consulta el estado con RADAR

En cualquier momento, sin cerrar nada ni escribir en disco, puedes preguntar qué se te
está quedando pendiente:

```bash
tuku radar
```

RADAR te muestra tareas abiertas, tareas bloqueadas y seguimientos (`followup`) vencidos:
justo lo que se te suele olvidar.

---

## 5. Cierra el ciclo

Al terminar la semana (o el período que hayas abierto):

```bash
tuku cerrar 2026-W32 --tipo semana
```

Esto siembra `ciclos/resultados_2026-W32.md` con Avances, Desviaciones, Aprendizajes,
Momentum y una Intención propuesta para el ciclo siguiente. Si es tu primer ciclo, TUKU
omite Desviaciones (no hay Intención previa contra la cual comparar) y en su lugar te
propone una.

---

## 6. Mantenimiento del perfil

Estos dos comandos no son necesarios a diario, pero conviene conocerlos:

```bash
tuku janitor          # revisa que el perfil cumpla las invariantes de spec/
tuku janitor --fix    # repara automáticamente lo que se pueda reparar
tuku sync             # sincroniza instrucciones de agente y plantillas de proceso
```

---

## Flujo típico de una semana

```
lunes      tuku abrir 2026-W32 --tipo semana
día a día  tuku registrar "lo que va pasando, en tus palabras"
cualquier  tuku radar                      # ¿qué se me está quedando?
viernes    tuku cerrar 2026-W32 --tipo semana
```

Para ver este flujo narrado con un caso completo, revisa
[`corpus/simulaciones/flujo-pyme-semana.md`](../corpus/simulaciones/flujo-pyme-semana.md).

---

## Más documentación

- [`docs/brief.md`](brief.md) — visión y problema que resuelve TUKU.
- [`docs/brief.md`](brief.md#3-principios) — principios arquitectónicos.
- [`docs/arquitectura.md`](arquitectura.md) — modelo de datos y motor.
- [`docs/glosario.md`](glosario.md) — vocabulario del dominio.
