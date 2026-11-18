# Tarea 2 — Formulación matemática del modelo

Responsable: **Juan Pablo**. Datos: [`datos/red_principal.json`](../datos/red_principal.json).

## 2.1 Grafo dirigido $G = (V, E)$ y función de capacidad $c$

La red de distribución se modela como un **grafo dirigido con capacidades** (red de flujo)

$$N = (G, c, s, t), \qquad G = (V, E)$$

### Conjunto de vértices $V$

$$V = \lbrace O, A, B, C, D, E, F, G, H, T \rbrace, \qquad |V| = 10$$

Cada vértice $v \in V$ representa un **centro logístico**:

- $s = O$: **origen**, centro donde se generan los paquetes.
- $t = T$: **destino**, centro al que deben llegar los paquetes.
- $V \setminus \lbrace s, t \rbrace = \lbrace A, B, C, D, E, F, G, H \rbrace$: **centros intermedios**, por donde los paquetes solo pasan (no se producen ni se almacenan).

### Conjunto de arcos $E$

$E \subseteq V \times V$ es un conjunto de **pares ordenados**. El arco $(u, v) \in E$ representa una **ruta de transporte** que solo puede recorrerse en el sentido $u \to v$.

$$
\begin{aligned}
E = \lbrace\ & (O,A), (O,B), (O,C), (B,A), (A,D), (A,E), (B,D), (B,F), (C,F), \
& (C,G), (D,E), (D,H), (E,H), (F,E), (F,G), (G,H), (G,T), (H,T)\ \rbrace
\end{aligned}
$$

$$|E| = 18$$

### Función de capacidad $c$

$$c : E \longrightarrow \lbrace 1, 2, \dots, 12 \rbrace$$

$c(u, v)$ es la **cantidad máxima de paquetes por hora** que puede trasladarse por la ruta $(u, v)$.

| Arco $(u,v)$ | $c(u,v)$ | Arco $(u,v)$ | $c(u,v)$ | Arco $(u,v)$ | $c(u,v)$ |
|---|---|---|---|---|---|
| $(O,A)$ | 10 | $(A,E)$ | 4 | $(D,H)$ | 7 |
| $(O,B)$ | 8 | $(B,D)$ | 5 | $(E,H)$ | 5 |
| $(O,C)$ | 7 | $(B,F)$ | 6 | $(F,E)$ | 3 |
| $(B,A)$ | 3 | $(C,F)$ | 5 | $(F,G)$ | 6 |
| $(A,D)$ | 6 | $(C,G)$ | 4 | $(G,H)$ | 4 |
| | | $(D,E)$ | 3 | $(G,T)$ | 12 |
| | | | | $(H,T)$ | 12 |

### Propiedades estructurales exigidas

Para todo $u, v \in V$:

| Propiedad | Expresión |
|---|---|
| Sin lazos | $(v, v) \notin E$ |
| Sin arcos repetidos | $E$ es un conjunto, cada par $(u,v)$ aparece una sola vez |
| Sin arcos recíprocos | $(u, v) \in E \Rightarrow (v, u) \notin E$ |
| Sin vértices aislados | $\forall v \in V,\ \exists\, (u, w) \in E$ con $v = u$ o $v = w$ |
| Tamaño inicial | $10 \le \lvert V \rvert \le 12$, $\quad 15 \le \lvert E \rvert \le 20$ |
| Origen y destino | $s \ne t$ y existen al menos 2 caminos dirigidos distintos de $s$ a $t$ |

### Sucesores y predecesores

Notación: $\delta^+(v) = \lbrace (v,w) \in E \rbrace$ (arcos que **salen** de $v$) y $\delta^-(v) = \lbrace (u,v) \in E \rbrace$ (arcos que **entran** a $v$).

| $v$ | Sucesores | Predecesores | $\sum_{\delta^+(v)} c$ | $\sum_{\delta^-(v)} c$ |
|---|---|---|---|---|
| O | A, B, C | — | 25 | 0 |
| A | D, E | O, B | 10 | 13 |
| B | A, D, F | O | 14 | 8 |
| C | F, G | O | 9 | 7 |
| D | E, H | A, B | 10 | 11 |
| E | H | A, D, F | 5 | 10 |
| F | E, G | B, C | 9 | 11 |
| G | H, T | C, F | 16 | 10 |
| H | T | D, E, G | 12 | 16 |
| T | — | G, H | 0 | 24 |

Observaciones:

- De $O$ salen como máximo 25 paquetes/hora y a $T$ llegan como máximo 24, pero el flujo real depende de las capacidades intermedias (por ejemplo, $E$ puede recibir 10 pero solo despachar 5).
- La suma de los grados de salida es $3+2+3+2+2+1+2+2+1 = 18 = |E|$.

## 2.2 Restricciones del flujo y problema de flujo máximo

### 2.2a Función de flujo y restricción de capacidad

#### 2.2a.1 Función de flujo $x$

Un **flujo** en la red $N = (G, c, s, t)$ es una función que asigna a cada arco una cantidad de paquetes:

$$x : E \longrightarrow \mathbb{Z}_{\ge 0}, \qquad (u, v) \longmapsto x(u, v)$$

**Significado:** $x(u, v)$ es la cantidad de paquetes por hora que **efectivamente** se envía por la ruta $u \to v$.

Diferencia entre $c$ y $x$:

| Símbolo | Qué representa | ¿Cambia? |
|---|---|---|
| $c(u, v)$ | Capacidad **máxima** de la ruta (dato del problema) | Fija para cada configuración de la red |
| $x(u, v)$ | Paquetes que **realmente** circulan por la ruta (variable de decisión) | La elige el algoritmo |

Observaciones:

- El flujo se define solo sobre los arcos de $E$. Como no hay arcos recíprocos, por cada par de centros hay **a lo sumo un sentido** en que pueden circular paquetes.
- Se toman valores **enteros** porque los paquetes son indivisibles. Como todas las capacidades son enteras, existe un flujo máximo entero (teorema de integralidad, Ford y Fulkerson, 1956), y los algoritmos de caminos aumentantes lo encuentran.
- El **flujo nulo** $x(u,v) = 0$ para todo $(u,v) \in E$ siempre es un flujo válido de valor 0. Es el punto de partida de Ford–Fulkerson y Edmonds–Karp.
- Las rutas desactivadas (`"activo": false`) no pertenecen a $E$ en esa configuración, por lo que no tienen flujo.

**Ejemplo en la red principal.** Si se envían 5 paquetes/hora por el camino $O \to A \to D \to H \to T$ y nada más:

$$
x(u,v) =
\begin{cases}
5 & \text{si } (u,v) \in \lbrace (O,A), (A,D), (D,H), (H,T) \rbrace \
0 & \text{en los otros 14 arcos}
\end{cases}
$$

| Arco | $x(u,v)$ | $c(u,v)$ |
|---|---|---|
| $(O,A)$ | 5 | 10 |
| $(A,D)$ | 5 | 6 |
| $(D,H)$ | 5 | 7 |
| $(H,T)$ | 5 | 12 |
| resto | 0 | — |

Este flujo transporta 5 paquetes/hora de $O$ a $T$. En 2.2a.2 se formaliza por qué es válido respecto de las capacidades, y en 2.2b y 2.2c se revisan la conservación y el valor del flujo.

#### 2.2a.2 Restricción de capacidad

Ninguna ruta puede transportar más paquetes de los que admite ni una cantidad negativa:

$$0 \le x(u, v) \le c(u, v), \qquad \forall\, (u, v) \in E$$

**Significado:**

- $x(u,v) \ge 0$: los paquetes solo viajan en el sentido de la ruta ($u \to v$). Un valor negativo significaría transportar en sentido contrario, lo que no está permitido.
- $x(u,v) \le c(u,v)$: no se supera la cantidad máxima de paquetes por hora de la ruta.

Son $|E| = 18$ pares de desigualdades, una por cada ruta de la red principal.

**Holgura y arcos saturados.** Para un flujo $x$ que cumple la restricción se define la **holgura** de cada arco:

$$h(u, v) = c(u, v) - x(u, v) \ \ge 0$$

| Caso | Condición | Interpretación |
|---|---|---|
| Arco sin uso | $x(u,v) = 0$ | La ruta no se utiliza |
| Arco con holgura | $0 < x(u,v) < c(u,v)$ | La ruta podría llevar $h(u,v)$ paquetes más |
| Arco **saturado** | $x(u,v) = c(u,v)$, es decir $h(u,v) = 0$ | La ruta está al máximo: es un posible **cuello de botella** |

**Ejemplo (continuación de 2.2a.1).** Con 5 paquetes/hora por $O \to A \to D \to H \to T$:

| Arco | $x$ | $c$ | ¿$0 \le x \le c$? | Holgura $h$ |
|---|---|---|---|---|
| $(O,A)$ | 5 | 10 | ✔ | 5 |
| $(A,D)$ | 5 | 6 | ✔ | **1** |
| $(D,H)$ | 5 | 7 | ✔ | 2 |
| $(H,T)$ | 5 | 12 | ✔ | 7 |
| otros 14 arcos | 0 | — | ✔ | $c(u,v)$ |

El flujo cumple la restricción de capacidad en los 18 arcos. Por ese mismo camino solo se podría agregar
$\min\lbrace 5, 1, 2, 7 \rbrace = 1$ paquete/hora más, porque $(A,D)$ quedaría saturado. Esta idea (el mínimo de las holguras a lo largo de un camino) es la **capacidad residual** que usan Ford–Fulkerson y Edmonds–Karp para aumentar el flujo.

**Contraejemplo.** Enviar 7 paquetes/hora por el mismo camino no es válido: $x(A,D) = 7 > c(A,D) = 6$.

### 2.2b Conservación del flujo en los centros intermedios

#### 2.2b.1 Formulación de la restricción de conservación

En cada centro intermedio, **todo lo que entra debe salir**:

$$\sum_{(u,v) \in E} x(u, v) \;=\; \sum_{(v,w) \in E} x(v, w), \qquad \forall\, v \in V \setminus \lbrace s, t \rbrace$$

- El lado izquierdo suma el flujo de los arcos que **entran** a $v$, es decir, los de $\delta^-(v)$.
- El lado derecho suma el flujo de los arcos que **salen** de $v$, es decir, los de $\delta^+(v)$.

Con la notación de 2.1 se escribe de forma compacta:

$$x^{\text{ent}}(v) = \sum_{e \in \delta^-(v)} x(e), \qquad x^{\text{sal}}(v) = \sum_{e \in \delta^+(v)} x(e), \qquad x^{\text{ent}}(v) = x^{\text{sal}}(v)$$

Equivalentemente, el **flujo neto** (exceso) de cada centro intermedio es cero:

$$\operatorname{exc}(v) = x^{\text{ent}}(v) - x^{\text{sal}}(v) = 0, \qquad \forall\, v \in V \setminus \lbrace s, t \rbrace$$

**Significado en la red de distribución:**

- Los centros intermedios **no producen** paquetes: no puede salir más de lo que llega.
- Los centros intermedios **no almacenan ni pierden** paquetes: no puede llegar más de lo que sale. El modelo describe un régimen estable, hora a hora, sin acumulación en bodega.
- Un paquete que llega a un centro intermedio sigue hacia otro centro por alguna de sus rutas de salida.

**¿Por qué se excluyen $s$ y $t$?**

| Vértice | Comportamiento | Exceso |
|---|---|---|
| $s = O$ | **Genera** los paquetes: sale más de lo que entra | $\operatorname{exc}(O) = -\lvert x \rvert \le 0$ |
| $t = T$ | **Recibe** los paquetes: entra más de lo que sale | $\operatorname{exc}(T) = \lvert x \rvert \ge 0$ |
| $v \in V \setminus \lbrace s,t \rbrace$ | Solo deja pasar los paquetes | $\operatorname{exc}(v) = 0$ |

En la red principal, $V \setminus \lbrace s,t \rbrace = \lbrace A, B, C, D, E, F, G, H \rbrace$, así que hay **8 ecuaciones de conservación**.

**Ejemplo (continuación de 2.2a).** Con 5 paquetes/hora por $O \to A \to D \to H \to T$:

| Centro | Entra | Sale | ¿Se conserva? |
|---|---|---|---|
| A | $x(O,A) = 5$ | $x(A,D) = 5$ | ✔ $5 = 5$ |
| D | $x(A,D) = 5$ | $x(D,H) = 5$ | ✔ $5 = 5$ |
| H | $x(D,H) = 5$ | $x(H,T) = 5$ | ✔ $5 = 5$ |
| B, C, E, F, G | 0 | 0 | ✔ $0 = 0$ |

Un flujo que cumple la restricción de capacidad (2.2a.2) y la de conservación (2.2b) se llama **flujo factible**.

#### 2.2b.2 Verificación de la conservación con un flujo de varios caminos

Se considera un flujo en la red principal formado por **tres caminos** que se combinan:

| Camino | Paquetes/hora |
|---|---|
| $P_1:\ O \to A \to D \to H \to T$ | 5 |
| $P_2:\ O \to B \to F \to G \to T$ | 6 |
| $P_3:\ O \to C \to G \to T$ | 4 |

El flujo de cada arco es la suma de lo que envían los caminos que lo usan. Los caminos $P_2$ y $P_3$ **se juntan en $G$**, así que $x(G,T) = 6 + 4 = 10$.

| Arco | $x$ | $c$ | Arco | $x$ | $c$ |
|---|---|---|---|---|---|
| $(O,A)$ | 5 | 10 | $(C,G)$ | 4 | 4 |
| $(O,B)$ | 6 | 8 | $(D,H)$ | 5 | 7 |
| $(O,C)$ | 4 | 7 | $(F,G)$ | 6 | 6 |
| $(A,D)$ | 5 | 6 | $(G,T)$ | 10 | 12 |
| $(B,F)$ | 6 | 6 | $(H,T)$ | 5 | 12 |

Los otros 8 arcos tienen $x = 0$. Se cumple $0 \le x \le c$ en todos los arcos. Los arcos $(B,F)$, $(C,G)$ y $(F,G)$ quedan **saturados**.

**Comprobación de las 8 ecuaciones de conservación:**

| Centro | Entra $x^{\text{ent}}(v)$ | Sale $x^{\text{sal}}(v)$ | ¿Se conserva? |
|---|---|---|---|
| A | $x(O,A) + x(B,A) = 5 + 0 = 5$ | $x(A,D) + x(A,E) = 5 + 0 = 5$ | ✔ |
| B | $x(O,B) = 6$ | $x(B,A) + x(B,D) + x(B,F) = 0 + 0 + 6 = 6$ | ✔ |
| C | $x(O,C) = 4$ | $x(C,F) + x(C,G) = 0 + 4 = 4$ | ✔ |
| D | $x(A,D) + x(B,D) = 5 + 0 = 5$ | $x(D,E) + x(D,H) = 0 + 5 = 5$ | ✔ |
| E | $x(A,E) + x(D,E) + x(F,E) = 0$ | $x(E,H) = 0$ | ✔ |
| F | $x(B,F) + x(C,F) = 6 + 0 = 6$ | $x(F,E) + x(F,G) = 0 + 6 = 6$ | ✔ |
| G | $x(C,G) + x(F,G) = 4 + 6 = 10$ | $x(G,H) + x(G,T) = 0 + 10 = 10$ | ✔ |
| H | $x(D,H) + x(E,H) + x(G,H) = 5 + 0 + 0 = 5$ | $x(H,T) = 5$ | ✔ |

El flujo respeta la capacidad y la conservación, así que es **factible**. Sale de $O$: $5 + 6 + 4 = 15$ y llega a $T$: $10 + 5 = 15$ paquetes/hora. No es el máximo (en 1.4 se indicó que el máximo es 22), pero es un flujo válido.

**Contraejemplo: un flujo que no conserva.** Si en el flujo anterior se cambia solo $x(G,T) = 8$:

$$x^{\text{ent}}(G) = 4 + 6 = 10 \ne 8 = x^{\text{sal}}(G), \qquad \operatorname{exc}(G) = 2$$

Todas las capacidades se siguen respetando, pero el centro $G$ **acumularía 2 paquetes por hora** que nunca salen. Por eso no es un flujo factible. Además, a $T$ llegarían $8 + 5 = 13$ paquetes, aunque de $O$ salen 15. Cuando falla la conservación, lo que sale del origen ya no coincide con lo que llega al destino.

> Esta misma comprobación (capacidad y conservación en cada centro) la debe hacer automáticamente el código de la Persona 2 para la red principal y sus dos modificaciones.

### 2.2c Valor del flujo $|x|$

#### 2.2c.1 Definición del valor del flujo

El **valor** de un flujo $x$ es la cantidad **neta** de paquetes por hora que sale del origen:

$$|x| \;=\; \sum_{(s,v) \in E} x(s, v) \;-\; \sum_{(u,s) \in E} x(u, s)$$

- El primer término suma lo que **sale** de $s$ por sus rutas: $x^{\text{sal}}(s)$.
- El segundo término resta lo que **vuelve a entrar** a $s$: $x^{\text{ent}}(s)$.

Con la notación de 2.2b: $\ |x| = x^{\text{sal}}(s) - x^{\text{ent}}(s) = -\operatorname{exc}(s)$.

**Significado:** $|x|$ es el **rendimiento de la red**, es decir, cuántos paquetes por hora se despachan efectivamente desde el origen hacia el resto de la red. Es la cantidad que la empresa quiere **maximizar**.

**¿Por qué se resta lo que entra a $s$?** En general, una red puede tener rutas que regresan al origen. Un paquete que sale de $s$ y vuelve a $s$ no se transportó a ningún lugar, así que no debe contarse. Por eso se usa la cantidad **neta**.

**Aplicación a la red principal.** En la red principal $s = O$, con

$$\delta^+(O) = \lbrace (O,A), (O,B), (O,C) \rbrace, \qquad \delta^-(O) = \varnothing$$

Ninguna ruta llega a $O$, así que el segundo término vale 0 y el valor se reduce a

$$|x| = x(O,A) + x(O,B) + x(O,C)$$

Esto no vale siempre: si alguna modificación agrega una ruta que llega a $O$ (por ejemplo $D \to O$), habrá que restar su flujo.

**Valores de los ejemplos anteriores:**

| Flujo | $x(O,A)$ | $x(O,B)$ | $x(O,C)$ | $\lvert x \rvert$ |
|---|---|---|---|---|
| Flujo nulo | 0 | 0 | 0 | 0 |
| Un camino (2.2a) | 5 | 0 | 0 | 5 |
| Tres caminos (2.2b.2) | 5 | 6 | 4 | 15 |

Todos son flujos factibles con distinto valor. El problema de flujo máximo (2.2d) consiste en encontrar, entre todos los flujos factibles, uno de **valor máximo**.
