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


def avisos_de_plazo(due: str, day: date | None, hour: str | None) -> tuple[str, ...]:
    """Lo raro de un vencimiento, que no lo impide: ya pasó, o es anterior a la promesa.

    Registrar algo que ya venció es legítimo ("se me pasó pagar la luz"), y
    estar atrasado se calcula (`spec/pendientes.md`): el pendiente se abre y el
    comando alerta.
    """
    if not due:
        return ()
    ahora = datetime.now()
    dia, _, h = due.partition(" ")
    vence = datetime.fromisoformat(f"{dia} {h or '23:59'}")
    prometido = datetime.fromisoformat(
        f"{(day or ahora.date()).isoformat()} {hour or ahora.strftime('%H:%M')}"
    )
    if (day or hour) and vence < prometido:
        return (f"vence el {due}, antes de {prometido:%Y-%m-%d %H:%M}, cuando se promete.",)
    if vence < ahora:
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
    (`spec/pendientes.md`). Un `day` posterior a HOY se rechaza: el registro
    de algo que todavía no se dijo no existe, y la fecha del pendiente va en
    `due`. Con `due`, el horizonte es `con fecha`; sin ninguno de los dos, el
    primer escalón del autor.
    """
    from tuku import scope_tree as ambitos
    from tuku.config import archivo_vault, leer_config
    from tuku.entry import componer, stamp
    from tuku.regenerate import rehacer

    if day is not None and day > date.today():
        return Resultado.rechazo(
            f"el {day.isoformat()} todavía no llega: `--at` es cuándo se prometió. "
            f"Para que venza ese día: --due {day.isoformat()}"
        )
    tree = ambitos.read_tree(vault)
    limpio_scope = None
    if scope and ambitos.normalizar(scope):
        resolved = ambitos.resolve_scope(tree, scope)
        if isinstance(resolved, Resultado):
            return resolved
        limpio_scope = resolved
    marca = Marca(ABRE, limpio_scope, body.strip())
    escalera = escalera_de(leer_config(vault).horizontes)
    horizon = CON_FECHA if due else canonico(horizon or escalera[0], escalera)

    ahora_path = archivo_vault(vault, "AHORA.md")
    ahora_actual = archivo.leer(ahora_path)
    if not is_registered(ahora_actual, marca):
        hora = hour or datetime.now().strftime("%H:%M")
        linea = componer(
            hora=hora,
            scope=limpio_scope,
            body=f"{ABRE}: {marca.cuerpo}",
            rutas=tree.paths,
        )
        stamped = stamp(ahora_actual, [linea], day=day or date.today())
        if isinstance(stamped, Resultado):
            return stamped
        archivo.escribir(ahora_path, stamped)

    ruta = archivo_vault(vault, "PENDIENTES.md")
    archivo.escribir(
        ruta,
        abrir(
            archivo.leer(ruta),
            marca,
            horizon=horizon,
            due=due,
            escalera=escalera,
            rutas=tree.paths,
        ),
    )
    rehacer(vault, ["AHORA.md", "PENDIENTES.md"], salvo=() if regenerar else ("todo",))
    return Resultado.hecho(
        f"pendiente abierto en «{horizon}»: {marca.cuerpo}",
        avisos=avisos_de_plazo(due, day, hour),
    )


def cerrar_en_vault(
    vault: Path,
    *,
    body: str,
    regenerar: bool = True,
    day: date | None = None,
    hour: str | None = None,
    scope: str | None = None,
) -> Resultado:
    """Cierra un pendiente por su cuerpo, estampando su huella en la bitácora.

    Un cierre sin pareja **no es un fallo**: es el caso normal del día uno
    (`devel/epics.md`). Se reporta, el registro queda escrito y `PENDIENTES.md`
    no se toca, porque inventar el pendiente que falta dejaría el archivo
    mintiendo.

    **El cierre cae en el ámbito donde estaba el pendiente.** Sin `scope`, el
    registro toma el de la fila que cierra; solo si la fila no tiene, el
    `scope_default` de la config. Con `scope`, manda `scope`.
    """
    from tuku import scope_tree as ambitos
    from tuku.config import ambito_por_defecto, archivo_vault
    from tuku.entry import componer, stamp
    from tuku.regenerate import rehacer

    tree = ambitos.read_tree(vault)
    if scope:
        resolved = ambitos.resolve_scope(tree, scope)
        if isinstance(resolved, Resultado):
            return resolved
        scope = resolved
    marca = Marca(CIERRA, None, body.strip())
    ruta = archivo_vault(vault, "PENDIENTES.md")
    pendientes_texto = archivo.leer(ruta)

    ambito_encontrado: str | None = None
    for f in filas(pendientes_texto):
        if clave(f.cuerpo) == clave(marca.cuerpo):
            ambito_encontrado = f.ambito
            break

    if (
        scope is None
        and ambito_encontrado is None
        and (por_defecto := ambito_por_defecto(vault))
    ):
        resolved = ambitos.resolve_scope(tree, por_defecto)
        if isinstance(resolved, Resultado):
            return resolved
        scope = resolved

    texto, hubo_pareja = cerrar(pendientes_texto, marca)

    ahora_path = archivo_vault(vault, "AHORA.md")
    ahora_actual = archivo.leer(ahora_path)
    if not is_registered(ahora_actual, marca):
        ambito_final = scope if scope is not None else ambito_encontrado
        hora = hour or datetime.now().strftime("%H:%M")
        linea = componer(
            hora=hora,
            scope=ambito_final,
            body=cierre(marca.cuerpo),
            rutas=tree.paths,
        )
        stamped = stamp(ahora_actual, [linea], day=day or date.today())
        if isinstance(stamped, Resultado):
            return stamped
        ahora_actual = stamped
    ahora_texto = quitar_aperturas_cerradas(ahora_actual, marca.cuerpo)
    if ahora_texto != archivo.leer(ahora_path):
        archivo.escribir(ahora_path, ahora_texto)

    if hubo_pareja:
        archivo.escribir(ruta, texto)
    rehacer(vault, ["AHORA.md", "PENDIENTES.md"], salvo=() if regenerar else ("todo",))

    if not hubo_pareja:
        return Resultado.hecho(
            f"cierre escrito: {marca.cuerpo}",
            avisos=(
                f"no había ningún pendiente abierto con el cuerpo {marca.cuerpo!r}, "
                f"así que no se borró nada. Si esperabas cerrarlo, revisa que el texto "
                f"coincida palabra por palabra.",
            ),
        )
    return Resultado.hecho(f"pendiente cerrado: {marca.cuerpo}")


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
            regenerate.vistas_en_ahora(ahora, pendientes, scope_tree.rutas(vault)),
        )
    ambitos_path = vault / regenerate.ARCHIVO_AMBITOS
    vistas[regenerate.ARCHIVO_AMBITOS.as_posix()] = (
        archivo.leer(ambitos_path) if ambitos_path.is_file() else None,
        regenerate.documento_del_vault(vault, pendientes),
    )
    historia = [archivo.leer(b) for b in sorted((vault / "bitacoras").glob("*.md"))]
    return lint(pendientes, ahora, vistas=vistas, historia=historia)
