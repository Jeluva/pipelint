# pipelint

Linter por línea de comandos, offline, para archivos `azure-pipelines.yml` de Azure DevOps.
Es un **proyecto de práctica** para mi portfolio: no se conecta a Azure DevOps ni a ninguna API, solo lee el YAML local.

## Qué hace

- `lint`: aplica reglas simples (secretos en texto plano en variables, tareas sin versión `@N`,
  `vmImage: *-latest`, `versionSpec` flotante, `curl | sh`, jobs sin steps, sin timeout, sin trigger).
  Sale con código 1 si hay errores, útil en CI.
- `resumen`: tabla de stages, jobs, cantidad de pasos y pool.
- `variables`: lista las variables y marca las que parecen secretos.
- `tareas`: cuenta las tareas usadas.

Soporta pipelines con `stages`, con `jobs` o solo con `steps`. No valida el esquema completo ni expande templates.

## Cómo correrlo

Requiere Python 3 y PyYAML (`pip install pyyaml`).

```
python3 -m pipelint lint ejemplos/azure-pipelines.yml
python3 -m pipelint resumen ejemplos/azure-pipelines.yml
python3 -m pipelint variables ejemplos/azure-pipelines.yml
python3 -m pipelint tareas ejemplos/azure-pipelines.yml
```

Tests (opcional): `pip install pytest && python3 -m pytest`

## Autor

Jerónimo Luca Vazza (Jeluva)
