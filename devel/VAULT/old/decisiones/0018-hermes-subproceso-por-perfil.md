# ADR 0018 — Integración agéntica vía subproceso `hermes chat` con sesión persistente por perfil

## Contexto

TUKU necesita invocar un LLM para la Fase 5 (siembra asistida de ciclos, captura conversacional,
alta de notas). La instalación de Hermes Agent ya existe en `~/.hermes` del sistema y es la
herramienta elegida por el usuario para interacción agéntica.

Se exploraron dos alternativas para integrar Hermes en TUKU:

1. **API Python interna (`AIAgent` de `run_agent.py`)**:
   - La clase `AIAgent` existe en el venv privado de Hermes, pero `hermes` no expone un módulo
     Python importable desde fuera (`from hermes import HermesAgent` falla con
     `ModuleNotFoundError`).
   - Usarla requeriría que TUKU instale el venv completo de Hermes o lo importe desde una ruta
     absoluta, acoplando el motor a la versión y ubicación exacta de la instalación del usuario.
   - Viola ADR 0002 (el motor no se vendoriza en el perfil) en su espíritu: acoplar a una ruta
     de instalación es equivalente a copiar código.

2. **Subproceso vía CLI (`hermes chat -q "..." -Q --safe-mode --source tool`)**:
   - Usa el binario `hermes` instalado en el `PATH` del sistema, sin acoplamientos de venv.
   - El aislamiento de perfil se logra fijando `HERMES_HOME=<perfil>/.hermes`, donde cada
     perfil TUKU tiene su propio estado de Hermes (sesiones, memoria, logs) sin contaminar
     `~/.hermes`.
   - La sesión se mantiene entre llamadas con `--continue`, que retoma la sesión más reciente
     en el `HERMES_HOME` activo — y como cada perfil tiene su propio home, el `--continue` es
     automáticamente correcto por perfil.
   - Las credenciales (`.env`, `auth.json`) se enlazan como symlinks desde `~/.hermes` al
     `.hermes/` del perfil, sin duplicarlas ni versionar secretos.
   - `--safe-mode` desactiva personalizaciones del usuario (`SOUL.md`, skills, memoria global)
     para reproducibilidad en CI. `--source tool` excluye estas sesiones del historial del
     usuario.
   - `tuku init` detecta si `~/.hermes` existe y crea el directorio `.hermes/` en el perfil con
     los symlinks y un `config.yaml` mínimo (`model.show_reasoning: false`,
     `model.thinking: false`, sin TTS/STT). El directorio se agrega al `.gitignore` del perfil.

La API Python podría ser superior si Hermes la expusiera de forma estable y pública; hoy no lo
hace. Se adopta el subproceso como decisión provisional mientras aparece esa alternativa.

## Decisión

**TUKU invoca Hermes mediante subproceso `hermes chat` con sesión persistente por perfil.**

El contrato de invocación es:

```python
# --continue sin nombre retoma la sesión más reciente del HERMES_HOME activo;
# si no existe ninguna, inicia una nueva. Forma canónica para toda invocación:
cmd = ["hermes", "chat", "-z", prompt, "--continue"]

env = {**os.environ, "HERMES_HOME": str(profile_dir / ".hermes"), "TZ": "UTC"}
```

Sin `--safe-mode` ni `--source tool`: Hermes accede a memoria y contexto del perfil,
lo que le permite aprender el vocabulario del usuario a lo largo del tiempo. El
aislamiento entre perfiles lo da `HERMES_HOME`, no las banderas de sesión.

`tuku init` provisiona `<perfil>/.hermes/` con symlinks a credenciales y configuración mínima.
El directorio `.hermes/` se excluye del control de versiones del perfil (`.gitignore`).

## Consecuencias

**A favor:**
- Sin acoplamiento de venv: TUKU funciona con cualquier versión de Hermes que esté en el PATH.
- Aislamiento perfecto por perfil: dos perfiles TUKU en la misma máquina tienen estados de
  Hermes completamente separados; sus memorias, sesiones y logs no se mezclan.
- El gateway de Hermes puede levantarse por perfil de forma independiente (un gateway por
  `HERMES_HOME`), sin conflicto.
- La credencial se gestiona una vez en `~/.hermes/.env` y todos los perfiles la heredan sin
  duplicarla.
- Pruebas con `perfil_tmp`: `tuku init` ya provisiona el `.hermes/` necesario, así que la
  fixture `hermes_efimero` de los tests queda trivial (apuntar `HERMES_HOME` al `.hermes/`
  sembrado por `init`).

**En contra:**
- Overhead de subproceso por cada llamada (~500 ms de arranque de la CLI de Hermes). Aceptable
  en flujos de un turno o pocos turnos; no apto para bucles de herramienta de alta frecuencia.
- La sesión persistente con `--continue` asume que la sesión más reciente del `HERMES_HOME` es
  siempre la correcta; si dos procesos de TUKU escriben al mismo perfil en paralelo, pueden
  confundir sesiones. Alcance no previsto en V1; se documenta como limitación conocida.
- Si Hermes no está instalado, los subcomandos agénticos fallan con un error claro; los
  deterministas (`--sin-agente`) siguen funcionando sin restricción.

**Estado:** `aceptado` — provisional hasta que Hermes exponga una API Python pública estable,
momento en que se escribirá ADR 0019 que supera a éste.
