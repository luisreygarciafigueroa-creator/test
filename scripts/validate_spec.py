#!/usr/bin/env python3
"""Valida data/iom_spec.json contra data/iom_spec.schema.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ModuleNotFoundError as exc:
    if exc.name != "jsonschema":
        raise
    print(
        "ERROR: falta la dependencia obligatoria jsonschema; "
        "instala requirements-lock.txt antes de validar.",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "iom_spec.json"
SCHEMA_PATH = ROOT / "data" / "iom_spec.schema.json"


def main() -> int:
    for path in (SCHEMA_PATH, SPEC_PATH):
        if not path.is_file():
            print(f"ERROR: no existe el archivo requerido: {path}", file=sys.stderr)
            return 1
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        instance = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: no se pudo leer JSON válido: {exc}", file=sys.stderr)
        return 1
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        print(f"ERROR: el esquema {SCHEMA_PATH.name} no es válido: {exc.message}", file=sys.stderr)
        return 1
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(map(str, e.absolute_path)))
    if errors:
        for err in errors:
            path = ".".join(str(p) for p in err.absolute_path) or "<root>"
            print(f"ERROR {path}: {err.message}", file=sys.stderr)
        return 1
    print(f"OK: {SPEC_PATH.name} cumple el esquema {SCHEMA_PATH.name}")
    print(
        f"  schema_version={instance.get('schema_version')}  "
        f"spec_version={instance.get('spec_version')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
