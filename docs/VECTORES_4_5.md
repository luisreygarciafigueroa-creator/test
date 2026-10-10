# Las cinco perspectivas del marco I.O.

El marco I.O. se articula mediante **cinco perspectivas complementarias**:

| # | Id | Perspectiva | Rol |
|---|-----|-------------|-----|
| 1 | `Ind` | **Individualidad** | Posicional (izquierda): unidad / singularidad |
| 2 | `D` | **Dualidad** | Posicional (centro): relación / diferencia |
| 3 | `Tot` | **Totalidad** | Posicional (derecha): integración / sistema |
| 4 | `Evol` | **Evolución** | Vectorial: flujo del vacío hacia la estructura |
| 5 | `Invol` | **Involución** | Vectorial: flujo de la estructura hacia el vacío |

Las tres primeras (Individualidad, Dualidad, Totalidad) describen los *modos de actualización* y se representan como metadatos de posición en cada tríada (izquierda, centro, derecha). Las perspectivas cuarta y quinta (Evolución e Involución) describen las *direcciones de flujo informativo* y se materializan como secuencias vectoriales de cinco pasos.

Fuente estructurada: [`data/iom_spec.json`](../data/iom_spec.json) (`five_perspectives`, `vectors`).

## Cuarta perspectiva — Evolución

| Fase | Etiquetas de izquierda a derecha | Posiciones del eje | Flecha |
|---|---|---|---|
| Avance | `vacío · ind · dua · tot · evol` | `0 · 1 · 2 · 3 · 4` | → |
| Retroceso | `evol · tot · dua · ind · vacío` | `4 · 3 · 2 · 1 · 0` | ← |

## Quinta perspectiva — Involución

| Fase | Etiquetas de izquierda a derecha | Posiciones del eje | Flecha |
|---|---|---|---|
| Avance | `invol · tot · dua · ind · vacío` | `4 · 3 · 2 · 1 · 0` | → |
| Retroceso | `vacío · ind · dua · tot · invol` | `0 · 1 · 2 · 3 · 4` | ← |

## Representación formal

Cada fila se materializa como cinco instancias `io:VectorStep`. Cada instancia conserva el vector (`Evol` / `Invol`), fase, posición del eje, índice visual, etiqueta y flecha. En conjunto son **20 pasos vectoriales**. Las dos filas de retroceso son reflejos de los recorridos de sus respectivas perspectivas.

En la ontología, las cinco perspectivas son individuos de `io:Perspective` con etiquetas en español: Individualidad, Dualidad, Totalidad, Evolución e Involución.
