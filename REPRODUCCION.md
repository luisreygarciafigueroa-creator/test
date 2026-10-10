# Reproducción de IOM

La cadena ejecutable comprueba el modelo formalizado del marco de **cinco perspectivas** (Individualidad, Dualidad, Totalidad, Evolución e Involución) y reproduce una suite de experimentos empíricos estructurales. Los resultados son medibles, auditables y reproducibles de extremo a extremo.

## Entorno fijado

- Python 3.12 (versión exacta en `experiments/results/software_versions.json`).
- Lean 4.9.0, fijado en `lean-toolchain` mediante Elan.
- Dependencias Python con versiones directas fijadas en `requirements.txt` y lock completo en `requirements-lock.txt`; PyTorch CPU 2.6.0.
- Sistema CI: Ubuntu 24.04.

Instala Elan/Lean si es necesario:

```bash
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y --default-toolchain leanprover/lean4:v4.9.0
export PATH="$HOME/.elan/bin:$PATH"
```

## Reproducción integral

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
.venv/bin/python scripts/capture_environment.py
.venv/bin/python scripts/create_manifest.py
.venv/bin/python scripts/package_reproducible.py
```

La generación toma `data/iom_spec.json` como fuente única y actualiza `ontology/io_ontology.ttl` y los CSV en `datasets/`. El experimento escribe el resultado JSON y el log. La captura registra versiones reales, el manifiesto genera hashes SHA-256 y el empaquetador crea `dist/IOM-reproducible.zip` con código, Lean, RDF/OWL, SHACL, datasets, configuración, dependencias, resultados, logs y documentación.

## Criterios de comprobación

1. `lake build` compila los cuatro operadores y los teoremas de posiciones/espejos/vectores sin `sorry` ni `admit`.
2. El generador produce 78 nodos, 104 aristas `creates`, 78 aristas dirigidas de espejo, 20 pasos vectoriales y 390 candidatos de relación.
3. Las pruebas comparan literalmente las 26 filas de tríadas (13 de avance y 13 de retroceso) y las cuatro secuencias vectoriales; incluyen mutaciones negativas.
4. OWL RL infiere tipos por dominios/rangos y SHACL valida reglas, cardinalidades, direcciones, espejos, enlaces y secuencias vectoriales.
5. La suite ejecuta PI-HGAT-T completo y ablaciones sin fase/sin posición, con 13 folds leave-one-triad-out cada una. Las métricas se vinculan a propiedades ontológicas y se reportan de forma completa (por fold, clase, matriz de confusión y variabilidad).
6. Los baselines (reglas deterministas, regresión logística, MLP) se evalúan bajo la misma partición para comparación empírica controlada.

## Reproducir etapas individuales

```bash
lake build
.venv/bin/python scripts/generate_ontology.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_shacl.py
.venv/bin/python experiments/pi_hgat_t.py
```

La metodología y las métricas están en [`EXPERIMENTOS.md`](EXPERIMENTOS.md). La fuente de referencia `docs/MARCOI.O.txt` se conserva; la especificación operativa actualizada se registra en `data/iom_spec.json` y los anexos.

## Pasos adicionales v1.1

```bash
# Validar esquema y migraciones
.venv/bin/python scripts/validate_spec.py
.venv/bin/python scripts/migrate_spec.py --check

# Pruebas de propiedades (Lean ↔ CSV ↔ ontología)
.venv/bin/python -m unittest tests.test_property_links -v

# Baselines
.venv/bin/python experiments/baselines.py

# Auditoría automática (commit + hashes + métricas)
.venv/bin/python scripts/generate_audit_report.py
```
