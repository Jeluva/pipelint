import argparse
import sys
from . import __version__, core

ORDEN = {"error": 0, "aviso": 1, "info": 2}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pipelint",
        description="Linter offline para azure-pipelines.yml")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n, ayuda in [("lint", "Revisa reglas y buenas practicas"),
                     ("resumen", "Tabla de stages, jobs, pasos y pool"),
                     ("variables", "Lista variables y marca las sospechosas"),
                     ("tareas", "Cuenta las tareas (task@version) usadas")]:
        p = sub.add_parser(n, help=ayuda)
        p.add_argument("archivo")
    a = ap.parse_args(argv)
    try:
        data = core.cargar(a.archivo)
    except (OSError, ValueError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if a.cmd == "lint":
        hall = sorted(core.lint(data), key=lambda h: ORDEN[h[0]])
        for sev, cod, msg in hall:
            print(f"[{sev.upper():5}] {cod} {msg}")
        errores = sum(1 for h in hall if h[0] == "error")
        print(f"\n{len(hall)} hallazgos, {errores} errores")
        return 1 if errores else 0
    if a.cmd == "resumen":
        for f in core.resumen(data):
            print(f"{f['stage']:<14} {f['job']:<16} pasos={f['pasos']:<3} pool={f['pool']}")
    elif a.cmd == "variables":
        for k, v in core.variables(data).items():
            marca = " <-- posible secreto" if core.SECRETO_RE.search(k) and v and not str(v).startswith("$(") else ""
            print(f"{k} = {v}{marca}")
    elif a.cmd == "tareas":
        cuenta = {}
        for _, j in core.jobs_de(data):
            for s in core.pasos(j):
                if isinstance(s, dict) and "task" in s:
                    cuenta[s["task"]] = cuenta.get(s["task"], 0) + 1
        for t, n in sorted(cuenta.items()):
            print(f"{n}x {t}")
    return 0
