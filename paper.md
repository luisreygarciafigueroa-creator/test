# IOM — formalización, ontología y experimentos computacionales reproducibles

## Alcance y procedencia

Este informe describe un marco verificable de extremo a extremo. El documento de referencia se conserva en [`docs/MARCOI.O.txt`](docs/MARCOI.O.txt); la especificación operativa canónica se registra en [`data/iom_spec.json`](data/iom_spec.json). Las hipótesis estructurales del marco se someten a pruebas formales (Lean, OWL/SHACL) y a evaluación empírica reproducible (validación cruzada, ablaciones, baselines y conjunto externo).

## Especificación categorial actualizada

La fuente canónica define trece tríadas por fase. La fase de avance comienza con `involución | vacio | evolución`; la fase de retroceso termina con `evolución | vacio | involución`. Las otras doce filas de cada fase conservan el orden y las etiquetas de la tabla de referencia. Cada concepto se representa como `io:OntoNode` con índices de fila, fase, posición, perspectiva posicional, dirección y etiqueta.

Las columnas corresponden a izquierda/centro/derecha y a metadatos `Ind`/`D`/`Tot`. Esos nombres de perspectiva no sustituyen las etiquetas de las filas categoriales.

Las cuatro reglas de creación generan 104 aristas `io:creates`; los espejos entre fases son recíprocos y cambian izquierda/derecha, preservando centro. Hay 78 nodos de tríadas (13 × 2 fases × 3 posiciones).

## Perspectivas vectoriales cuarta y quinta

Las secuencias vigentes son:

| Vector | Fase | Etiquetas (izquierda a derecha) | Eje | Flecha |
|---|---|---|---|---|
| Evolutivo | Avance | vacio · ind · dua · tot · evol | 0 · 1 · 2 · 3 · 4 | → |
| Evolutivo | Retroceso | evol · tot · dua · ind · vacio | 4 · 3 · 2 · 1 · 0 | ← |
| Involutivo | Avance | invol · tot · dua · ind · vacio | 4 · 3 · 2 · 1 · 0 | → |
| Involutivo | Retroceso | vacio · ind · dua · tot · invol | 0 · 1 · 2 · 3 · 4 | ← |

RDF conserva por separado el índice visual, el eje, la etiqueta y la flecha. Son 20 pasos en total.

## Formalización Lean

`IOM/Core.lean` define el estado `State(time : Int, payload : List String)`, el vacío, deduplicación e inversión. `IOM/Operators.lean` define `E`, `S_fwd`, `Ivo` y `S_rev`, junto con teoremas de composición y del punto fijo estricto del vacío. `IOM/Specification.lean` formaliza posiciones, espejo involutivo, inversión de índice y cotas 0–4. La construcción se compila con Lean 4.9.0 sin `sorry` ni `admit`.

Las pruebas Lean verifican los tipos, operadores y propiedades de posición/espejo que el resto de la cadena empírica asume.

## Ontología y restricciones

`scripts/generate_ontology.py` consume la especificación JSON y genera `ontology/io_ontology.ttl` más tres CSV. El grafo declara vocabulario OWL: clases, propiedades de objeto y de datos, dominios, rangos, propiedades funcionales y simetría de `io:mirrorOf`. `scripts/validate_shacl.py` verifica axiomas esperados, ejecuta expansión OWL RL y evalúa `ontology/io_shapes.ttl`.

SHACL restringe cardinalidad, valores permitidos, fase-dirección, posición-perspectiva, espejo recíproco, `creates` y las cuatro secuencias vectoriales. Las pruebas negativas alteran enlaces/datos para verificar que las formas detectan incompatibilidades.

## Experimento PI-HGAT-T

Se implementa la definición operacional de referencia del repositorio: *Perspective-Informed Heterogeneous Graph Attention Network for Triads*. Un codificador con atención multi-cabeza consume atributos de fase y posición de los seis nodos de cada par de filas; un decodificador predice relaciones dirigidas `none`, `mirrorOf` o `creates`. No usa el rótulo textual ni el índice de tríada.

Los 390 candidatos derivados de las 13 filas se evalúan con 13 particiones leave-one-triad-out. Se ejecutan tres variantes: atributos completos, ablación sin fase y ablación sin posición. Los datasets tienen 78 nodos, 78 aristas dirigidas de espejo, 104 aristas dirigidas `creates` y 208 pares sin relación.

Las métricas se atan explícitamente a las propiedades ontológicas: F1 de `mirrorOf` evalúa inversión lateral y reciprocidad; F1 de `creates` evalúa las cuatro reglas; la conformidad semántica de aristas predichas mide su admisibilidad bajo las reglas que SHACL define.

### Resultados numéricos finales (leave-one-triad-out, semilla 20261008)

**Tabla A. PI-HGAT-T y ablaciones**

| Variante | Accuracy | Macro-F1 | mirrorOf F1 | creates F1 | Conformidad reglas |
|---|---:|---:|---:|---:|---:|
| **PI-HGAT-T (fase + posición)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| Ablación sin fase | 0.6000 | 0.6056 | 0.7500 | 0.6667 | 0.5385 |
| Ablación sin posición | 0.6359 | 0.5771 | 0.3871 | 0.4870 | 0.3932 |

**Tabla B. Matriz de confusión del modelo completo** (filas = gold, columnas = predicted)

| | none | mirrorOf | creates |
|---|---:|---:|---:|
| none | 208 | 0 | 0 |
| mirrorOf | 0 | 78 | 0 |
| creates | 0 | 0 | 104 |

**Tabla C. Variabilidad por fold (accuracy)**

| Variante | Media ± std | Rango |
|---|---|---|
| PI-HGAT-T completo | 1.0000 ± 0.0000 | 1.00 – 1.00 |
| Sin fase | 0.6000 ± 0.0000 | 0.60 – 0.60 |
| Sin posición | 0.6359 ± 0.0253 | 0.60 – 0.67 |

**Tabla D. Baselines (misma partición)**

| Método | Accuracy | Macro-F1 | mirrorOf F1 | creates F1 |
|---|---:|---:|---:|---:|
| Reglas deterministas (oracle SHACL) | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| MLP sin grafo | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Regresión logística | 0.5333 | 0.2424 | 0.0000 | 0.0000 |
| PI-HGAT-T (referencia) | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

La puntuación perfecta del modelo completo y del oracle SHACL confirma la recuperabilidad determinista de `io:mirrorOf` y `io:creates` a partir de fase y posición. Las ablaciones cuantifican el aporte de cada factor. Detalle completo (matrices por ablación, per-class, folds) en [`EXPERIMENTOS.md`](EXPERIMENTOS.md) y en `experiments/results/pi_hgat_t_metrics.json` / `baselines_comparison.json`.

## Reproducción y verificación

Sigue [`REPRODUCCION.md`](REPRODUCCION.md). La CI compila Lean, regenera los artefactos, ejecuta las pruebas, valida OWL RL/SHACL, ejecuta PI-HGAT-T, compara baselines y genera la auditoría automática.

El corpus operativo codifica las reglas del marco de forma estructurada. La cadena Lean + OWL/SHACL + experimentos + baselines + evaluación externa permite comprobar de forma reproducible la consistencia formal y el desempeño empírico estructural del sistema.
