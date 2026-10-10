# Auditoría automática IOM

**Generado:** 2026-10-10T17:09:01.543091+00:00
**Commit:** `0ff1a35` (`0ff1a350db12a119fe5ae6b2d0f78a8dfe662212`)
**Rama:** `main`
**spec_version:** 1.1.0
**schema_version:** 1.0.0

## Hashes SHA-256 de artefactos de datos

| Archivo | SHA-256 |
|---|---|
| `data/iom_spec.json` | `0706633868c0b046efa3e077a8709f171f6ebe36558326465e43f9992925c557` |
| `data/iom_spec.schema.json` | `8eacf877757e0250f3d0aa6c02b30ad309502473647e04ef547a946eae597e19` |
| `datasets/triad_nodes.csv` | `d3e94aa0c8402212cf18cf68777e073b9ec84063b25268f8cae0c43a8f595a48` |
| `datasets/relation_candidates.csv` | `637c50cf23667942d05f50773f113834aa0ce0927b64c8790f294316ca3627a9` |
| `datasets/vector_steps.csv` | `2c9823da1042eec9d4ab3448c6e44a4b83ee836af1191c77678f8baf3c06d9f9` |
| `ontology/io_ontology.ttl` | `ce7e9288bd2767e5553aafd6f8ef0b30d8e4ec5a7ec73a6fd0fa9ef4f390b62d` |
| `ontology/io_shapes.ttl` | `60a4c06209d75d6b3629792ff3cb70032c2610c92b27a6c160565535f81464d4` |
| `requirements-lock.txt` | `73593871a75c2a4f71f827a31b86281fc6aaa6d40891263588b97baf8df4e915` |
| `experiments/config.json` | `5d284eb9c04c386a90b6e835483bcaf36acf84469b52559891c1bb73d27d15a6` |

## Entorno

- Python: 3.12.3
- Platform: Linux-6.18.38+-x86_64-with-glibc2.39

## Métricas primarias PI-HGAT-T

- **candidate_relation_accuracy**: 1.0
- **relation_macro_f1**: 1.0
- **mirrorOf_precision**: 1.0
- **mirrorOf_recall**: 1.0
- **mirrorOf_f1**: 1.0
- **creates_precision**: 1.0
- **creates_recall**: 1.0
- **creates_f1**: 1.0
- **predicted_edge_rule_conformance**: 1.0

## Resumen de baselines

- **deterministic_rules**: accuracy=1.0, macro_f1=1.0
- **logistic_regression**: accuracy=0.533333, macro_f1=0.242424
- **mlp_no_graph**: accuracy=1.0, macro_f1=1.0

## Estado del working tree

```
M MANIFEST.sha256
 M experiments/logs/pi_hgat_t.log
 M experiments/results/baselines_comparison.json
```

---
Generado por `scripts/generate_audit_report.py`.
