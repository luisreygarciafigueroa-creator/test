#!/usr/bin/env python3
"""Puente: las relaciones del CSV deben satisfacer los predicados formales
codificados en IOM/FormalRules.lean (isMirror / isCreates / conteos)."""
from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_relations():
    with (ROOT / "datasets" / "relation_candidates.csv").open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def parse_node(node_id: str) -> tuple[str, int]:
    m = re.fullmatch(r"T\d{2}_(adv|ret)_P([0-2])", node_id)
    assert m, node_id
    return m.group(1), int(m.group(2))


def is_mirror(src: str, tgt: str) -> bool:
    sp, spos = parse_node(src)
    tp, tpos = parse_node(tgt)
    return sp != tp and tpos == 2 - spos


def is_creates(src: str, tgt: str) -> bool:
    sp, spos = parse_node(src)
    tp, tpos = parse_node(tgt)
    if sp == tp:
        return False
    lateral_s = spos in (0, 2)
    lateral_t = tpos in (0, 2)
    return (lateral_s and tpos == 1) or (spos == 1 and lateral_t)


def same_triad(src: str, tgt: str) -> bool:
    return src.split("_")[0] == tgt.split("_")[0]


class FormalRulesBridgeTests(unittest.TestCase):
    """Comprueba que el JSON/CSV regenerado cumple los predicados Lean."""

    @classmethod
    def setUpClass(cls):
        cls.rows = load_relations()
        cls.lean = (ROOT / "IOM" / "FormalRules.lean").read_text(encoding="utf-8")

    def test_lean_defines_isMirror_and_isCreates(self):
        self.assertIn("def isMirror", self.lean)
        self.assertIn("def isCreates", self.lean)
        self.assertIn("expectedMirrorDirected", self.lean)
        self.assertIn("expectedCreatesDirected", self.lean)

    def test_every_mirrorOf_satisfies_isMirror(self):
        for row in self.rows:
            if row["relation"] != "mirrorOf":
                continue
            self.assertTrue(same_triad(row["source"], row["target"]))
            self.assertTrue(
                is_mirror(row["source"], row["target"]),
                f"mirrorOf viola isMirror: {row['source']} -> {row['target']}",
            )
            self.assertFalse(
                is_creates(row["source"], row["target"]),
                f"mirrorOf no debe ser creates: {row}",
            )

    def test_every_creates_satisfies_isCreates(self):
        for row in self.rows:
            if row["relation"] != "creates":
                continue
            self.assertTrue(same_triad(row["source"], row["target"]))
            self.assertTrue(
                is_creates(row["source"], row["target"]),
                f"creates viola isCreates: {row['source']} -> {row['target']}",
            )
            self.assertFalse(
                is_mirror(row["source"], row["target"]),
                f"creates no debe ser mirror: {row}",
            )

    def test_none_satisfies_neither(self):
        for row in self.rows:
            if row["relation"] != "none":
                continue
            if not same_triad(row["source"], row["target"]):
                continue
            self.assertFalse(is_mirror(row["source"], row["target"]), row)
            self.assertFalse(is_creates(row["source"], row["target"]), row)

    def test_counts_match_lean_constants(self):
        from collections import Counter
        c = Counter(r["relation"] for r in self.rows)
        self.assertEqual(c["mirrorOf"], 78)
        self.assertEqual(c["creates"], 104)
        self.assertEqual(c["none"], 208)
        self.assertIn("78", self.lean)
        self.assertIn("104", self.lean)
        self.assertIn("208", self.lean)

    def test_partition_complete(self):
        for row in self.rows:
            if not same_triad(row["source"], row["target"]):
                continue
            m = is_mirror(row["source"], row["target"])
            c = is_creates(row["source"], row["target"])
            self.assertFalse(m and c, row)
            if row["relation"] == "mirrorOf":
                self.assertTrue(m)
            elif row["relation"] == "creates":
                self.assertTrue(c)
            else:
                self.assertFalse(m or c)


if __name__ == "__main__":
    unittest.main()
