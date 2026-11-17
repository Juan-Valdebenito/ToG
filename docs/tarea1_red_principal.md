# Tarea 1 — Diseño de la red principal y formato de datos

Responsable: **Juan Pablo**. Archivo de datos: [`datos/red_principal.json`](../datos/red_principal.json).

## 1.1 Centros logísticos (vértices)

V = {O, A, B, C, D, E, F, G, H, T},  |V| = 10

| Vértice | Significado |
|---|---|
| O | Centro de origen (bodega central): de aquí salen los paquetes |
| A, B, C | Centros intermedios de primer nivel (reciben directamente desde O) |
| D, E, F, G | Centros intermedios de segundo nivel |
| H | Centro intermedio de consolidación previo al destino |
| T | Centro de destino: aquí deben llegar los paquetes |

## 1.2 Rutas (arcos) y capacidades

Cada arco (u, v) es una ruta de transporte con sentido u → v.
c(u, v) es la capacidad máxima de la ruta, en paquetes por hora.

| # | Arco | c | # | Arco | c |
|---|---|---|---|---|---|
| 1 | O → A | 10 | 10 | C → G | 4 |
| 2 | O → B | 8 | 11 | D → E | 3 |
| 3 | O → C | 7 | 12 | D → H | 7 |
| 4 | B → A | 3 | 13 | E → H | 5 |
| 5 | A → D | 6 | 14 | F → E | 3 |
| 6 | A → E | 4 | 15 | F → G | 6 |
| 7 | B → D | 5 | 16 | G → H | 4 |
| 8 | B → F | 6 | 17 | G → T | 12 |
| 9 | C → F | 5 | 18 | H → T | 12 |

|E| = 18,  c : E → {1, …, 12}

## 1.3 Validación de las reglas del enunciado

Comprobado con `py -3 datos/validar_red.py datos/red_principal.json`:

| Regla | Resultado |
|---|---|
| 10 ≤ \|V\| ≤ 12 | ✔ \|V\| = 10 |
| 15 ≤ \|E\| ≤ 20 | ✔ \|E\| = 18 |
| Capacidades enteras entre 1 y 12 | ✔ mínimo 3, máximo 12 |
| Sin lazos | ✔ |
| Sin arcos repetidos | ✔ |
| Sin arcos recíprocos (u→v y v→u) | ✔ |
| Ningún vértice aislado | ✔ |

## 1.4 Origen y destino

s = O,  t = T.

Existen **16 caminos dirigidos simples distintos** de O a T (el enunciado pide al menos 2). Ejemplos:

- O → A → D → H → T
- O → B → F → G → T
- O → C → G → T

**Valor de referencia para pruebas** (calculado aparte, solo para que P2 y P3 comprueben su código):
flujo máximo = **22** paquetes/hora, con corte mínimo
S = {O, A, B, C, D, E, F}, T = {G, H, T} y arcos de corte
C→G (4) + D→H (7) + E→H (5) + F→G (6) = 22.
La red de ejemplo del enunciado ([`datos/red_ejemplo_enunciado.json`](../datos/red_ejemplo_enunciado.json)) debe dar 14.

## 1.5 Formato de datos acordado

Todas las redes (principal, modificaciones y caso manual) usan este JSON:

```json
{
  "nombre": "texto",
  "unidad_capacidad": "paquetes por hora",
  "origen": "O",
  "destino": "T",
  "vertices": [ {"id": "O", "nombre": "Centro de origen"} ],
  "arcos":    [ {"u": "O", "v": "A", "cap": 10, "activo": true} ]
}
```

- `id`: identificador corto del centro (una letra).
- `u`, `v`: el arco va de `u` hacia `v`.
- `cap`: entero entre 1 y 12.
- `activo`: `false` representa una ruta desactivada (se ignora en el cálculo, pero se conserva en el archivo).

Firma acordada para el algoritmo (P2):

```python
max_flow(grafo, s, t) -> (valor, flujo_por_arco, S, T, arcos_corte)
```
