# Evaluación independiente (interpretación de relaciones)

Este conjunto **no** es una partición del generador de 390 candidatos. Incluye:

| kind | Descripción |
|---|---|
| `control_mirror` / `control_creates` | Controles canónicos bajo las reglas |
| `out_of_rules` | Pares que las cuatro reglas y el espejo **no** etiquetan como mirror/creates |
| `cross_triad` | Pares entre tríadas distintas (fuera del dominio local de las reglas) |
| `new_concept` | Etiquetas **ajenas** al vocabulario de las 13 tríadas |
| `ambiguous` | Frontera semántica (p. ej. doble `vacío`) |

## Archivos

- `independent_pairs.csv` — pares visibles al anotador (sin gold)
- `PROTOCOL.json` — instrucciones de cegado, etiquetas y métricas a publicar
- `rule_reference.json` — etiquetas de regla **ocultas** (solo análisis post-hoc)
- `annotations_template.json` — plantilla para 3+ anotadores humanos independientes

## Uso legítimo del lenguaje

Los resultados de este experimento, una vez anotados por humanos ciegos, pueden describirse como **evaluación de interpretabilidad / acuerdo inter-anotador** sobre el marco.

Las cifras de accuracy de PI-HGAT-T en `experiments/results/` deben describirse como **recuperación de relaciones estructurales generadas por reglas**, no como «validación empírica del marco» en el mundo real.
