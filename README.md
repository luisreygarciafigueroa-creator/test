# IOM — formalización, ontología y experimentos empíricos reproducibles

Repositorio ejecutable del marco I.O. El marco se articula con **cinco perspectivas** (Individualidad, Dualidad, Totalidad, Evolución e Involución). El documento de referencia [`docs/MARCOI.O.txt`](docs/MARCOI.O.txt) se conserva íntegro. La especificación operativa de tríadas y vectores está centralizada en [`data/iom_spec.json`](data/iom_spec.json) y transcrita en [`docs/TRIADAS_CATEGORIALES.md`](docs/TRIADAS_CATEGORIALES.md) y [`docs/VECTORES_4_5.md`](docs/VECTORES_4_5.md).

> El código verifica propiedades formales de la especificación y somete hipótesis estructurales a pruebas empíricas reproducibles (Lean, OWL/SHACL, validación cruzada y baselines).

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

- **Cinco perspectivas:** Individualidad (`Ind`), Dualidad (`D`), Totalidad (`Tot`), Evolución (`Evol`) e Involución (`Invol`). Las tres primeras son posicionales en cada tríada; las dos últimas son vectoriales (cuatro secuencias de cinco pasos).
- **Especificación canónica:** 13 tríadas de avance, 13 de retroceso; extremo inicial de avance `involución | vacío | evolución`, extremo final de retroceso `evolución | vacío | involución`; etiquetas con acentos y orden fiel a la tabla de referencia.
- **Lean 4.9.0:** operadores temporales, espejos de posición, cotas de índices vectoriales y teoremas formales; sin `sorry` ni `admit`.
- **RDF/OWL + SHACL:** axiomas de clases y propiedades, dominios/rangos, propiedades funcionales/simetría y restricciones SHACL de estructura, espejo, creación y secuencias vectoriales. El validador ejecuta expansión OWL RL y SHACL.
- **PI-HGAT-T:** clasificador de relaciones `none`/`mirrorOf`/`creates`, PyTorch, semilla fija, validación cruzada leave-one-triad-out y ablaciones sin fase/sin posición. Las métricas se vinculan a las propiedades de la ontología y se reportan de forma completa (por fold, clase y matriz de confusión).
- **Baselines empíricos:** reglas deterministas, regresión logística y MLP sin grafo, comparados bajo la misma partición.
- **Evaluación externa:** conjunto de 60 pares con protocolo de anotación independiente en `datasets/external_eval/`.
- **Datasets reproducibles:** `datasets/triad_nodes.csv` (78 filas), `datasets/vector_steps.csv` (20) y `datasets/relation_candidates.csv` (390).

## Extensiones científicas y técnicas (v1.1)

- **Esquema JSON**: `data/iom_spec.schema.json` + `scripts/validate_spec.py`.
- **Versionado formal**: campo `spec_version` y historial `migrations` en `iom_spec.json`; `scripts/migrate_spec.py`.
- **Pruebas de propiedades**: `tests/test_property_links.py` conecta Lean, CSV y ontología.
- **Relaciones operativas**: `docs/RELACIONES_OPERATIVAS.md` (mirrorOf / creates con ejemplos positivos, negativos y casos límite).
- **Baselines**: `experiments/baselines.py`.
- **Evaluación externa**: `datasets/external_eval/`.
- **Auditoría automática**: `scripts/generate_audit_report.py` → `AUDITORIA_AUTO.md` y `experiments/results/audit_report.json`.

## Archivos importantes

| Ruta | Función |
|---|---|
| `data/iom_spec.json` | Fuente de verdad estructurada de etiquetas, secuencias y reglas |
| `IOM/` y `IOM.lean` | Especificación de estados, operadores y teoremas Lean |
| `ontology/io_ontology.ttl` | Instancias RDF y axiomas OWL generados |
| `ontology/io_shapes.ttl` | Validación SHACL estructural y semántica |
| `scripts/generate_ontology.py` | Generación de Turtle y CSV desde la fuente canónica |
| `scripts/validate_shacl.py` | Comprobación OWL RL y SHACL |
| `experiments/` | Configuración, PI-HGAT-T, baselines, métricas, versiones y logs |
| `datasets/` | CSV regenerables para análisis, entrenamiento y evaluación externa |
| `requirements-lock.txt` | Lock completo de dependencias; `MANIFEST.sha256` identifica artefactos |
| `EXPERIMENTOS.md`, `AUDITORIA.md`, `REPRODUCCION.md`, `paper.md` | Método, trazabilidad, alcance y reproducción |

Para la metodología y la correspondencia de métricas: [`EXPERIMENTOS.md`](EXPERIMENTOS.md). Para ejecutar paso a paso: [`REPRODUCCION.md`](REPRODUCCION.md).
