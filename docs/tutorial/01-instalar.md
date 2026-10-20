# 1. Instalar

> Qué quedó en disco, qué es tuyo y qué es de TUKU.

Necesitas [`uv`](https://docs.astral.sh/uv/) o `pipx`, cualquiera de los dos.

```bash
uv tool install --force "git+https://github.com/pewma-ai/tuku.git@devel"
```

```bash
tuku init mi-vault
```

Es el primero de los dos comandos que corres tú. Crea una carpeta, el **vault**, con todo lo que TUKU necesita para empezar. No pide configurar nada.

## Mira la carpeta

Todo son archivos de texto y cualquier programa los lee. Para mirarlos conviene [Obsidian](https://obsidian.md): muestra los recuadros de pendientes y lo que una página trae de otra, y el vault ya viene configurado para que Obsidian escriba igual que TUKU.

| Archivo | Qué guarda |
| --- | --- |
| `AHORA.md` | Lo que pasó, con su hora. Un encabezado por cada día de la semana en curso |
| `PENDIENTES.md` | Lo que sigue abierto y cuándo vence |
| `AGENTS.md` | Lo que tu agente sabe y cómo debe actuar |
| `LIBRO-DE-ESTILO.md` | Cómo opera TUKU, capítulo por capítulo. Tu vocabulario (clasificaciones, horizontes y tipos de nota) está en `reglas/*.user.md` y el libro lo incluye |
| `ambitos/` | Tus frentes: trabajo, casa, un cliente |
| `notas/` | Lo que sabes y no es de un día |

Los nombres en MAYÚSCULAS son de TUKU y los de minúsculas son tuyos.

> [!check] Qué debería pasar
> - `AHORA.md` tiene siete encabezados, de lunes a domingo, con la fecha de la semana en que instalaste.
> - `ambitos/` tiene una sola carpeta, `personal`.
> - `PENDIENTES.md` está vacío.

Abre `AGENTS.md` y léelo: en dos minutos sabes todo lo que tu agente sabe, porque el vault no guarda otras instrucciones.

## Abre tu agente

Ábrelo apuntando a la carpeta `mi-vault`.

> Claude Code, agy, Antigravity o el escritorio que uses. Sirve cualquiera que pueda leer la carpeta y correr comandos.

Empieza a hablarle. Si necesitas explicarle algo para que funcione, el vault tiene un defecto: anótalo.

Siguiente: [2. Registrar](02-registrar.md).
