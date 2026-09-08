# Escenario · 001-05-init-no-toca-la-red

**Cubre:** epic 001, fase 0, decidido #3 de [`../../devel/epics.md`](../../devel/epics.md) ("Offline: no toca la red").

## Escenario: `tuku init` completa con la red bloqueada

Dado el módulo `socket` parchado para que abrir un socket, conectar o resolver un nombre lance
Cuando se llama a `init(destino, variante="vanilla", home=RAIZ)`
Entonces la siembra completa igual: `AHORA.md` con las fechas resueltas y sin placeholders

## Por qué existe, si `001-02` ya siembra sin red

`001-02` no ve tráfico, pero no lo impide: si mañana `init()` (o algo que importe) intentara resolver un nombre o abrir una conexión, `001-02` seguiría pasando. Este lo fuerza: con `socket.socket`, `socket.create_connection` y `socket.getaddrinfo` parchados para lanzar `RedBloqueada`, cualquier intento sube y el test falla señalando exactamente eso.

Es barato porque `init()` es copia de archivos: no hay nada que la red pueda aportar. El test convierte esa propiedad en una afirmación con garante.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_05
```

Deja el vault en `playground/001-05-init-no-toca-la-red/`.

## Qué se mira a mano

- Nada específico: si el test pasa, la afirmación "offline" está aislada. La revisión byte a byte del vault la hace `001-02`.
