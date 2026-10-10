# IOM — formalización, ontología y experimentos empíricos reproducibles

Repositorio ejecutable del marco I.O. El marco se articula con **cinco perspectivas** (Individualidad, Dualidad, Totalidad, Evolución e Involución). El documento de referencia [`docs/MARCOI.O.txt`](docs/MARCOI.O.txt) se conserva íntegro. La especificación operativa de tríadas y vectores está centralizada en [`data/iom_spec.json`](data/iom_spec.json) y transcrita en [`docs/TRIADAS_CATEGORIALES.md`](docs/TRIADAS_CATEGORIALES.md) y [`docs/VECTORES_4_5.md`](docs/VECTORES_4_5.md).

> El código verifica propiedades formales de la especificación y mide la **recuperación de relaciones estructurales generadas por reglas** (Lean, OWL/SHACL, validación cruzada y baselines). La interpretación humana independiente se estudia por separado en `datasets/independent_eval/`.

## Verificación completa

Requisitos: Elan/Lean 4.9.0, Python 3.12, `venv` e Internet para instalar dependencias.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
lake build
.venv/bin/python scripts/validate_spec.py
.venv/bin/python scripts/generate_ontology.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_shacl.py
.venv/bin/python experiments/pi_hgat_t.py
.venv/bin/python experiments/baselines.py
.venv/bin/python scripts/generate_audit_report.py
```

La CI ejecuta la compilación Lean, genera los artefactos, ejecuta las pruebas, valida OWL RL/SHACL, reproduce PI-HGAT-T, compara baselines y genera el informe de auditoría.

## Contenido verificado

- **Premisas y teoremas:** [`docs/PREMISAS_Y_TEOREMAS.md`](docs/PREMISAS_Y_TEOREMAS.md) — vacío, unidad informativa, infinito, transformación.
- **Cinco perspectivas:** Individualidad (`Ind`), Dualidad (`D`), Totalidad (`Tot`), Evolución (`Evol`) e Involución (`Invol`). Las tres primeras son posicionales en cada tríada; las dos últimas son vectoriales (cuatro secuencias de cinco pasos).
- **Especificación canónica:** 13 tríadas de avance, 13 de retroceso; extremo inicial de avance `involución | vacío | evolución`, extremo final de retroceso `evolución | vacío | involución`; etiquetas con acentos y orden fiel a la tabla de referencia.
- **Lean 4.9.0:** operadores temporales, espejos, reglas `creates`, secuencias vectoriales (`IOM/FormalRules.lean`) y teoremas; sin `sorry` ni `admit`. Los CSV regenerados se comprueban contra los predicados formales (`tests/test_formal_rules_bridge.py`).
- **RDF/OWL + SHACL:** axiomas de clases y propiedades, dominios/rangos, propiedades funcionales/simetría y restricciones SHACL de estructura, espejo, creación y secuencias vectoriales. El validador ejecuta expansión OWL RL y SHACL.
- **PI-HGAT-T:** clasificador de relaciones `none`/`mirrorOf`/`creates`, PyTorch, semilla fija, validación cruzada leave-one-triad-out y ablaciones. Las métricas miden **recuperación de relaciones generadas por reglas** y se reportan por fold, clase y matriz de confusión.
- **Baselines:** reglas deterministas, regresión logística y MLP sin grafo, comparados bajo la misma partición.
- **Evaluación independiente:** `datasets/independent_eval/` (fuera de reglas, conceptos nuevos, ambiguos; protocolo ciego).
- **Evaluación externa (reglas):** conjunto de 60 pares con protocolo de anotación en `datasets/external_eval/`.
- **Datasets reproducibles:** `datasets/triad_nodes.csv` (78 filas), `datasets/vector_steps.csv` (20) y `datasets/relation_candidates.csv` (390).

## Extensiones científicas y técnicas (v1.1)

- **Esquema JSON**: `data/iom_spec.schema.json` + `scripts/validate_spec.py`.
- **Versionado formal**: campo `spec_version` y historial `migrations` en `iom_spec.json`; `scripts/migrate_spec.py`.
- **Pruebas de propiedades**: `tests/test_property_links.py` y `tests/test_formal_rules_bridge.py`.
- **Relaciones operativas**: `docs/RELACIONES_OPERATIVAS.md`.
- **Baselines**: `experiments/baselines.py`.
- **Auditoría automática**: `scripts/generate_audit_report.py`.

Para la metodología: [`EXPERIMENTOS.md`](EXPERIMENTOS.md). Para ejecutar paso a paso: [`REPRODUCCION.md`](REPRODUCCION.md).
