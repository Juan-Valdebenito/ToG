# Investigación, selección e implementación del algoritmo de flujo máximo

Sección del informe correspondiente al apartado 2 del enunciado (y la parte de implementación del apartado 3).
Código: [`simulador/flujo.py`](../simulador/flujo.py). Pruebas: [`tests/test_flujo.py`](../tests/test_flujo.py). Comparación empírica: [`scripts/comparar_algoritmos.py`](../scripts/comparar_algoritmos.py).

## 1. Idea común: caminos aumentantes sobre la red residual

Dado un flujo factible x en G = (V, E) con capacidades c, la **red residual** G_x tiene, para cada arco (u, v) ∈ E:

- un **arco directo** u → v con capacidad residual c_x(u, v) = c(u, v) − x(u, v): lo que todavía cabe por la ruta;
- un **arco inverso** v → u con capacidad residual c_x(v, u) = x(u, v): el flujo ya enviado que se puede "devolver" (redirigir por otro camino).

Un **camino aumentante** es un camino dirigido de s a t en G_x con todos sus arcos de capacidad residual positiva. Su **cuello de botella** es δ = mín c_x(u, v) sobre sus arcos. Enviar δ por el camino (sumar δ en los arcos directos, restar δ en los originales recorridos al revés) produce un flujo factible de valor |x| + δ.

Ford y Fulkerson (1956) demostraron que **un flujo es máximo si y solo si no existe camino aumentante**, y que en ese momento el conjunto S de vértices alcanzables desde s en G_x define un corte de capacidad igual a |x| (teorema de flujo máximo–corte mínimo; también Elias, Feinstein y Shannon, 1956). Ambos algoritmos estudiados se basan en esta idea; solo difieren en **cómo eligen el camino aumentante**.

## 2. Alternativas investigadas

### 2.1 Método de Ford–Fulkerson con búsqueda en profundidad (DFS)

```
x ← 0
mientras exista un camino aumentante P de s a t en G_x (encontrado con DFS):
    δ ← mín { c_x(u, v) : (u, v) ∈ P }
    aumentar x en δ a lo largo de P
devolver x
```

- **Elección del camino:** el primero que encuentra la DFS, que puede ser largo y con un cuello de botella pequeño.
- **Terminación:** con capacidades enteras cada aumento suma al menos 1, así que hay a lo más |x*| iteraciones (|x*| = valor máximo). Con capacidades irracionales el método puede no terminar e incluso converger a un valor que no es el máximo (Ford y Fulkerson, 1962; Zwick, 1995 da las redes más pequeñas donde ocurre).
- **Complejidad:** O(|E| · |x*|). Depende del **valor** del flujo, no solo del tamaño de la red: en el ejemplo clásico con dos caminos de capacidad 10⁶ unidos por un arco de capacidad 1, una mala elección de caminos alterna por ese arco y necesita 2·10⁶ iteraciones en lugar de 2 (Cormen et al., 2022, cap. 24; Kleinberg y Tardos, 2006, cap. 7).

### 2.2 Algoritmo de Edmonds–Karp (búsqueda en anchura, BFS)

Es el mismo método de Ford–Fulkerson, pero el camino aumentante se elige con **BFS**, es decir, siempre uno con el **menor número de arcos** en G_x (Edmonds y Karp, 1972).

- **Propiedad clave:** la distancia (en arcos) de s a cada vértice en la red residual nunca disminuye de una iteración a la siguiente. Cada vez que un arco es cuello de botella (arco crítico) desaparece de G_x, y para volver a ser crítico la distancia a su origen debe crecer en al menos 2. Por eso cada arco es crítico a lo más |V|/2 veces.
- **Número de iteraciones:** O(|V| · |E|), **independiente de las capacidades**.
- **Complejidad:** cada BFS cuesta O(|V| + |E|), total O(|V| · |E|²) (Edmonds y Karp, 1972; Cormen et al., 2022, cap. 24).
- **Terminación:** garantizada para cualquier capacidad real, no solo entera.

### 2.3 Otras alternativas (no seleccionadas)

| Algoritmo | Complejidad | Comentario |
|---|---|---|
| Dinic / Dinitz (1970) | O(\|V\|² · \|E\|) | Usa la red de niveles de BFS y bloquea flujos con varias DFS. Más rápido en redes grandes, pero más difícil de implementar y explicar. |
| Push–relabel (Goldberg y Tarjan, 1988) | O(\|V\|² · \|E\|), O(\|V\|³) con FIFO | No usa caminos aumentantes: trabaja con preflujos y alturas. Muy eficiente en la práctica, pero el corte y el flujo intermedio son menos intuitivos de mostrar. |

Ahuja, Magnanti y Orlin (1993) presentan un panorama completo de estas familias.

## 3. Comparación

| Característica | Ford–Fulkerson (DFS) | Edmonds–Karp (BFS) |
|---|---|---|
| Elección del camino aumentante | Cualquiera (el primero de la DFS) | El más corto en número de arcos |
| Iteraciones (cota) | O(\|x*\|) | O(\|V\| · \|E\|) |
| Complejidad total | O(\|E\| · \|x*\|) | O(\|V\| · \|E\|²) |
| Depende de las capacidades | Sí | No |
| Termina con capacidades irracionales | No necesariamente | Sí |
| Corte mínimo al terminar | Sí (alcanzables desde s en G_x) | Sí (igual) |
| Dificultad de implementación | Baja | Baja (cambia la pila por una cola) |
| Resultado (valor máximo) | El mismo | El mismo |

### 3.1 Comparación empírica

Se implementaron **ambas** variantes con el mismo código base (`caminos_aumentantes`, cambiando solo la búsqueda) y se midieron con `python scripts/comparar_algoritmos.py`.

**Redes del proyecto** (número de caminos aumentantes):

| Red | Flujo máximo | FF-DFS | EK-BFS |
|---|---|---|---|
| Figura 1 del enunciado | 14 | 3 | 3 |
| Red principal | 22 | 8 | **6** |
| Configuración 2 (sin D→H) | 15 | 5 | **4** |
| Configuración 3 (con E→T) | 25 | 11 | **8** |

**Redes aleatorias** (50 redes por tamaño, capacidades 1..100, sin lazos, repetidos ni recíprocos):

| \|V\| | \|E\| | FF-DFS: caminos prom. (máx.) | EK-BFS: caminos prom. (máx.) |
|---|---|---|---|
| 12 | 30 | 5,9 (15) | 3,9 (12) |
| 30 | 120 | 46,0 (120) | 9,2 (22) |
| 60 | 300 | 127,2 (300) | 11,6 (23) |

En todas las redes ambas variantes obtuvieron el mismo valor máximo (el script lo comprueba). La diferencia en iteraciones crece con el tamaño de la red y con las capacidades, como predice la teoría: DFS encuentra caminos largos que se saturan con poco flujo y obliga a corregir con arcos inversos. En la red principal, por ejemplo, DFS usa el camino O→A→E→**D**→H→T, que recorre el arco inverso E→D (devuelve flujo de D→E), mientras que Edmonds–Karp nunca necesita esa corrección en esta red.

## 4. Justificación de la elección: Edmonds–Karp

1. **Cota de iteraciones independiente de las capacidades.** Las modificaciones desde la interfaz pueden cambiar capacidades y agregar rutas; con Edmonds–Karp el costo depende solo de |V| y |E|. En la red principal (|V| = 10, |E| = 18) la cota es |V|·|E| = 180 aumentos, y en la práctica son 6.
2. **Terminación garantizada** en cualquier red, sin depender de que las capacidades sean enteras.
3. **Mismo resultado y mismo corte** que Ford–Fulkerson: el corte mínimo se obtiene igual, con los vértices alcanzables desde s en la red residual final.
4. **Simplicidad:** es Ford–Fulkerson cambiando la pila de la DFS por una cola, por lo que es fácil de implementar con código propio, de explicar en la presentación y de verificar a mano (los caminos son cortos y se listan en la interfaz).
5. **Menos iteraciones observadas** en todas las redes probadas (tabla 3.1).

Dinic y push–relabel tienen mejor complejidad, pero para redes de 10 a 12 centros no aportan una diferencia perceptible y son más difíciles de justificar paso a paso.

## 5. Implementación

Todo el algoritmo está en [`simulador/flujo.py`](../simulador/flujo.py) y solo usa estructuras básicas de Python (`dict`, `list` y `set`; la cola de la BFS es una lista con un índice de lectura). No se usa ninguna biblioteca de grafos ni de flujos.

### 5.1 Representación de la red residual

`residual[u][v]` es un diccionario de diccionarios con la capacidad residual de u hacia v. Al construirlo, cada arco original (u, v) aporta `residual[u][v] = c(u, v)` y su inverso `residual[v][u] = 0`. Como el modelo prohíbe arcos recíprocos, el inverso de un arco nunca coincide con otro arco original, y el flujo de cada arco se recupera directamente:

x(u, v) = c(u, v) − residual[u][v].

### 5.2 Funciones

| Función | Entrada | Resultado |
|---|---|---|
| `arcos_activos(grafo)` | Red en formato JSON | Lista de (u, v, cap) de las rutas activas |
| `construir_residual(vertices, arcos)` | Vértices y arcos | Red residual inicial (directos = c, inversos = 0) |
| `bfs_camino_aumentante(residual, s, t)` | Residual, s, t | Árbol BFS `padre` del camino más corto s→t, o `None` |
| `dfs_camino_aumentante(residual, s, t)` | Residual, s, t | Árbol DFS `padre` de algún camino s→t, o `None` (solo para comparar) |
| `reconstruir_camino(padre, t)` | Árbol de búsqueda y t | Lista [s, …, t] |
| `caminos_aumentantes(vertices, arcos, s, t, buscar)` | Red y función de búsqueda | (valor, residual final, lista de (camino, δ)) |
| `edmonds_karp(vertices, arcos, s, t)` | Red, s, t | `caminos_aumentantes` con BFS |
| `ford_fulkerson_dfs(vertices, arcos, s, t)` | Red, s, t | `caminos_aumentantes` con DFS |
| `flujo_por_arco(arcos, residual)` | Arcos originales y residual final | {(u, v): x(u, v)} |
| `corte_minimo(vertices, arcos, residual, s)` | Red, residual final, s | (S, T, arcos de S hacia T) |
| `max_flow(grafo, s, t)` | Red JSON, s, t | (valor, flujo por arco, S, T, arcos del corte) — firma acordada por el grupo |
| `verificar(grafo, s, t, valor, x, corte)` | Red y resultados | Comprobaciones de capacidad, conservación y \|x\| = c(S, T) |

### 5.3 Núcleo del algoritmo

```python
def caminos_aumentantes(vertices, arcos, s, t, buscar_camino):
    residual = construir_residual(vertices, arcos)
    valor, iteraciones = 0, []
    while True:
        padre = buscar_camino(residual, s, t)        # BFS en Edmonds–Karp
        if padre is None:                            # no hay camino aumentante: x es máximo
            break
        camino = reconstruir_camino(padre, t)
        cuello = min(residual[u][v] for u, v in zip(camino, camino[1:]))
        for u, v in zip(camino, camino[1:]):
            residual[u][v] -= cuello                 # se consume capacidad
            residual[v][u] += cuello                 # se habilita devolver flujo
        valor += cuello
        iteraciones.append((camino, cuello))
    return valor, residual, iteraciones
```

La BFS (`bfs_camino_aumentante`) recorre la red residual con una cola, solo por arcos con capacidad residual positiva, y se detiene en cuanto alcanza t. El diccionario `padre` permite reconstruir el camino desde t hacia s.

### 5.4 Traza sobre la red de la Figura 1

| Iteración | Camino (BFS) | δ | \|x\| acumulado |
|---|---|---|---|
| 1 | O → A → C → T | mín(8, 5, 5) = 5 | 5 |
| 2 | O → A → D → T | mín(3, 3, 9) = 3 | 8 |
| 3 | O → B → D → T | mín(6, 6, 6) = 6 | 14 |

Después de la iteración 3, `residual[O] = {A: 0, B: 0}`: desde O no se alcanza ningún vértice, por lo que no hay más caminos aumentantes. El flujo máximo es 14, igual que la distribución del enunciado.

### 5.5 Corte mínimo

Al terminar, `corte_minimo` hace una BFS desde s en la red residual final: S son los vértices alcanzables y T = V \ S. Como no hay camino aumentante, t ∈ T. Además:

- todo arco original de S hacia T está **saturado** (si no, su extremo final sería alcanzable);
- todo arco original de T hacia S tiene **flujo 0** (si no, su arco inverso haría alcanzable su origen).

Por eso |x| = Σ x(S→T) − Σ x(T→S) = c(S, T), y como todo flujo factible cumple |x| ≤ c(S, T) para cualquier corte, el flujo es máximo y el corte es mínimo.

- Figura 1: S = {O}, T = {A, B, C, D, T}, corte O→A (8) + O→B (6) = 14.
- Red principal: S = {O, A, B, C, D, E, F}, T = {G, H, T}, corte C→G (4) + D→H (7) + E→H (5) + F→G (6) = 22.

### 5.6 Comprobaciones automáticas

`verificar` revisa, para cualquier red y resultado:

1. **Capacidad:** 0 ≤ x(u, v) ≤ c(u, v) en cada arco activo.
2. **Conservación:** en cada v ∉ {s, t}, lo que entra es igual a lo que sale.
3. **Valor:** el valor devuelto es igual al flujo neto que sale de s, que es igual a c(S, T).

La interfaz muestra el resultado de estas tres comprobaciones después de cada cálculo, y las pruebas (`python -m unittest discover tests`) las ejecutan sobre la Figura 1 (14), la red principal (22) y las configuraciones 2 (15) y 3 (25). Además comprueban que DFS y BFS dan el mismo valor.

## Referencias

- Ahuja, R. K., Magnanti, T. L. y Orlin, J. B. (1993). *Network Flows: Theory, Algorithms, and Applications*. Prentice Hall.
- Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022). *Introduction to Algorithms* (4.ª ed.), cap. 24 "Maximum Flow". MIT Press.
- Dinic, E. A. (1970). Algorithm for solution of a problem of maximum flow in networks with power estimation. *Soviet Mathematics Doklady*, 11, 1277–1280.
- Edmonds, J. y Karp, R. M. (1972). Theoretical improvements in algorithmic efficiency for network flow problems. *Journal of the ACM*, 19(2), 248–264.
- Elias, P., Feinstein, A. y Shannon, C. E. (1956). A note on the maximum flow through a network. *IRE Transactions on Information Theory*, 2(4), 117–119.
- Ford, L. R. y Fulkerson, D. R. (1956). Maximal flow through a network. *Canadian Journal of Mathematics*, 8, 399–404.
- Ford, L. R. y Fulkerson, D. R. (1962). *Flows in Networks*. Princeton University Press.
- Goldberg, A. V. y Tarjan, R. E. (1988). A new approach to the maximum-flow problem. *Journal of the ACM*, 35(4), 921–940.
- Kleinberg, J. y Tardos, É. (2006). *Algorithm Design*, cap. 7 "Network Flow". Pearson / Addison-Wesley.
- Zwick, U. (1995). The smallest networks on which the Ford–Fulkerson maximum flow procedure may fail to terminate. *Theoretical Computer Science*, 148(1), 165–170.
