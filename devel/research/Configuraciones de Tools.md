## Quartz
https://quartz.jzhao.xyz/
### Ocultar carpetas que empiezan por prefijos (ej. `_`)
Mediante la función **`filterFn`** dentro de la configuración del explorador en `quartz.config.ts`.
```TypeScript
Component.Explorer({
  filterFn: (node) => {
    // Excluye carpetas o archivos que comiencen por "_" 
    return !node.name.startsWith("_")
  },
})
```
### Content apuntando a mi Vault en GIT

1. **Tu Repositorio "Vault" (Contenido puro):**
    - Creas un repositorio Git propio (ej. `mi-vault-personal`).
    - Este repositorio solo contiene tus archivos Markdown (`.md`), carpetas de notas, imágenes/adjuntos y tu `.obsidian/`.
    - No incluye absolutamente nada del código de Quartz, Node.js ni `package.json`.
        
2. **Tu Repositorio "Sitio Quartz" (El motor):**
    - Clonas el repositorio de Quartz (o usas la plantilla oficial)        
    - Dentro de la carpeta `content/` de Quartz, agregas tu repositorio de notas como un **submódulo de Git**:
        
```bash
cd quartz
rm -rf content/* # Limpias el contenido por defecto
git submodule add https://github.com/tu-usuario/mi-vault-personal.git content
```
## Hermes

### Profiles para Hermes paralelos

1) **¿Necesitas volver a escribir la API key de DeepSeek en otro profile?**

Depende de cómo lo crees:

- `hermes profile create nuevo` (blank) → sí, `.env` queda vacío, tienes que correr nuevo setup y meter la key de nuevo.
- `hermes profile create nuevo --clone` → no, copia tu `config.yaml`, `.env` (con la API key de DeepSeek incluida), `SOUL.md` y skills del profile actual. Memoria y sesiones quedan limpias.
- `hermes profile create nuevo --clone-all` → copia todo lo de `--clone` más memorias, skills, cron jobs, plugins (pero no historial de sesiones/`state.db`, eso es demasiado pesado).

Si solo quieres reusar la misma key sin re-escribirla: `hermes profile create nuevo --clone`.

2) **Cómo usar profiles en los gateways**

Cada profile corre su propio proceso de gateway, totalmente independiente:

```bash
hermes profile create coder --clone     # crea el profile, reusa tu API key
coder gateway start                     # gateway del profile "coder" (proceso propio)
coder gateway install                   # launchd propio: hermes-gateway-coder
```

El alias `coder` es equivalente a `hermes -p coder`, funciona con cualquier subcomando (`coder chat`, `coder doctor`, etc.).

Importante: si vas a conectar el mismo tipo de plataforma (ej. Telegram) en varios profiles, cada uno necesita su propio bot token en su `.env` — si dos profiles usan el mismo token, el segundo gateway se bloquea con un error explícito (safety lock, soportado para Telegram/Discord/Slack/WhatsApp/Signal).

3) **¿Puedes tener 3 gateways abiertos a la vez, uno por profile?**

Sí, sin problema — son procesos independientes con su propio `HERMES_HOME`, cada uno con su propio PID, logs y estado:

```bash
hermes profile create bot1 --clone
hermes profile create bot2 --clone
hermes profile create bot3 --clone

bot1 gateway install   # servicio launchd propio, auto-restart
bot2 gateway install
bot3 gateway install
```

Cada uno queda supervisado independientemente (`hermes-gateway-bot1`, `-bot2`, `-bot3`). Lo único que tienes que cuidar tú:
- Puertos distintos si cada uno también corre API Server (`API_SERVER_PORT` diferente por profile en su `.env`).
- Bot tokens distintos por plataforma, como mencioné arriba.
- Nunca apuntar dos gateways al mismo `HERMES_HOME`/datos — pero como cada profile ya tiene su propio directorio, esto no aplica entre profiles distintos.

### Gateway con API y Telegram

**Telegram en ~/.hermes/.env**

- TELEGRAM_BOT_TOKEN — token del bot (secreto, dado por BotFather)
- TELEGRAM_ALLOWED_USERS — allowlist de user IDs autorizados a hablar con el bot
- TELEGRAM_HOME_CHANNEL — canal/chat "home" por defecto

**Config en ~/.hermes/.env:**
```bash
# ~/.hermes/.env
API_SERVER_ENABLED=true
API_SERVER_PORT=8642
API_SERVER_HOST=127.0.0.1  
API_SERVER_KEY=hermes-dev-local # Cambiar!
```
Un solo gateway para ambos: Telegram y el API Server no son procesos separados — son "platforms" dentro del mismo hermes gateway. No hay que lanzar nada aparte para Telegram; ya corre junto.

```
hermes gateway restart   # recarga .env y arranca ambos platforms
hermes gateway status    # confirma supervisión por launchd
```
3. Verificar que ambos quedaron up:
```
grep -i "connected" ~/.hermes/logs/gateway.log | tail -5
```
Deberías ver ✓ telegram connected y ✓ api_server connected.

Recomendado: regenera la key antes de usarlo en serio:
```
sed -i '' "s/API_SERVER_KEY=.*/API_SERVER_KEY=$(openssl rand -hex 32)/" ~/.hermes/.env
hermes gateway restart
```

**Script completo reusable**
```bash
#!/usr/bin/env bash
API_KEY=$(grep API_SERVER_KEY ~/.hermes/.env | tail -1 | cut -d= -f2)
BASE="http://localhost:8642/v1/responses"
CONV="mi-charla"   # nombre fijo = misma sesión en todas las llamadas futuras

curl -s "$BASE" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"hermes-agent\",\"input\":\"Recuerda el numero 42. Responde solo OK.\",\"conversation\":\"$CONV\"}"

echo

curl -s "$BASE" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"hermes-agent\",\"input\":\"Que numero te pedi recordar?\",\"conversation\":\"$CONV\"}"
```

