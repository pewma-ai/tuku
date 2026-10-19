"""tuku todo open / tuku todo close: las dos consecuencias deterministas.

Fase 2 de `devel/epics.md`. `**pendiente**` abre, `(Hecho)` cierra
(`spec/bitacora.md`). El cuerpo es el mismo texto en los tres lugares: el
registro que abre, la fila de `PENDIENTES.md` y el registro que cierra. **Abrir
es copiar, cerrar es encontrar y borrar.** Ninguna de las dos interpreta nada, y
por eso este paso no necesita LLM.

Operan **por registro**, no reconciliando el archivo. `PENDIENTES.md` es fuente
de verdad y no se regenera desde las bitácoras (`spec/pendientes.md`, regla 7):
un reconciliador borraría los pendientes abiertos en ciclos anteriores que el
`AHORA.md` en curso ya no menciona. La idempotencia se paga a mano: abrir
comprueba que la fila no esté, cerrar que la pareja exista.

El archivo es **una sola tabla**, `| Horizonte | Vence | Ámbito | Detalle |`.
El horizonte y la fecha son columnas y no estructura: bajar de escalón o agendar
mueve o edita una fila, y nunca crea ni destruye secciones.

**Qué lee y escribe:** las funciones de este módulo solo tocan `PENDIENTES.md`,
que es la fuente de verdad. Los casos de uso `abrir_en_vault` y `cerrar_en_vault`
escriben además el registro en `AHORA.md` y regeneran las dos vistas derivadas,
la región de cada día de `AHORA.md` y `ambitos/PENDIENTES-AMBITOS.md`, llamando
a `tuku.regenerate`; con `--no-regenerate` no las rehace y el lote regenera
una sola vez al final.
**A mano:** agregar la fila con su horizonte, o borrarla al cerrarlo, y copiar
el pendiente bajo su día y en el callout de su ámbito.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from tuku import archivo
from tuku import scope_tree as ambitos
from tuku.config import ambito_por_defecto, archivo_vault, leer_config
from tuku.entry import componer, stamp
from tuku.plan import Change, State, apply
from tuku.resultado import Resultado
from tuku.todo_core import (
    ABRE as ABRE,
)
from tuku.todo_core import (
    CABECERA as CABECERA,
)
from tuku.todo_core import (
    CIERRA as CIERRA,
)
from tuku.todo_core import (
    CON_FECHA as CON_FECHA,
)
from tuku.todo_core import (
    ESCALERA as ESCALERA,
)
from tuku.todo_core import (
    ESTA_SEMANA as ESTA_SEMANA,
)
from tuku.todo_core import (
    AperturaCerrada as AperturaCerrada,
)
from tuku.todo_core import (
    ConsecuenciaPendiente as ConsecuenciaPendiente,
)
from tuku.todo_core import (
    Fila as Fila,
)
from tuku.todo_core import (
    Marca as Marca,
)
from tuku.todo_core import (
    SinTabla as SinTabla,
)
from tuku.todo_core import (
    abrir as abrir,
)
from tuku.todo_core import (
    cambiar_ambito as cambiar_ambito,
)
from tuku.todo_core import (
    canonico as canonico,
)
from tuku.todo_core import (
    canonizar as canonizar,
)
from tuku.todo_core import (
    cerrados_el_mismo_dia as cerrados_el_mismo_dia,
)
from tuku.todo_core import (
    cerrar as cerrar,
)
from tuku.todo_core import (
    cierre as cierre,
)
from tuku.todo_core import (
    clave as clave,
)
from tuku.todo_core import (
    comando_de as comando_de,
)
from tuku.todo_core import (
    cuerpos as cuerpos,
)
from tuku.todo_core import (
    duplicados as duplicados,
)
from tuku.todo_core import (
    escalera_de as escalera_de,
)
from tuku.todo_core import (
    filas as filas,
)
from tuku.todo_core import (
    horizontes as horizontes,
)
from tuku.todo_core import (
    huerfanas as huerfanas,
)
from tuku.todo_core import (
    lint as lint,
)
from tuku.todo_core import (
    parsear as parsear,
)
from tuku.todo_core import (
    prefijo_de_marca as prefijo_de_marca,
)
from tuku.todo_core import (
    quitar_aperturas_cerradas as quitar_aperturas_cerradas,
)
from tuku.todo_core import (
    reemplazar_cuerpo as reemplazar_cuerpo,
)
from tuku.todo_core import (
    sin_consecuencia as sin_consecuencia,
)
from tuku.todo_core import (
    slug as slug,
)


def avisos_de_plazo(
    due: str, day: date | None, hour: str | None, now: datetime
) -> tuple[str, ...]:
    """Lo raro de un vencimiento, que no lo impide: ya pasó, o es anterior a la promesa.

    Registrar algo que ya venció es legítimo ("se me pasó pagar la luz"), y
    estar atrasado se calcula (`spec/pendientes.md`): el pendiente se abre y el
    comando alerta.
    """
    if not due:
        return ()
    dia, _, h = due.partition(" ")
    vence = datetime.fromisoformat(f"{dia} {h or '23:59'}")
    prometido = datetime.fromisoformat(
        f"{(day or now.date()).isoformat()} {hour or now.strftime('%H:%M')}"
    )
    if (day or hour) and vence < prometido:
        return (f"vence el {due}, antes de {prometido:%Y-%m-%d %H:%M}, cuando se promete.",)
    if vence < now:
        return (f"vence el {due}, que ya pasó: el pendiente nace atrasado.",)
    return ()


def is_registered(logbook: str, mark: Marca) -> bool:
    """Whether `logbook` already has a record with this mark and body, on any day.

    It makes `abrir_en_vault` and `cerrar_en_vault` idempotent: the match is by
    `clave`, so an extra or missing link does not make another record.
    """
    return any(
        (m := parsear(line)) is not None
        and m.marca == mark.marca
        and clave(m.cuerpo) == clave(mark.cuerpo)
        for line in logbook.splitlines()
    )


def plan_open(
    state: State,
    *,
    body: str,
    scope: str | None,
    horizon: str | None,
    due: str,
    day: date | None,
    hour: str | None,
    now: datetime,
) -> Change | Resultado:
    """The change of `tuku todo open`: the record and the row, or the rejection."""
    if day is not None and day > now.date():
        return Resultado.rechazo(
            f"el {day.isoformat()} todavía no llega: `--at` es cuándo se prometió. "
            f"Para que venza ese día: --due {day.isoformat()}"
        )
    limpio_scope = None
    if scope is not None:
        resolved = ambitos.resolve_scope(state.tree, scope)
        if isinstance(resolved, Resultado):
            return resolved
        limpio_scope = resolved
    marca = Marca(ABRE, limpio_scope, body.strip())
    escalera = escalera_de(state.horizons)
    horizon = CON_FECHA if due else canonico(horizon or escalera[0], escalera)

    logbook = state.logbook
    if not is_registered(logbook, marca):
        linea = componer(
            hora=hour or now.strftime("%H:%M"),
            scope=limpio_scope,
            body=f"{ABRE}: {marca.cuerpo}",
            rutas=state.tree.paths,
        )
        stamped = stamp(logbook, [linea], day=day or now.date())
        if isinstance(stamped, Resultado):
            return stamped
        logbook = stamped
    rows = abrir(
        state.todo,
        marca,
        horizon=horizon,
        due=due,
        escalera=escalera,
        rutas=state.tree.paths,
    )
    return Change(
        {"AHORA.md": logbook, "PENDIENTES.md": rows},
        f"pendiente abierto en «{horizon}»: {marca.cuerpo}",
        warnings=avisos_de_plazo(due, day, hour, now),
        regenerate=("AHORA.md", "PENDIENTES.md"),
    )


def abrir_en_vault(
    vault: Path,
    *,
    body: str,
    scope: str | None = None,
    horizon: str | None = None,
    due: str = "",
    regenerar: bool = True,
    day: date | None = None,
    hour: str | None = None,
    now: datetime,
) -> Resultado:
    """Abre un pendiente, estampa huella en la bitácora y regenera las vistas.

    Recibe los campos, no la línea del registro: abrir **es** el pendiente, y la
    marca la lleva implícita el verbo. Es la única vía: `tuku entry create` rechaza
    un `**pendiente**` y manda acá. El registro en `AHORA.md` se escribe salvo que
    ya esté.

    Regenerar es parte de abrir: si la vista quedara para un segundo comando, el
    pendiente existiría sin aparecer en su día, que es la falla silenciosa que
    `spec/pendientes.md` persigue. `regenerar=False` es la escotilla del lote,
    que regenera una sola vez al final.

    `day` y `hour` son cuándo se prometió y `due`, para cuándo es, como se
    escribe en la columna `Vence`: `AAAA-MM-DD` o `AAAA-MM-DD HH:MM`
    (`spec/pendientes.md`). Un `day` posterior a HOY (el de `now`) se rechaza: el
    registro de algo que todavía no se dijo no existe, y la fecha del pendiente va
    en `due`. Con `due`, el horizonte es `con fecha`; sin ninguno de los dos, el
    primer escalón del autor. La decisión es de `plan_open`.
    """
    state = State(
        ambitos.read_tree(vault),
        logbook=archivo.leer(archivo_vault(vault, "AHORA.md")),
        todo=archivo.leer(archivo_vault(vault, "PENDIENTES.md")),
        horizons=tuple(leer_config(vault).horizontes),
    )
    plan = plan_open(
        state, body=body, scope=scope, horizon=horizon, due=due, day=day, hour=hour, now=now
    )
    return apply(vault, plan, skip=() if regenerar else ("todo",))


def plan_close(
    state: State,
    *,
    body: str,
    scope: str | None,
    day: date | None,
    hour: str | None,
    now: datetime,
) -> Change | Resultado:
    """The change of `tuku todo close`: the closing record and the row, or a rejection."""
    if scope:
        resolved = ambitos.resolve_scope(state.tree, scope)
        if isinstance(resolved, Resultado):
            return resolved
        scope = resolved
    marca = Marca(CIERRA, None, body.strip())
    found = next(
        (f.ambito for f in filas(state.todo) if clave(f.cuerpo) == clave(marca.cuerpo)), None
    )

    if scope is None and found is None and state.default_scope:
        resolved = ambitos.resolve_scope(state.tree, state.default_scope)
        if isinstance(resolved, Resultado):
            return resolved
        scope = resolved

    rows, paired = cerrar(state.todo, marca)

    logbook = state.logbook
    if not is_registered(logbook, marca):
        linea = componer(
            hora=hour or now.strftime("%H:%M"),
            scope=scope if scope is not None else found,
            body=cierre(marca.cuerpo),
            rutas=state.tree.paths,
        )
        stamped = stamp(logbook, [linea], day=day or now.date())
        if isinstance(stamped, Resultado):
            return stamped
        logbook = stamped
    logbook = quitar_aperturas_cerradas(logbook, marca.cuerpo)

    files = {"AHORA.md": logbook, "PENDIENTES.md": rows}
    regenerate = ("AHORA.md", "PENDIENTES.md")
    if not paired:
        return Change(
            files,
            f"cierre escrito: {marca.cuerpo}",
            warnings=(
                f"no había ningún pendiente abierto con el cuerpo {marca.cuerpo!r}, "
                f"así que no se borró nada. Si esperabas cerrarlo, revisa que el texto "
                f"coincida palabra por palabra.",
            ),
            regenerate=regenerate,
        )
    return Change(files, f"pendiente cerrado: {marca.cuerpo}", regenerate=regenerate)


def cerrar_en_vault(
    vault: Path,
    *,
    body: str,
    regenerar: bool = True,
    day: date | None = None,
    hour: str | None = None,
    scope: str | None = None,
    now: datetime,
) -> Resultado:
    """Cierra un pendiente por su cuerpo, estampando su huella en la bitácora.

    Un cierre sin pareja **no es un fallo**: es el caso normal del día uno
    (`devel/epics.md`). Se reporta, el registro queda escrito y `PENDIENTES.md`
    no se toca, porque inventar el pendiente que falta dejaría el archivo
    mintiendo.

    **El cierre cae en el ámbito donde estaba el pendiente.** Sin `scope`, el
    registro toma el de la fila que cierra; solo si la fila no tiene, el
    `scope_default` de la config. Con `scope`, manda `scope`. La decisión es de
    `plan_close`.
    """
    state = State(
        ambitos.read_tree(vault),
        logbook=archivo.leer(archivo_vault(vault, "AHORA.md")),
        todo=archivo.leer(archivo_vault(vault, "PENDIENTES.md")),
        default_scope=ambito_por_defecto(vault),
    )
    plan = plan_close(state, body=body, scope=scope, day=day, hour=hour, now=now)
    return apply(vault, plan, skip=() if regenerar else ("todo",))


def hallazgos_del_vault(vault: Path) -> list[str]:
    """`lint` sobre el vault: lee los archivos y calcula las vistas esperadas."""
    from tuku import regenerate, scope_tree
    from tuku.config import archivo_vault

    pendientes = archivo.leer(archivo_vault(vault, "PENDIENTES.md"))
    ahora_path = vault / "AHORA.md"
    ahora = archivo.leer(ahora_path) if ahora_path.is_file() else None
    vistas: dict[str, tuple[str | None, str]] = {}
    if ahora is not None:
        vistas["AHORA.md"] = (
            ahora,
            regenerate.vistas_en_ahora(
                ahora, pendientes, scope_tree.rutas(vault), regenerate.primer_escalon(vault)
            ),
        )
    ambitos_path = vault / regenerate.ARCHIVO_AMBITOS
    vistas[regenerate.ARCHIVO_AMBITOS.as_posix()] = (
        archivo.leer(ambitos_path) if ambitos_path.is_file() else None,
        regenerate.documento_del_vault(vault, pendientes),
    )
    historia = [archivo.leer(b) for b in sorted((vault / "bitacoras").glob("*.md"))]
    return lint(pendientes, ahora, vistas=vistas, historia=historia)
