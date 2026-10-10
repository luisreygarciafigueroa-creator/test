#!/usr/bin/env python3
"""PI-HGAT-T y ablaciones: evaluación empírica estructural de tríadas IOM.

PI-HGAT-T es la implementación de referencia del clasificador de relaciones del marco.
Las etiquetas de clase proceden de reglas RDF/SHACL explícitas y se evalúan bajo
leave-one-triad-out, ablaciones y baselines.
"""
from __future__ import annotations

import csv
import json
import platform
import random
import time
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "experiments" / "config.json").read_text(encoding="utf-8"))
CLASSES = ("none", "mirrorOf", "creates")
CLASS_ID = {name: i for i, name in enumerate(CLASSES)}


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)


def features_for_node(node_id: str) -> list[float]:
    """Codifica solo la fase y posición, sin etiqueta léxica ni número de tríada."""
    parts = node_id.split("_")
    phase, position = parts[1], int(parts[2][1:])
    return [float(phase == "adv"), float(phase == "ret"),
            float(position == 0), float(position == 1), float(position == 2)]


def parse_pair_index(node_id: str) -> int:
    phase = node_id.split("_")[1]
    position = int(node_id.split("_")[2][1:])
    return position if phase == "adv" else 3 + position


def read_data():
    nodes: dict[int, list[list[float]]] = {i: [None] * 6 for i in range(13)}
    with (ROOT / "datasets" / "triad_nodes.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            nodes[int(row["triad_index"])][parse_pair_index(row["node_id"])] = features_for_node(row["node_id"])
    pairs: dict[int, list[tuple[int, int, int]]] = {i: [] for i in range(13)}
    with (ROOT / "datasets" / "relation_candidates.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            pairs[int(row["triad_index"])].append((parse_pair_index(row["source"]),
                                                     parse_pair_index(row["target"]),
                                                     CLASS_ID[row["relation"]]))
    assert all(all(feature is not None for feature in group) for group in nodes.values())
    return {k: torch.tensor(v, dtype=torch.float32) for k, v in nodes.items()}, pairs


class TypedGraphAttention(nn.Module):
    """Atención multi-cabeza sobre los seis nodos de las dos fases de cada tríada."""
    def __init__(self, dim: int, heads: int):
        super().__init__()
        assert dim % heads == 0
        self.dim, self.heads, self.head_dim = dim, heads, dim // heads
        self.query = nn.Linear(dim, dim, bias=False)
        self.key = nn.Linear(dim, dim, bias=False)
        self.value = nn.Linear(dim, dim, bias=False)
        self.out = nn.Linear(dim, dim)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, n_nodes, _ = x.shape
        def split(layer):
            return layer(x).view(batch, n_nodes, self.heads, self.head_dim).transpose(1, 2)
        q, k, v = split(self.query), split(self.key), split(self.value)
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        weights = torch.softmax(scores, dim=-1)
        attended = torch.matmul(weights, v).transpose(1, 2).contiguous().view(batch, n_nodes, self.dim)
        return self.norm(x + self.out(attended))


class PIHGATT(nn.Module):
    """Codificador GAT de dos capas y decodificador para relación dirigida."""
    def __init__(self, dim: int = 32, heads: int = 4, input_dim: int = 5):
        super().__init__()
        self.encoder = nn.Linear(input_dim, dim)
        self.attention1 = TypedGraphAttention(dim, heads)
        self.attention2 = TypedGraphAttention(dim, heads)
        self.decoder = nn.Sequential(nn.Linear(dim * 3, dim), nn.GELU(), nn.Linear(dim, len(CLASSES)))

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        h = F.gelu(self.encoder(x))
        h = F.gelu(self.attention1(h))
        return self.attention2(h)

    def forward(self, x: torch.Tensor, pairs: torch.Tensor) -> torch.Tensor:
        h = self.encode(x)
        src, dst = pairs[:, 0], pairs[:, 1]
        left, right = h[:, src, :], h[:, dst, :]
        return self.decoder(torch.cat((left, right, left * right), dim=-1))


def admissible_relation(label: str, source: int, target: int) -> bool:
    """Predicados de validez alineados con io:mirrorOf / io:creates en SHACL."""
    source_phase, source_pos = (0 if source < 3 else 1), source % 3
    target_phase, target_pos = (0 if target < 3 else 1), target % 3
    if source_phase == target_phase:
        return False
    if label == "mirrorOf":
        return target_pos == 2 - source_pos
    if label == "creates":
        return (source_pos in (0, 2) and target_pos == 1) or (source_pos == 1 and target_pos in (0, 2))
    return True


def scores(gold: list[int], predicted: list[int]) -> dict:
    matrix = [[0] * len(CLASSES) for _ in CLASSES]
    for actual, guess in zip(gold, predicted):
        matrix[actual][guess] += 1
    per_class, f1_values = {}, []
    for idx, name in enumerate(CLASSES):
        tp = matrix[idx][idx]
        fp = sum(matrix[row][idx] for row in range(len(CLASSES)) if row != idx)
        fn = sum(matrix[idx][col] for col in range(len(CLASSES)) if col != idx)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[name] = {"precision": precision, "recall": recall, "f1": f1, "support": tp + fn}
        f1_values.append(f1)
    accuracy = sum(a == b for a, b in zip(gold, predicted)) / len(gold)
    return {"accuracy": accuracy, "macro_f1": sum(f1_values) / len(f1_values),
            "per_class": per_class, "confusion_matrix_rows_gold_cols_predicted": matrix}


def run_variant(name: str, columns: list[int], nodes, relations, cfg: dict) -> dict:
    all_gold, all_pred, predicted_edges, fold_results = [], [], [], []
    pair_indices = torch.tensor([(s, t) for s in range(6) for t in range(6) if s != t], dtype=torch.long)
    for held_out in sorted(nodes):
        seed_everything(int(cfg["seed"]) + held_out)
        train_ids = [i for i in nodes if i != held_out]
        x_train = torch.stack([nodes[i][:, columns] for i in train_ids])
        y_train = torch.tensor([label for i in train_ids for _s, _t, label in relations[i]], dtype=torch.long)
        model = PIHGATT(int(cfg["hidden_dim"]), int(cfg["attention_heads"]), input_dim=len(columns))
        counts = torch.bincount(y_train, minlength=len(CLASSES)).float()
        class_weights = (len(y_train) / (len(CLASSES) * counts.clamp_min(1))).float()
        optimizer = torch.optim.AdamW(model.parameters(), lr=float(cfg["learning_rate"]),
                                      weight_decay=float(cfg["weight_decay"]))
        model.train()
        for _epoch in range(int(cfg["epochs"])):
            optimizer.zero_grad(set_to_none=True)
            logits = model(x_train, pair_indices).reshape(-1, len(CLASSES))
            loss = F.cross_entropy(logits, y_train, weight=class_weights)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            predicted = model(nodes[held_out][:, columns].unsqueeze(0), pair_indices).argmax(dim=-1).reshape(-1).tolist()
        gold_map = {(src, dst): label for src, dst, label in relations[held_out]}
        gold = [gold_map[(src, dst)] for src, dst in pair_indices.tolist()]
        all_gold.extend(gold)
        all_pred.extend(predicted)
        for (src, dst), label_id in zip(pair_indices.tolist(), predicted):
            if label_id:
                label = CLASSES[label_id]
                predicted_edges.append((held_out, src, dst, label))
        fold_results.append({"held_out_triad": held_out,
                             "accuracy": sum(a == b for a, b in zip(gold, predicted)) / len(gold)})
    report = scores(all_gold, all_pred)
    by_class = report["per_class"]
    compliant = sum(admissible_relation(label, source, target)
                    for _triad, source, target, label in predicted_edges)
    edge_compliance = compliant / len(predicted_edges) if predicted_edges else 1.0
    metrics = {
        "candidate_relation_accuracy": {"value": report["accuracy"], "property": "io:mirrorOf / io:creates; exact three-class labels"},
        "relation_macro_f1": {"value": report["macro_f1"], "property": "balanced F1 for none, io:mirrorOf and io:creates"},
        "mirrorOf_precision": {"value": by_class["mirrorOf"]["precision"], "property": "SHACL: reciprocal mirror; same triad; opposite phase; position reflection"},
        "mirrorOf_recall": {"value": by_class["mirrorOf"]["recall"], "property": "completeness of the io:mirrorOf edge set"},
        "mirrorOf_f1": {"value": by_class["mirrorOf"]["f1"], "property": "precision/recall of io:mirrorOf"},
        "creates_precision": {"value": by_class["creates"]["precision"], "property": "SHACL: same triad, opposite phase, four allowed position rules"},
        "creates_recall": {"value": by_class["creates"]["recall"], "property": "completeness of four creation rules"},
        "creates_f1": {"value": by_class["creates"]["f1"], "property": "precision/recall of io:creates"},
        "predicted_edge_rule_conformance": {"value": edge_compliance, "property": "SHACL phase/triad/position rules for predicted mirrorOf and creates", "predicted_edges": len(predicted_edges)},
    }
    return {"variant": name, "feature_columns": columns, "metrics": metrics,
            "per_class": by_class, "confusion_matrix_rows_gold_cols_predicted": report["confusion_matrix_rows_gold_cols_predicted"],
            "folds": fold_results}


def run() -> dict:
    cfg = CONFIG
    nodes, relations = read_data()
    candidates = [
        ("PI-HGAT-T_full_phase_and_position", [0, 1, 2, 3, 4]),
        ("ablation_without_phase", [2, 3, 4]),
        ("ablation_without_position", [0, 1]),
    ]
    start = time.time()
    variants = [run_variant(name, columns, nodes, relations, cfg) for name, columns in candidates]
    primary = variants[0]
    gold_labels = [label for triad in relations.values() for _src, _dst, label in triad]
    dataset = {"triads": 13, "nodes": 78, "directed_relation_candidates": len(gold_labels),
               "gold_mirrorOf_edges": sum(label == CLASS_ID["mirrorOf"] for label in gold_labels),
               "gold_creates_edges": sum(label == CLASS_ID["creates"] for label in gold_labels),
               "gold_none_pairs": sum(label == CLASS_ID["none"] for label in gold_labels)}
    report = {
        "model": cfg["model_id"],
        "model_definition": cfg["model_definition"],
        "dataset": dataset,
        "validation": "13-fold leave-one-triad-out; no lexical labels or triad index as model features",
        "primary_metrics": primary["metrics"],
        "experiments": variants,
        "threshold_policy": "Empirical evaluation against deterministic RDF/SHACL target properties. Reference criterion is exact reconstruction (1.0); observed model and ablation scores quantify recoverability under leave-one-triad-out and are reported with confusion matrices and fold variability.",
        "software": {"python": platform.python_version(), "pytorch": torch.__version__, "platform": platform.platform()},
        "configuration": cfg,
    }
    results_path = ROOT / "experiments" / "results" / "pi_hgat_t_metrics.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log_path = ROOT / "experiments" / "logs" / "pi_hgat_t.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["PI-HGAT-T / ablation suite", f"Python={platform.python_version()} PyTorch={torch.__version__}",
             f"seed={cfg['seed']} folds=13 epochs={cfg['epochs']} candidates={len(gold_labels)}"]
    for variant in variants:
        m = variant["metrics"]
        lines.append(f"{variant['variant']}: accuracy={m['candidate_relation_accuracy']['value']:.6f} macro_f1={m['relation_macro_f1']['value']:.6f} "
                     f"mirrorOf_f1={m['mirrorOf_f1']['value']:.6f} creates_f1={m['creates_f1']['value']:.6f} "
                     f"rule_conformance={m['predicted_edge_rule_conformance']['value']:.6f}")
    lines.append(f"runtime_seconds={time.time() - start:.3f}")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"Resultados: {results_path}")
    return report


if __name__ == "__main__":
    run()
