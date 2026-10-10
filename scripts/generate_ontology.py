#!/usr/bin/env python3
"""Genera RDF/OWL y datasets desde data/iom_spec.json, única fuente tabular."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "data" / "iom_spec.json").read_text(encoding="utf-8"))
IO = Namespace("http://example.org/iom#")
g = Graph()
for prefix, namespace in (("io", IO), ("rdfs", RDFS), ("xsd", XSD), ("owl", OWL)):
    g.bind(prefix, namespace)

# OWL vocabulary: class/property declarations and explicit domains/ranges.
ontology = IO.Ontology
g.add((ontology, RDF.type, OWL.Ontology))
g.add((ontology, OWL.versionInfo, Literal("1.1.0")))
g.add((ontology, RDFS.label, Literal("Ontología IOM", lang="es")))
g.add((ontology, RDFS.comment, Literal(SPEC["source_note"], lang="es")))
classes = ("OntoNode", "VectorStep", "Perspective", "ExpandedCategory", "Position", "Direction", "SourceModel")
for name in classes:
    g.add((IO[name], RDF.type, OWL.Class))
for names in (("OntoNode", "VectorStep", "ExpandedCategory", "Perspective"),):
    axiom = BNode("iomDisjointCoreClasses")
    head = BNode("iomDisjointClassList0")
    g.add((axiom, RDF.type, OWL.AllDisjointClasses))
    g.add((axiom, OWL.members, head))
    cells = [BNode(f"iomDisjointClassList{i}") for i in range(len(names))]
    for index, name in enumerate(names):
        g.add((cells[index], RDF.first, IO[name]))
        g.add((cells[index], RDF.rest, cells[index + 1] if index + 1 < len(cells) else RDF.nil))

object_properties = {
    "hasPerspective": ("OntoNode", "Perspective"),
    "hasPosition": ("OntoNode", "Position"),
    "hasDirection": ("OntoNode", "Direction"),
    "hasVector": ("VectorStep", "Perspective"),
    "mirrorOf": ("OntoNode", "OntoNode"),
    "creates": ("OntoNode", "OntoNode"),
}
datatype_properties = {
    "hasTriadIndex": ("OntoNode", XSD.integer),
    "hasPhase": ("OntoNode", XSD.string),
    "hasLocalPos": ("OntoNode", XSD.integer),
    "hasCyclePhase": ("VectorStep", XSD.string),
    "hasAxisPosition": ("VectorStep", XSD.integer),
    "hasStepIndex": ("VectorStep", XSD.integer),
    "displayArrow": ("VectorStep", XSD.string),
    "hasLevel": ("ExpandedCategory", XSD.integer),
    "declaredTriadCount": ("SourceModel", XSD.integer),
    "declaredPerspectiveCount": ("SourceModel", XSD.integer),
    "declaredOperatorCount": ("SourceModel", XSD.integer),
    "declaredExpandedCategoryCount": ("SourceModel", XSD.integer),
}
for name, (domain, range_) in object_properties.items():
    prop = IO[name]
    g.add((prop, RDF.type, OWL.ObjectProperty))
    g.add((prop, RDFS.domain, IO[domain]))
    g.add((prop, RDFS.range, IO[range_]))
for name, (domain, range_) in datatype_properties.items():
    prop = IO[name]
    g.add((prop, RDF.type, OWL.DatatypeProperty))
    g.add((prop, RDFS.domain, IO[domain]))
    g.add((prop, RDFS.range, range_))
for name in ("hasPerspective", "hasPosition", "hasDirection", "hasVector", "hasTriadIndex", "hasPhase", "hasLocalPos", "hasCyclePhase", "hasAxisPosition", "hasStepIndex", "displayArrow", "hasLevel"):
    g.add((IO[name], RDF.type, OWL.FunctionalProperty))
g.add((IO.mirrorOf, RDF.type, OWL.SymmetricProperty))

for pos in ("left", "center", "right"):
    g.add((IO[pos], RDF.type, OWL.NamedIndividual))
    g.add((IO[pos], RDF.type, IO.Position))
    g.add((IO[pos], RDFS.label, Literal({"left": "Izquierda", "center": "Centro", "right": "Derecha"}[pos], lang="es")))
for direction in ("evol", "invol"):
    g.add((IO[direction], RDF.type, OWL.NamedIndividual))
    g.add((IO[direction], RDF.type, IO.Direction))
# Cinco perspectivas canónicas: Individualidad, Dualidad, Totalidad, Evolución e Involución.
_perspective_labels = SPEC.get("perspective_labels") or {
    "Ind": "Individualidad", "D": "Dualidad", "Tot": "Totalidad",
    "Evol": "Evolución", "Invol": "Involución",
}
for name, label in _perspective_labels.items():
    g.add((IO[name], RDF.type, IO.Perspective))
    g.add((IO[name], RDFS.label, Literal(label, lang="es")))

perspectives = [IO[name] for name in SPEC["perspectives"]]
position_names = SPEC["positions"]
triad_rows = SPEC["triads"]
nodes_csv = []
for phase, rows in triad_rows.items():
    direction = IO[SPEC["phases"][phase]["direction"]]
    for triad_idx, labels in enumerate(rows):
        for pos_idx, label in enumerate(labels):
            node = IO[f"T{triad_idx:02d}_{phase}_P{pos_idx}"]
            g.add((node, RDF.type, IO.OntoNode))
            g.add((node, IO.hasTriadIndex, Literal(triad_idx, datatype=XSD.integer)))
            g.add((node, IO.hasPhase, Literal(phase, datatype=XSD.string)))
            g.add((node, IO.hasLocalPos, Literal(pos_idx, datatype=XSD.integer)))
            g.add((node, IO.hasPosition, IO[position_names[pos_idx]]))
            g.add((node, IO.hasPerspective, perspectives[pos_idx]))
            g.add((node, IO.hasDirection, direction))
            g.add((node, RDFS.label, Literal(label, lang="es")))
            nodes_csv.append({"node_id": str(node).split("#", 1)[1], "triad_index": triad_idx, "phase": phase,
                              "direction": str(direction).split("#", 1)[1], "position_index": pos_idx,
                              "position": position_names[pos_idx], "perspective": SPEC["perspectives"][pos_idx], "label": label})

# Espejos entre fases: se invierten laterales y se conserva el centro.
for triad_idx in range(len(triad_rows["adv"])):
    for pos_idx in range(3):
        adv = IO[f"T{triad_idx:02d}_adv_P{pos_idx}"]
        ret = IO[f"T{triad_idx:02d}_ret_P{2-pos_idx}"]
        g.add((adv, IO.mirrorOf, ret))
        g.add((ret, IO.mirrorOf, adv))

# Aplicar las cuatro reglas de creación indicadas en la fuente estructurada.
for triad_idx in range(len(triad_rows["adv"])):
    for rule in SPEC["creation_rules"]:
        for source_pos in rule["source_positions"]:
            for target_pos in rule["target_positions"]:
                source = IO[f"T{triad_idx:02d}_{rule['source_phase']}_P{source_pos}"]
                target = IO[f"T{triad_idx:02d}_{rule['target_phase']}_P{target_pos}"]
                g.add((source, IO.creates, target))

vector_csv = []
for vector_row in SPEC["vectors"]:
    vector, phase = vector_row["name"], vector_row["phase"]
    for step_index, (label, axis_pos) in enumerate(zip(vector_row["labels"], vector_row["axis_positions"])):
        step = IO[f"vector_{vector.lower()}_{phase}_{step_index}"]
        g.add((step, RDF.type, IO.VectorStep))
        g.add((step, IO.hasVector, IO[vector]))
        g.add((step, IO.hasCyclePhase, Literal(phase, datatype=XSD.string)))
        g.add((step, IO.hasAxisPosition, Literal(axis_pos, datatype=XSD.integer)))
        g.add((step, IO.hasStepIndex, Literal(step_index, datatype=XSD.integer)))
        g.add((step, IO.displayArrow, Literal(vector_row["arrow"], datatype=XSD.string)))
        g.add((step, RDFS.label, Literal(label, lang="es")))
        vector_csv.append({"step_id": str(step).split("#", 1)[1], "vector": vector, "phase": phase,
                           "step_index": step_index, "axis_position": axis_pos, "label": label,
                           "arrow": vector_row["arrow"]})

for level, labels in SPEC["expanded_categories"].items():
    for index, label in enumerate(labels, 1):
        category = IO[f"expanded_L{level}_{index:02d}"]
        g.add((category, RDF.type, IO.ExpandedCategory))
        g.add((category, IO.hasLevel, Literal(int(level), datatype=XSD.integer)))
        g.add((category, RDFS.label, Literal(label, lang="es")))

model = IO.SourceModel
g.add((model, RDF.type, IO.SourceModel))
for prop, value in ((IO.declaredTriadCount, 13), (IO.declaredPerspectiveCount, 5),
                    (IO.declaredOperatorCount, 4), (IO.declaredExpandedCategoryCount, 21)):
    g.add((model, prop, Literal(value, datatype=XSD.integer)))

# Pair-classification dataset for PI-HGAT-T: 36 directed candidates per triad.
relation_csv = []
relation_lookup = {}
for subject, _, obj in g.triples((None, IO.mirrorOf, None)):
    relation_lookup[(str(subject), str(obj))] = "mirrorOf"
for subject, _, obj in g.triples((None, IO.creates, None)):
    relation_lookup[(str(subject), str(obj))] = "creates"
for triad_idx in range(13):
    ids = [IO[f"T{triad_idx:02d}_{phase}_P{pos}"] for phase in ("adv", "ret") for pos in range(3)]
    for source in ids:
        for target in ids:
            if source == target:
                continue
            relation_csv.append({"triad_index": triad_idx, "source": str(source).split("#", 1)[1],
                                 "target": str(target).split("#", 1)[1],
                                 "relation": relation_lookup.get((str(source), str(target)), "none")})

assert len(triad_rows["adv"]) == len(triad_rows["ret"]) == 13
assert len(nodes_csv) == 78
assert len(vector_csv) == 20
assert sum(1 for _ in g.triples((None, IO.creates, None))) == 104
assert len(relation_csv) == 13 * 6 * 5

out = ROOT / "ontology" / "io_ontology.ttl"
out.parent.mkdir(parents=True, exist_ok=True)
g.serialize(destination=str(out), format="turtle")

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

write_csv(ROOT / "datasets" / "triad_nodes.csv", nodes_csv)
write_csv(ROOT / "datasets" / "vector_steps.csv", vector_csv)
write_csv(ROOT / "datasets" / "relation_candidates.csv", relation_csv)
print(f"Tríadas: 13 por fase; nodos: {len(nodes_csv)}; creates: 104; espejos: 78")
print(f"Pasos vectoriales: {len(vector_csv)}; candidatos PI-HGAT-T: {len(relation_csv)}")
print(f"OWL/Turtle: {out}")
