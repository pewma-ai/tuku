# TUKU — Deployment

> Ubicación en el repo: `docs/deployment.md`
> Estado: decisión tomada. Los detalles de comandos pueden afinarse; el modelo de dos
> artefactos no.

---

## 1. Dos artefactos, nunca mezclados

TUKU se compone de dos cosas con ciclos de vida, dueños y repositorios distintos:

| | **Motor** | **Perfil** |
|---|---|---|
| Qué es | código, janitors, procesos, plantillas | bitácoras, tareas, entidades, notas |
| Dónde vive | site-packages (vía pipx) | repositorio Git del usuario |
| Quién lo versiona | PEWMA.AI | el usuario |
| Cadencia de cambio | semanas | diaria |
| Vida útil esperada | años | décadas |

**Regla dura: el motor nunca se copia dentro del perfil.** Vendorizar el código en el
repositorio de datos contamina el historial de las bitácoras con churn de versiones,
convierte cada actualización en un merge sobre datos ajenos al motor, y multiplica copias
innecesarias en el despliegue servidor. El perfil contiene datos y punteros; nada más.

**Corolario de servidor:** el mismo motor apunta a N perfiles. El diseño local *es* el
diseño del servidor. Por eso `--profile` existe desde el primer commit, aunque al principio
solo haya uno.

---

## 2. Instalación

### 2.1 Usuario final (release)

```bash
pipx install tuku
```

pipx aísla el entorno automáticamente y no toca el Python del sistema. Es el mecanismo
correcto para un motor Python distribuido como CLI.

**Descartado npm.** Los janitors son Python y lo seguirán siendo; un wrapper Node añadiría
una dependencia de runtime sin aportar nada, especialmente costosa en los contextos de
usuario que TUKU busca servir.

**Descartado `curl | bash`.** Si en algún momento hay script de instalación, el gesto debe
ser: descargar, inspeccionar, ejecutar. Nunca canalizar directo a shell.

### 2.2 Instalación desde branch (estado actual del proyecto)

Mientras no exista release en PyPI, la instalación es directa desde el repositorio:

```bash
pipx install "git+https://github.com/pewma-ai/tuku@devel"
```

Otras referencias válidas:

```bash
# rama estable
pipx install "git+https://github.com/pewma-ai/tuku@main"
# tag concreto
pipx install "git+https://github.com/pewma-ai/tuku@v0.3.0"
# commit fijo (reproducible)
pipx install "git+https://github.com/pewma-ai/tuku@a1b2c3d"
```

**Actualizar desde branch.** `pipx upgrade` reutiliza la especificación original y no
siempre detecta commits nuevos en una rama móvil. El comando confiable es:

```bash
pipx install --force "git+https://github.com/pewma-ai/tuku@devel"
```

Conviene documentarlo como el camino oficial de actualización mientras `devel` sea la
fuente, y envolverlo en `tuku upgrade` para que el usuario no tenga que recordarlo.

**Probar sin instalar:**

```bash
uvx --from "git+https://github.com/pewma-ai/tuku@devel" tuku doctor
```

### 2.3 Requisito: la versión debe ser identificable

Instalar desde una rama móvil significa que dos usuarios con "la misma versión" pueden
tener código distinto. Por eso el paquete debe estampar su procedencia en tiempo de build
(`setuptools-scm` o equivalente) y `tuku doctor` debe reportar versión, commit y rama. Sin
esto, ningún reporte de bug de esta etapa es accionable.

### 2.4 Desarrollo

```bash
git clone https://github.com/pewma-ai/tuku && cd tuku
git checkout devel
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

---

## 3. Estado en el sistema del usuario

### 3.1 `~/.tuku/` — configuración, no código

```
~/.tuku/
├── config.toml        # registro de perfiles, perfil por defecto
├── credentials        # claves API — permisos 0600
├── cache/             # thesaurus compilado, índices derivados
└── logs/
```

`config.toml`:

```toml
default_profile = "personal"

[profiles.personal]
path = "~/repos/tuku-personal"

[profiles.trabajo]
path = "~/repos/tuku-paranal"
```

Todo lo de `cache/` es reconstruible: borrarlo nunca pierde información.
`credentials` nunca entra al perfil ni a Git.

### 3.2 El perfil

Repositorio Git independiente, propiedad del usuario. `tuku init` lo siembra:

```
mi-tuku/
├── .tuku/
│   ├── config.yaml        # schema_version, tipos, derivaciones, clasificaciones
│   └── procesos/          # punteros o symlinks a los procesos del motor
├── AGENTS.md              # instrucciones raíz para el agente
├── entradas/              # canónico inmutable: un archivo por mes
│   ├── 2026-08.md
│   └── 2025/
├── tareas/
│   ├── abiertas.md        # único archivo mutable del sistema
│   ├── 2026-08.md         # cerradas o canceladas ese mes
│   └── 2025/
├── ciclos/
│   ├── plan_2026-08-10_temuco.md
│   ├── resultados_2026-07-28_turno.md
│   └── 2025/
├── entidades/
│   ├── personal/
│   │   ├── personal.md
│   │   └── medico/
│   │       ├── medico.md
│   │       └── pediatra.md
│   └── paranal/
│       ├── paranal.md
│       └── sw-responsible.md
├── tipos/
│   └── pewma/cliente.md
├── estrategia/
│   ├── cadencias.md
│   └── capacidad.md
└── notas/
```

**Los assets de agente deben ser descubribles desde el perfil.** Un agente de codificación
lee lo que está en la carpeta; si los procesos viven solo en site-packages, no los ve, y se
pierde la ventaja del anidamiento POSIX de instrucciones. Por eso `tuku init` genera
`.tuku/procesos/` como punteros o symlinks al motor instalado, y `AGENTS.md` por nivel.
Se regenera con `tuku sync` y no ensucia el historial de datos.

---

## 4. Versionado de esquema y migraciones

Consecuencia directa del principio fundamental: **los datos sobreviven al motor**. Un
usuario puede instalar TUKU, dejarlo dos años y volver; su repositorio debe seguir siendo
legible, y el motor nuevo debe saber leer el formato viejo.

- `.tuku/config.yaml` declara `schema_version`.
- El motor declara qué rango de esquemas soporta.
- `tuku doctor` compara ambos y avisa.
- `tuku migrate` transforma el perfil, **siempre en un commit propio y aislado**, para que
  el usuario pueda revisar el diff y revertir.
- Las migraciones son parte del motor (`src/tuku/migrations/`) y se acumulan; ninguna se
  borra.

Definirlo hoy cuesta poco; retrofitearlo cuesta muchísimo.

---

## 5. Superficie de comandos

```
tuku init [ruta]        # crea el perfil, siembra cadencias de sistema
tuku setup              # modelo, claves, canal de entrada
tuku abrir              # bitacora_ + plan_
tuku cerrar             # resultados_
tuku tarea ...          # alta, cierre, consulta del backlog canónico
tuku janitor            # garantiza invariantes (idempotente)
tuku sync               # regenera punteros y AGENTS.md tras actualizar el motor
tuku doctor             # versión, esquema, enlaces rotos, estado del cron
tuku migrate            # migración de esquema
tuku upgrade            # reinstala desde el canal configurado
```

Flag global `--profile <nombre>` en todos.

---

## 6. Del escritorio al servidor

El salto a la VM no cambia el modelo, solo la ubicación de los perfiles:

- Un motor instalado, N perfiles como repositorios aislados.
- `~/.tuku/config.toml` pasa a ser configuración de servicio con N entradas.
- El cron que revisa acciones agénticas pendientes itera sobre perfiles.
- Aislamiento por proceso y por usuario del sistema operativo, no solo por directorio.

Nada de esto exige rediseño **siempre que `--profile` exista desde el principio**. Esa es la
única decisión de hoy que compra el despliegue de mañana.

---

## 7. Lo que no se decide aquí

- Autenticación y modelo de identidad multiusuario.
- Quién paga la inferencia (BYOK vs. absorbida).
- Conectores con terceros (Calendar, Drive, JIRA).
- Federación entre perfiles vía MCP — aparcada, pero ya obliga a `id` estable e
  independiente del path.
