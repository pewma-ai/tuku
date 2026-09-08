"""Lo que devuelve una operación sobre el vault.

Cada comando de TUKU tiene dos mitades que conviene no mezclar: **decidir qué
pasa con el vault** y **contárselo a quien invocó**. La primera es del sistema y
se prueba con un `assert`; la segunda es del CLI, y son `print` y códigos de
salida.

`Resultado` es la costura entre las dos. Un caso de uso devuelve si la operación
procedió y qué hay que decir; [`cli.py`](cli.py) traduce eso a texto y a un
código de `spec/cli.md`. La consecuencia práctica es que la regla se puede
probar sin capturar `stdout` ni montar un escenario completo:

    r = note.crear_con_constancia(vault, title="...", body="...")
    assert r.ok and "nota creada" in r.mensaje

**No lleva el código de salida.** Un caso de uso no sabe de códigos, igual que
no sabe si su mensaje va a una terminal o a un log. `ok` alcanza: el CLI mapea a
`EXITO` o `RECHAZO`. Los otros dos códigos no nacen acá, y por eso no están: el
`2` es de argparse ante una invocación mal escrita, y el `3` sube como excepción
desde la resolución del árbol de TUKU.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Resultado:
    """Si la operación procedió, y qué decir sobre ella.

    `error` distingue a dónde va el mensaje: un rechazo por el estado del vault
    se escribe en `stderr`, y lo que el comando reporta sin negarse (un lint con
    hallazgos, un cierre sin pareja) va a `stdout` aunque no sea un éxito.
    """

    ok: bool
    mensaje: str
    error: bool = False

    @classmethod
    def hecho(cls, mensaje: str) -> Resultado:
        """La operación procedió."""
        return cls(True, mensaje)

    @classmethod
    def rechazo(cls, mensaje: str, *, error: bool = True) -> Resultado:
        """La operación se negó por el estado del vault.

        `spec/cli.md` exige que el mensaje nombre el defecto **y** la corrección.
        Con `error=False` el rechazo se reporta por `stdout`, que es lo que hacen
        los lint: informan de lo que encontraron sin que sea un fallo de
        invocación.
        """
        return cls(False, mensaje, error)
