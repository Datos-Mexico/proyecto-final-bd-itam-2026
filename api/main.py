"""Entry point informativo del paquete `api`.

La aplicación FastAPI real vive en `app.main:app`. Para arrancar
el servidor en local:

    uv run uvicorn app.main:app --reload --port 8000

Este módulo se conserva como referencia mínima y emite un mensaje
guía cuando se ejecuta directamente.
"""


def main() -> None:
    print(
        "Para arrancar la API ejecuta:\n"
        "    uv run uvicorn app.main:app --reload --port 8000"
    )


if __name__ == "__main__":
    main()
