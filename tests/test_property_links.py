#!/usr/bin/env python3
"""Pruebas de propiedades que conectan Lean, CSV y ontología generada."""
from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_spec() -> dict:
    return json.loads((ROOT / "data" / "iom_spec.json").read_text(encoding="utf-8"))


def load_csv(name: str) -> list[dict]:
    with (ROOT / "datasets" / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class PropertyLinksTests(unittest.TestCase):
    """Conectan la especificación JSON, los CSV regenerados y las reglas formales."""

    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec()
        cls.nodes = load_csv("triad_nodes.csv")
        cls.relations = load_csv("relation_candidates.csv")
        cls.vectors = load_csv("vector_steps.csv")
        cls.n_triads = len(cls.spec["triads"]["adv"])

    def test_spec_has_formal_version(self):
        self.assertIn("spec_version", self.spec)
        self.assertRegex(self.spec["spec_version"], r"^\d+\.\d+\.\d+$")
        self.assertIn("schema_version", self.spec)

    def test_node_count_matches_spec(self):
        # 13 tríadas × 2 fases × 3 posiciones = 78
        expected = self.n_triads * 2 * 3
        self.assertEqual(len(self.nodes), expected)
        indices = {int(r["triad_index"]) for r in self.nodes}
        self.assertEqual(indices, set(range(self.n_triads)))

    def test_relation_candidate_count(self):
        # 13 × 6 × 5 = 390 pares dirigidos no reflexivos
        expected = self.n_triads * 6 * 5
        self.assertEqual(len(self.relations), expected)

    def test_gold_relation_counts(self):
        counts = {"none": 0, "mirrorOf": 0, "creates": 0}
        for row in self.relations:
            counts[row["relation"]] += 1
        # mirrorOf: 13 tríadas × 6 nodos / 2 (simétrico) * 2 direcciones?
        # Según EXPERIMENTOS: 78 mirrorOf, 104 creates, 208 none
        self.assertEqual(counts["mirrorOf"], 78)
        self.assertEqual(counts["creates"], 104)
        self.assertEqual(counts["none"], 208)

    def test_mirrorOf_property_holds_in_csv(self):
        """Cada arista mirrorOf respeta: misma tríada, fase opuesta, posición reflejada."""
        for row in self.relations:
            if row["relation"] != "mirrorOf":
                continue
            src, tgt = row["source"], row["target"]
            # node_id formato T{ii}_{phase}_P{pos}
            s_parts = src.split("_")
            t_parts = tgt.split("_")
            self.assertEqual(s_parts[0], t_parts[0], "misma tríada")
            self.assertNotEqual(s_parts[1], t_parts[1], "fase opuesta")
            s_pos = int(s_parts[2][1:])
            t_pos = int(t_parts[2][1:])
            self.assertEqual(t_pos, 2 - s_pos, "posición reflejada")

    def test_creates_property_holds_in_csv(self):
        """Cada arista creates respeta las cuatro reglas de creation_rules."""
        rules = self.spec["creation_rules"]
        allowed = set()
        for rule in rules:
            for sp in rule["source_positions"]:
                for tp in rule["target_positions"]:
                    allowed.add((rule["source_phase"], sp, rule["target_phase"], tp))
        for row in self.relations:
            if row["relation"] != "creates":
                continue
            s_parts = row["source"].split("_")
            t_parts = row["target"].split("_")
            key = (s_parts[1], int(s_parts[2][1:]), t_parts[1], int(t_parts[2][1:]))
            self.assertIn(key, allowed, f"creates no permitido: {row['source']} -> {row['target']}")

    def test_vector_steps_count(self):
        # 4 vectores × 5 pasos = 20
        self.assertEqual(len(self.vectors), 20)

    def test_lean_operators_file_exists_and_mentions_mirror(self):
        """El código Lean debe existir y referenciar los operadores de espejo."""
        lean_spec = (ROOT / "IOM" / "Specification.lean").read_text(encoding="utf-8")
        self.assertIn("mirror", lean_spec.lower())
        self.assertIn("TriadPosition", lean_spec)
        self.assertTrue((ROOT / "IOM" / "Core.lean").exists())
        self.assertTrue((ROOT / "IOM" / "Operators.lean").exists())

    def test_ontology_ttl_contains_mirrorOf_and_creates(self):
        ttl = (ROOT / "ontology" / "io_ontology.ttl").read_text(encoding="utf-8")
        self.assertIn("mirrorOf", ttl)
        self.assertIn("creates", ttl)
        self.assertIn("OntoNode", ttl)

    def test_shacl_shapes_exist(self):
        shapes = (ROOT / "ontology" / "io_shapes.ttl").read_text(encoding="utf-8")
        self.assertIn("mirrorOf", shapes)
        self.assertIn("creates", shapes)


if __name__ == "__main__":
    unittest.main()
