# Perspectivas cuarta y quinta: vectores I.O.

> **Procedencia:** transcripción de las dos tablas vectoriales proporcionadas por el usuario el 8 de octubre de 2026. Se conservan etiquetas, posiciones de eje y flechas; las etiquetas vectoriales abreviadas (`vacío`, `ind`, `dua`, `tot`, `evol`, `invol`) son literales.

Las tres primeras perspectivas (`Ind`, `D`, `Tot`) se representan como metadatos de posición (izquierda, centro, derecha). Las perspectivas cuarta y quinta describen las secuencias vectoriales; no agregan filas a las tríadas.

## Cuarta perspectiva — Vector Evolutivo

| Fase | Etiquetas de izquierda a derecha | Posiciones del eje | Flecha |
|---|---|---|---|
| Avance | `vacío · ind · dua · tot · evol` | `0 · 1 · 2 · 3 · 4` | → |
| Retroceso | `evol · tot · dua · ind · vacío` | `4 · 3 · 2 · 1 · 0` | ← |

## Quinta perspectiva — Vector Involutivo

| Fase | Etiquetas de izquierda a derecha | Posiciones del eje | Flecha |
|---|---|---|---|
| Avance | `invol · tot · dua · ind · vacío` | `4 · 3 · 2 · 1 · 0` | → |
| Retroceso | `vacío · ind · dua · tot · invol` | `0 · 1 · 2 · 3 · 4` | ← |

## Representación formal

Cada fila se materializa como cinco instancias `io:VectorStep`. Cada instancia conserva el vector, fase, posición del eje, índice visual de izquierda a derecha, etiqueta y flecha. En conjunto son **20 pasos vectoriales**. Las dos filas de retroceso son reflejos de los recorridos de sus respectivas perspectivas, pero sus etiquetas y flechas se transcriben como aparecen en las tablas recibidas.
