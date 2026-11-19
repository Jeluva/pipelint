"""Lectura y reglas de lint para azure-pipelines.yml (sin red, solo YAML)."""
import re
import yaml

SECRETO_RE = re.compile(r"(password|passwd|pwd|secret|token|apikey|api_key|key)", re.I)
VERSION_FLOTANTE = {"latest", "*", ""}


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("El YAML no es un mapa de nivel superior")
    return data


def jobs_de(data):
    """Devuelve lista de (stage, job_dict) normalizando pipelines con o sin stages."""
    out = []
    if "stages" in data:
        for st in data["stages"] or []:
            for j in st.get("jobs", []) or []:
                out.append((st.get("stage", "?"), j))
    elif "jobs" in data:
        for j in data["jobs"] or []:
            out.append(("(sin stage)", j))
    elif "steps" in data:
        out.append(("(sin stage)", {"job": "(implicito)", "steps": data["steps"],
                                    "pool": data.get("pool")}))
    return out


def pasos(job):
    return job.get("steps", []) or []


def variables(data):
    """Normaliza variables a dict nombre->valor (acepta mapa o lista name/value)."""
    v = data.get("variables") or {}
    if isinstance(v, dict):
        return dict(v)
    res = {}
    for item in v:
        if isinstance(item, dict) and "name" in item:
            res[item["name"]] = item.get("value")
    return res


def resumen(data):
    filas = []
    for stage, j in jobs_de(data):
        nombre = j.get("job") or j.get("deployment") or "?"
        filas.append({"stage": stage, "job": nombre, "pasos": len(pasos(j)),
                      "pool": _pool(j, data)})
    return filas


def _pool(job, data):
    p = job.get("pool") or data.get("pool")
    if isinstance(p, dict):
        return p.get("vmImage") or p.get("name") or "?"
    return p or "(ninguno)"


def lint(data):
    """Devuelve lista de (severidad, codigo, mensaje)."""
    h = []
    if "trigger" not in data and "pr" not in data:
        h.append(("aviso", "P001", "No define trigger ni pr: usa el CI por defecto de la rama"))
    jobs = jobs_de(data)
    if not jobs:
        h.append(("error", "P002", "No hay jobs, stages ni steps"))
    for nombre, valor in variables(data).items():
        if valor and isinstance(valor, str) and SECRETO_RE.search(nombre) \
                and not valor.startswith("$("):
            h.append(("error", "P003",
                      f"Variable '{nombre}' parece un secreto con valor en texto plano"))
    for stage, j in jobs:
        jn = j.get("job") or j.get("deployment") or "?"
        pool = _pool(j, data)
        if isinstance(pool, str) and re.search(r"-latest$", pool):
            h.append(("aviso", "P004",
                      f"{stage}/{jn}: pool '{pool}' flotante, puede cambiar sin avisar"))
        if not pasos(j) and "deployment" not in j:
            h.append(("error", "P005", f"{stage}/{jn}: job sin steps"))
        if "timeoutInMinutes" not in j:
            h.append(("info", "P006", f"{stage}/{jn}: sin timeoutInMinutes (default 60)"))
        for s in pasos(j):
            tarea = s.get("task") if isinstance(s, dict) else None
            if tarea and "@" not in tarea:
                h.append(("error", "P007", f"{stage}/{jn}: tarea '{tarea}' sin version (@N)"))
            for linea in str(s.get("script", "")).splitlines() if isinstance(s, dict) else []:
                if re.search(r"curl[^|]*\|\s*(sudo\s+)?(ba)?sh", linea):
                    h.append(("aviso", "P008",
                              f"{stage}/{jn}: curl | sh ejecuta codigo remoto sin verificar"))
            ver = (s.get("inputs") or {}).get("versionSpec") if isinstance(s, dict) else None
            if ver is not None and str(ver) in VERSION_FLOTANTE:
                h.append(("aviso", "P009", f"{stage}/{jn}: versionSpec flotante '{ver}'"))
    return h
