"""Pruebas de regresión para el contrato JSON Schema de la especificación."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "data" / "iom_spec.schema.json").read_text(encoding="utf-8"))
SPEC = json.loads((ROOT / "data" / "iom_spec.json").read_text(encoding="utf-8"))


class SpecificationSchemaTests(unittest.TestCase):
    def setUp(self):
        Draft202012Validator.check_schema(SCHEMA)
        self.validator = Draft202012Validator(SCHEMA)

    def test_canonical_spec_conforms_to_schema(self):
        self.assertEqual(list(self.validator.iter_errors(SPEC)), [])

    def test_missing_spec_version_is_rejected(self):
        invalid_spec = copy.deepcopy(SPEC)
        del invalid_spec["spec_version"]
        errors = list(self.validator.iter_errors(invalid_spec))
        self.assertTrue(any("spec_version" in error.message for error in errors))

    def test_malformed_semantic_version_is_rejected(self):
        invalid_spec = copy.deepcopy(SPEC)
        invalid_spec["spec_version"] = "1.1"
        errors = list(self.validator.iter_errors(invalid_spec))
        self.assertTrue(any(list(error.absolute_path) == ["spec_version"] for error in errors))


if __name__ == "__main__":
    unittest.main()
