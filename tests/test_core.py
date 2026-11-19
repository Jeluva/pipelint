import pathlib
from pipelint import core

EJ = pathlib.Path(__file__).parent.parent / "ejemplos" / "azure-pipelines.yml"


def codigos():
    return {h[1] for h in core.lint(core.cargar(EJ))}


def test_detecta_reglas():
    assert {"P003", "P004", "P006", "P007", "P008", "P009"} <= codigos()


def test_resumen():
    r = core.resumen(core.cargar(EJ))
    assert [f["job"] for f in r] == ["Compilar", "Publicar"]
