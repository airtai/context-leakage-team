from pathlib import Path


def get_openapi_spec() -> str:
    path = Path(__file__).parent / "openapi.json"
    with path.open("r") as file:
        s = file.read()

    return s


__all__ = ["get_openapi_spec"]
