# IOM — formalización, ontología y experimentos computacionales reproducibles

## Alcance y procedencia

Este informe describe un marco verificable de extremo a extremo. El documento de referencia se conserva en [`docs/MARCOI.O.txt`](docs/MARCOI.O.txt); la especificación operativa canónica se registra en [`data/iom_spec.json`](data/iom_spec.json). Las afirmaciones del marco sobre **vacío**, **unidad informativa**, **infinito** y **transformación**, separadas en premisas asumidas y teoremas derivados, constan en [`docs/PREMISAS_Y_TEOREMAS.md`](docs/PREMISAS_Y_TEOREMAS.md). La formalización Lean de espejos, creates y vectores está en `IOM/FormalRules.lean`.

Las hipótesis estructurales del marco se someten a pruebas formales (Lean, OWL/SHACL) y a evaluación de **recuperación de relaciones generadas por reglas** (validación cruzada, ablaciones, baselines). La interpretación humana independiente se estudia en `datasets/independent_eval/`.

## Especificación categorial actualizada

La fuente canónica define trece tríadas por fase. La fase de avance comienza con `involución | vacío | evolución`; la fase de retroceso termina con `evolución | vacío | involución`. Las otras doce filas de cada fase conservan el orden y las etiquetas de la tabla de referencia. Cada concepto se representa como `io:OntoNode` con índices de fila, fase, posición, perspectiva posicional, dirección y etiqueta.

El marco comprende **cinco perspectivas**: Individualidad (`Ind`), Dualidad (`D`), Totalidad (`Tot`), Evolución (`Evol`) e Involución (`Invol`). Las tres primeras son posicionales (izquierda/centro/derecha en cada tríada) y no sustituyen las etiquetas categoriales de las filas. Las dos últimas son vectoriales y describen las direcciones de flujo informativo.

Las cuatro reglas de creación generan 104 aristas `io:creates`; los espejos entre fases son recíprocos y cambian izquierda/derecha, preservando centro. Hay 78 nodos de tríadas (13 × 2 fases × 3 posiciones).

## Perspectivas cuarta y quinta: Evolución e Involución

Las secuencias vigentes son:

| Vector | Fase | Etiquetas (izquierda a derecha) | Eje | Flecha |
|---|---|---|---|---|
| Evolución | Avance | vacío · ind · dua · tot · evol | 0 · 1 · 2 · 3 · 4 | → |
| Evolución | Retroceso | evol · tot · dua · ind · vacío | 4 · 3 · 2 · 1 · 0 | ← |
| Involución | Avance | invol · tot · dua · ind · vacío | 4 · 3 · 2 · 1 · 0 | → |
| Involución | Retroceso | vacío · ind · dua · tot · invol | 0 · 1 · 2 · 3 · 4 | ← |

RDF conserva por separado el índice visual, el eje, la etiqueta y la flecha. Son 20 pasos en total.

## Formalización Lean

`IOM/Core.lean` define el estado `State(time : Int, payload : List String)`, el vacío, deduplicación e inversión. `IOM/Operators.lean` define `E`, `S_fwd`, `Ivo` y `S_rev`, junto con teoremas de composición y del punto fijo estricto del vacío. `IOM/Specification.lean` formaliza posiciones, espejo involutivo, inversión de índice y cotas 0–4. `IOM/FormalRules.lean` codifica los predicados `isMirror` e `isCreates` y los conteos canónicos; las relaciones del CSV se comprueban contra esos predicados (`tests/test_formal_rules_bridge.py`). La construcción se compila con Lean 4.9.0 sin `sorry` ni `admit`.

## Ontología y restricciones

`scripts/generate_ontology.py` consume la especificación JSON y genera `ontology/io_ontology.ttl` más tres CSV. El grafo declara vocabulario OWL: clases, propiedades de objeto y de datos, dominios, rangos, propiedades funcionales y simetría de `io:mirrorOf`. `scripts/validate_shacl.py` verifica axiomas esperados, ejecuta expansión OWL RL y evalúa `ontology/io_shapes.ttl`.

## Experimento PI-HGAT-T (recuperación de relaciones por reglas)

Se implementa *Perspective-Informed Heterogeneous Graph Attention Network for Triads*. Un codificador con atención multi-cabeza consume atributos de fase y posición; un decodificador predice `none`, `mirrorOf` o `creates`. No usa el rótulo textual ni el índice de tríada.

Los 390 candidatos derivados de las 13 filas se evalúan con 13 particiones leave-one-triad-out. Se ejecutan tres variantes: atributos completos, ablación sin fase y ablación sin posición.

Las métricas miden la **recuperación de relaciones estructurales generadas por reglas**: F1 de `mirrorOf` y `creates` respecto al gold determinista; no se interpretan como validación empírica del marco sobre datos independientes del generador.

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

La puntuación perfecta del modelo completo y del oracle SHACL confirma la **recuperación de relaciones estructurales generadas por reglas** (`io:mirrorOf` y `io:creates`) a partir de fase y posición bajo leave-one-triad-out. Estas cifras **no** constituyen por sí solas una validación empírica del marco sobre datos del mundo real; para interpretación humana independiente véase `datasets/independent_eval/`.

## Evaluación independiente

`datasets/independent_eval/` define pares fuera de las cuatro reglas, conceptos nuevos y casos ambiguos, con protocolo de anotación **ciega** por anotadores humanos independientes y publicación de desacuerdos y métricas de acuerdo.

## Reproducción y verificación

Sigue [`REPRODUCCION.md`](REPRODUCCION.md). La CI compila Lean, regenera los artefactos, ejecuta las pruebas (incluido el puente formal), valida OWL RL/SHACL, ejecuta PI-HGAT-T, compara baselines y genera la auditoría automática.
