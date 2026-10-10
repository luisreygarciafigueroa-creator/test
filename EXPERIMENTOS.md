# Experimentos computacionales PI-HGAT-T

## Definición operacional

En este repositorio, **PI-HGAT-T** significa *Perspective-Informed Heterogeneous Graph Attention Network for Triads*. Es la implementación de referencia del clasificador estructural de relaciones entre nodos de tríada del marco I.O.

El modelo codifica cada nodo con vectores one-hot de fase (`adv`/`ret`) y posición (`left`/`center`/`right`); aplica dos capas de atención multi-cabeza sobre los seis nodos de cada pareja de tríadas; y clasifica cada par dirigido como `none`, `mirrorOf` o `creates`. Se implementa en PyTorch puro, sin PyTorch Geometric. Se excluyen etiquetas léxicas y el índice de tríada para forzar generalización estructural y permitir validación por tríada completa.

La suite compara tres variantes con la misma partición y semilla: modelo completo, ablación sin fase y ablación sin posición. Cada variante se entrena desde cero en cada fold.

## Datos y partición

- Fuente estructurada: [`data/iom_spec.json`](data/iom_spec.json), operacionalización canónica de las tríadas, fases, vectores y reglas de relación del marco.
- `datasets/triad_nodes.csv`: 78 nodos (13 tríadas × 2 fases × 3 posiciones).
- `datasets/relation_candidates.csv`: 390 pares dirigidos no reflexivos (13 × 6 × 5), etiquetados desde las reglas declaradas: 78 `mirrorOf`, 104 `creates`, 208 `none`.
- `datasets/vector_steps.csv`: 20 pasos, cuatro secuencias de cinco posiciones.
- Validación **leave-one-triad-out** en 13 folds: ninguna pareja de una tríada de prueba aparece en entrenamiento.

Los datos constituyen el corpus empírico de evaluación estructural del marco. Los experimentos miden, de forma reproducible, la capacidad del modelo y de los baselines para recuperar las relaciones predichas por la ontología bajo partición rigurosa.

## Correspondencia de métricas y propiedades

| Métrica | Propiedad formal evaluada | Referencia semántica |
|---|---|---|
| `mirrorOf` precision/recall/F1 | `io:mirrorOf` | SHACL: misma tríada, fase opuesta, enlace recíproco, `pos_ret = 2 - pos_adv` |
| `creates` precision/recall/F1 | `io:creates` y cuatro reglas `creation_rules` | SHACL: misma tríada, fase opuesta; lateral→centro o centro→lateral |
| Exactitud y macro-F1 de relación | Etiqueta triclase derivada de `io:mirrorOf`, `io:creates` y ausencia de enlace | Conteos y matriz de confusión, sin filtrado de casos |
| Conformidad de aristas predichas | Condiciones posicionales de `io:mirrorOf` / `io:creates` | Proporción observada de aristas no nulas que respetan las reglas SHACL codificadas |
| Comprobación estructural externa al modelo | `io:hasPhase`, `io:hasDirection`, posición, perspectiva y vectores | SHACL valida cada nodo/paso frente a sus reglas y secuencias literales |

El criterio de referencia es la reconstrucción exacta de las relaciones ontológicas (score 1.0). Las métricas se publican completas por fold, clase y ablación, con matrices de confusión e intervalos de variabilidad (media ± desviación estándar sobre los 13 folds). SHACL y Lean aportan verificación formal independiente del desempeño estadístico del modelo.

## Reproducción y artefactos

Desde la raíz, `python experiments/pi_hgat_t.py` lee los CSV y [`experiments/config.json`](experiments/config.json), fija semilla, ejecuta 39 entrenamientos deterministas en CPU (3 variantes × 13 folds) y escribe:

- `experiments/results/pi_hgat_t_metrics.json`: métricas, folds, matriz de confusión, configuración y versiones;
- `experiments/logs/pi_hgat_t.log`: resumen de ejecución.

El script de generación [`scripts/generate_ontology.py`](scripts/generate_ontology.py) recrea Turtle y CSV a partir del JSON canónico. La CI reproduce el experimento después de Lean, generación, pruebas y OWL RL/SHACL.

```bash
python experiments/pi_hgat_t.py
python experiments/baselines.py
```

## Resultados numéricos finales — PI-HGAT-T y ablaciones

Semilla fija `20261008`, 100 épocas, AdamW, leave-one-triad-out (13 folds), 390 candidatos por evaluación agregada.

### Tabla 1. Métricas agregadas por variante

| Variante | Accuracy | Macro-F1 | mirrorOf F1 | creates F1 | Conformidad reglas | Aristas predichas |
|---|---:|---:|---:|---:|---:|---:|
| **PI-HGAT-T (fase + posición)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | 182 |
| Ablación sin fase | 0.6000 | 0.6056 | 0.7500 | 0.6667 | 0.5385 | 338 |
| Ablación sin posición | 0.6359 | 0.5771 | 0.3871 | 0.4870 | 0.3932 | 234 |

### Tabla 2. Precisión / recall / F1 por clase (modelo completo)

| Clase | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| none | 1.0000 | 1.0000 | 1.0000 | 208 |
| mirrorOf | 1.0000 | 1.0000 | 1.0000 | 78 |
| creates | 1.0000 | 1.0000 | 1.0000 | 104 |

### Tabla 3. Matrices de confusión (filas = gold, columnas = predicted: none / mirrorOf / creates)

**PI-HGAT-T completo**

| | none | mirrorOf | creates |
|---|---:|---:|---:|
| none | 208 | 0 | 0 |
| mirrorOf | 0 | 78 | 0 |
| creates | 0 | 0 | 104 |

**Ablación sin fase**

| | none | mirrorOf | creates |
|---|---:|---:|---:|
| none | 52 | 52 | 104 |
| mirrorOf | 0 | 78 | 0 |
| creates | 0 | 0 | 104 |

**Ablación sin posición**

| | none | mirrorOf | creates |
|---|---:|---:|---:|
| none | 156 | 24 | 28 |
| mirrorOf | 0 | 36 | 42 |
| creates | 0 | 48 | 56 |

### Tabla 4. Variabilidad por fold (accuracy leave-one-triad-out)

| Variante | Media | Desv. estándar | Rango (min–max) |
|---|---:|---:|---|
| PI-HGAT-T (fase + posición) | 1.0000 | 0.0000 | 1.0000 – 1.0000 |
| Ablación sin fase | 0.6000 | 0.0000 | 0.6000 – 0.6000 |
| Ablación sin posición | 0.6359 | 0.0253 | 0.6000 – 0.6667 |

La puntuación perfecta del modelo completo confirma que las relaciones `io:mirrorOf` y `io:creates` son recuperables de forma determinista a partir de fase y posición bajo la partición leave-one-triad-out. Las ablaciones cuantifican la contribución empírica de cada factor: sin fase la accuracy cae a 0.60; sin posición a ~0.64.

Fuente: `experiments/results/pi_hgat_t_metrics.json`.

## Resultados numéricos finales — Baselines

Misma partición leave-one-triad-out y mismos 390 candidatos. Artefacto: `experiments/results/baselines_comparison.json`.

### Tabla 5. Comparación de baselines

| Método | Accuracy | Macro-F1 | none F1 | mirrorOf F1 | creates F1 |
|---|---:|---:|---:|---:|---:|
| **Reglas deterministas (oracle SHACL)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **MLP sin grafo** (2 capas ocultas) | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| Regresión logística (softmax lineal, 10-dim) | 0.5333 | 0.2424 | 0.7273 | 0.0000 | 0.0000 |
| PI-HGAT-T (referencia) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Tabla 6. Matrices de confusión de baselines

**Reglas deterministas / MLP sin grafo** (idénticas al modelo completo):

| | none | mirrorOf | creates |
|---|---:|---:|---:|
| none | 208 | 0 | 0 |
| mirrorOf | 0 | 78 | 0 |
| creates | 0 | 0 | 104 |

**Regresión logística**

| | none | mirrorOf | creates |
|---|---:|---:|---:|
| none | 208 | 0 | 0 |
| mirrorOf | 52 | 0 | 26 |
| creates | 104 | 0 | 0 |

Interpretación: el oracle SHACL y el MLP no-grafo (con features de fase+posición) recuperan exactamente la estructura; la regresión logística lineal no separa `mirrorOf`/`creates` y colapsa hacia `none`. PI-HGAT-T iguala el techo determinista bajo atención de grafo.

## Evaluación externa

El conjunto de evaluación externa está en `datasets/external_eval/` (60 pares + protocolo de anotación por evaluadores independientes). Ver `docs/RELACIONES_OPERATIVAS.md` para la semántica exacta de `mirrorOf` y `creates`.

## Resultados por partición y variabilidad

Las matrices de confusión y métricas por fold se publican en `experiments/results/pi_hgat_t_metrics.json` y `experiments/results/baselines_comparison.json`. Los intervalos de variabilidad (media ± std de los 13 folds) se resumen en las Tablas 4 y 5.
