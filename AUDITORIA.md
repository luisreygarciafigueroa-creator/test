# Auditoría de correspondencia con la especificación IOM

**Fuentes:** [`docs/MARCOI.O.txt`](docs/MARCOI.O.txt) y la especificación operativa normalizada en [`data/iom_spec.json`](data/iom_spec.json). La especificación JSON alimenta generador, ontología, CSV, pruebas y experimentos.

## Correspondencia y comprobación

| Especificación | Representación | Verificación |
|---|---|---|
| Estado temporal y vacío | `State(time, payload)`; `vacuum` | Lean 4.9.0 |
| Cuatro operadores temporales | `E`, `S_fwd`, `Ivo`, `S_rev` | Teoremas Lean compilados |
| Posiciones de tríada | izquierda=0/`Ind`; centro=1/`D`; derecha=2/`Tot` | RDF/OWL, SHACL, pruebas y `TriadPosition` Lean |
| Avance/retroceso actualizados | 13 filas por fase; 78 nodos | CSV, RDF, SHACL, pruebas literales |
| Extremos actualizados | avance comienza `involución | vacío | evolución`; retroceso termina `evolución | vacío | involución` | Fuente JSON, RDF y pruebas |
| Espejos laterales | misma fila, fase opuesta, `pos_ret = 2 - pos_adv` | OWL `mirrorOf` simétrica, SHACL y Lean |
| Dinámicas `creates` | cuatro reglas, 8 aristas por fila = 104 | Generador, SHACL y comparación exacta |
| Perspectivas vectoriales 4–5 | cuatro secuencias de 5 pasos = 20 | RDF, SHACL semántico y pruebas |
| Axiomas de ontología | clases, dominios, rangos, simetría y funcionalidad | Aserciones OWL más expansión OWL RL |
| PI-HGAT-T | clasificación de relación estructural en 13 folds | JSON de métricas, logs, configuración y CI |

## Decisiones de transcripción

- Se usa la tabla de referencia canónica. La tríada `individualidad | dualidad | totalidad` que formaba la primera fila de una versión anterior deja de ser una etiqueta de las 13 filas categoriales; `Ind`, `D`, `Tot` permanecen como metadatos posicionales de perspectiva, distintos del rótulo categorial.
- Los rótulos se guardan en minúscula con ortografía canónica del español (incluidos acentos). La etiqueta `vacío` unifica las apariciones en extremos y en la fila Universo/Espacio.
- Los vectores de retroceso se actualizan a `evol · tot · dua · ind · vacío` y `vacío · ind · dua · tot · invol`. La orientación visible y el índice del eje son campos diferentes.
- El archivo de referencia `docs/MARCOI.O.txt` se conserva; las tablas operativas se documentan en `data/iom_spec.json` (`spec_version` 1.1.0).

## Métricas y verificación empírica

Las métricas de aristas de PI-HGAT-T están ligadas a `io:mirrorOf` y `io:creates` y a sus reglas SHACL. El criterio de referencia es la reconstrucción exacta (1.0) de la estructura ontológica determinista. El score observado del modelo se reporta junto con ablaciones, baselines y matrices de confusión por fold.

El dataset operativo comprende 13 tríadas y 78 nodos. Los experimentos miden, bajo leave-one-triad-out, la recuperabilidad empírica de las relaciones estructurales y la contribución de cada factor (fase, posición, estructura de grafo). Véase [`EXPERIMENTOS.md`](EXPERIMENTOS.md) para tablas completas, matrices de confusión y variabilidad por fold.

### Resumen numérico registrado

| Método | Accuracy | Macro-F1 | mirrorOf F1 | creates F1 |
|---|---:|---:|---:|---:|
| PI-HGAT-T (fase + posición) | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Ablación sin fase | 0.6000 | 0.6056 | 0.7500 | 0.6667 |
| Ablación sin posición | 0.6359 | 0.5771 | 0.3871 | 0.4870 |
| Reglas deterministas (oracle) | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| MLP sin grafo | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Regresión logística | 0.5333 | 0.2424 | 0.0000 | 0.0000 |

OWL RL expande inferencias de dominios/rangos; SHACL valida restricciones cerradas y reglas de estructura. Lean formaliza operadores, espejos y cotas de índice. Juntos, Lean + OWL/SHACL + PI-HGAT-T + baselines constituyen la cadena de verificación empírica y formal del marco.
