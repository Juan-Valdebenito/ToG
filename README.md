# ToG — Simulador de una red de distribución de paquetes

Proyecto 2 de Teoría de Grafos (INFO1158). Entrega y presentación: **jueves 26 de noviembre de 2026** (informe PDF hasta las 23:00 en Educa).

Aplicación que modela una red de centros logísticos como un grafo dirigido con capacidades, calcula el **flujo máximo** con un algoritmo propio, identifica un **corte mínimo** y permite modificar la red desde la interfaz para comparar configuraciones.

## Estructura

```
datos/
  red_principal.json          Red principal (10 vértices, 18 arcos, s = O, t = T)
  red_ejemplo_enunciado.json  Red de la Figura 1 del enunciado (para pruebas, flujo máx. = 14)
  validar_red.py              Comprueba las reglas del enunciado sobre una red
docs/
  tarea1_red_principal.md     Diseño de la red, validación y formato de datos
  tarea2_formulacion.md       Formulación matemática del modelo
```

## Ejecución

Requiere Python 3 (en Windows, si `python` abre Python 2, usar `py -3`).

```bash
py -3 datos/validar_red.py datos/red_principal.json
```

## Reparto de tareas

### Juan Pablo — Modelación matemática, teoría y verificación

1. **Diseñar la red principal y el formato de datos** ✅
   1. Definir los centros logísticos (vértices) y su significado. ✅
   2. Definir las rutas (arcos) con sentido y capacidades entre 1 y 12. ✅
   3. Validar las reglas: 10–12 vértices, 15–20 arcos, sin lazos, sin arcos repetidos ni recíprocos y sin vértices aislados. ✅
   4. Elegir origen s y destino t, y verificar que existan al menos 2 caminos dirigidos distintos. ✅
   5. Definir el formato JSON común y entregar los archivos de datos al equipo. ✅
2. **Formulación matemática del modelo** — [docs/tarea2_formulacion.md](docs/tarea2_formulacion.md)
   1. Definir formalmente G = (V, E), la función de capacidad c, las propiedades exigidas y los sucesores/predecesores de cada centro. ✅
   2. Formular las restricciones del flujo (capacidad y conservación), el valor del flujo |x| y el problema de flujo máximo como optimización.
      - **2.2a** Función de flujo y restricción de capacidad
        - 2.2a.1 Definir la función de flujo x, su significado y su diferencia con c (con ejemplo). ✅
        - 2.2a.2 Formular la restricción de capacidad 0 ≤ x(u,v) ≤ c(u,v), arcos saturados y holgura. ✅
      - **2.2b** Conservación del flujo en los centros intermedios
        - 2.2b.1 Formular la restricción de conservación, su significado y por qué se excluyen s y t. ✅
        - 2.2b.2 Verificar la conservación con un flujo de varios caminos en la red principal (y un contraejemplo). ✅
      - **2.2c** Valor del flujo |x|
        - 2.2c.1 Definir |x| (flujo neto que sale de s), su significado y aplicarlo a la red principal. ✅
        - 2.2c.2 Demostrar que lo que sale de s es igual a lo que llega a t. ✅
        - 2.2c.3 Cotas superiores del valor: capacidad de salida de s, de entrada a t y de cualquier corte. ✅
      - **2.2d** Problema de flujo máximo como problema de optimización
        - 2.2d.1 Plantear el problema (PFM): objetivo, restricciones, flujo óptimo y existencia de solución. ✅
        - 2.2d.2 Resumen del modelo completo y tamaño del problema en la red principal (variables y restricciones).
   3. Aplicar el modelo a la red principal: escribir las ecuaciones de conservación de cada centro intermedio y explicar los supuestos e interpretación del modelo.
3. **Teorema de flujo máximo–corte mínimo**: investigarlo, definir c(S, T) y explicar por qué el corte obtenido del grafo residual es mínimo.
4. **Caso de verificación manual (4–6 vértices)**: resolverlo a mano con caminos aumentantes, encontrar un flujo y un corte de igual valor y compararlo con la salida del código (capturas).
5. **Verificación de las 3 configuraciones e informe final**: comprobar capacidades, conservación y flujo = corte en la red inicial y sus dos modificaciones; unir las secciones del informe en PDF con las referencias.

### Persona 2 — Investigación e implementación del algoritmo

1. Investigar y comparar Ford–Fulkerson (DFS) y Edmonds–Karp (BFS), con fuentes académicas, y justificar la elección.
2. Implementar con código propio el grafo residual, la búsqueda BFS de caminos aumentantes y Edmonds–Karp (valor máximo y flujo de cada arco original).
3. Implementar el corte mínimo: S = vértices alcanzables desde s en el residual, T = el resto, y los arcos de S hacia T.
4. Implementar las comprobaciones: capacidades, conservación del flujo y valor del flujo = capacidad del corte.
5. Documentar las funciones (entradas, salidas y propósito) y escribir la sección del informe sobre investigación e implementación.

### Persona 3 — Interfaz interactiva y simulación

1. Construir la interfaz que dibuje los centros, las rutas, sus direcciones y capacidades (sin usar funciones de flujo de bibliotecas).
2. Agregar los controles: elegir origen y destino, botón Calcular/Recalcular, mostrar el flujo máximo, flujo/capacidad por arco y la partición S | T resaltando los arcos del corte.
3. Permitir modificaciones desde la interfaz: desactivar una ruta, cambiar su capacidad y agregar una conexión, rechazando arcos inválidos.
4. Definir y analizar las 3 configuraciones (inicial + 2 modificaciones): flujo máximo, corte mínimo e interpretación de las diferencias.
5. Preparar el repositorio (README, `requirements.txt`, instrucciones), escribir la sección de resultados con capturas y liderar la demo.

## Calendario

| Fecha | Hito |
|---|---|
| 18 nov | Red principal y formato de datos definidos (Juan Pablo) ✅ |
| 21 nov | Algoritmo y corte mínimo funcionando (P2); interfaz básica dibujando la red (P3) |
| 23 nov | Integración completa y modificaciones funcionando |
| 24 nov | Resultados de las 3 configuraciones y verificación manual comparada con el código |
| 25 nov | Informe armado y ensayo de la presentación (12 min, unos 4 por persona) |
| 26 nov | Presentación y entrega del PDF antes de las 23:00 |
