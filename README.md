# ToG — Simulador de una red de distribución de paquetes

Proyecto 2 de Teoría de Grafos (INFO1158). Entrega y presentación: **jueves 26 de noviembre de 2026** (informe PDF hasta las 23:00 en Educa).

Aplicación que modela una red de centros logísticos como un grafo dirigido con capacidades, calcula el **flujo máximo** con un algoritmo propio, identifica un **corte mínimo** y permite modificar la red desde la interfaz para comparar configuraciones.

## Estructura

```
app.py                        Interfaz interactiva (Streamlit)
simulador/
  flujo.py                    Edmonds–Karp (y Ford–Fulkerson DFS para comparar), corte mínimo y comprobaciones
tests/
  test_flujo.py               Pruebas: ejemplo = 14, principal = 22, config. 2 = 15, config. 3 = 25
datos/
  red_principal.json          Red principal / configuración 1 (10 vértices, 18 arcos, s = O, t = T)
  config_2_sin_DH.json        Configuración 2: ruta D -> H desactivada
  config_3_nueva_ET.json      Configuración 3: nueva ruta E -> T (capacidad 6)
  caso_manual.json            Caso de verificación manual del apartado 5 (5 vértices, flujo máx. = 11)
  red_ejemplo_enunciado.json  Red de la Figura 1 del enunciado (para pruebas, flujo máx. = 14)
  validar_red.py              Comprueba las reglas del enunciado sobre una red
docs/
  tarea1_red_principal.md     Diseño de la red, validación y formato de datos
  tarea2_formulacion.md       Formulación matemática del modelo
  tarea_p2_algoritmo.md       Investigación, comparación, justificación e implementación del algoritmo
  caso_manual.md              Resolución manual del caso de verificación y contraste con el código
  tarea3_resultados.md        Interfaz, modificaciones y resultados de las 3 configuraciones
  capturas/                   Capturas de la aplicación para el informe
scripts/
  capturas.py                 Regenera las capturas (solo desarrollo, requiere playwright)
  comparar_algoritmos.py      Compara Ford–Fulkerson (DFS) y Edmonds–Karp (BFS) en iteraciones
```

## Instalación y ejecución

Requiere **Python 3.11 o superior** (Streamlit 1.67 no se instala en versiones anteriores). En Windows, si `python` abre otra versión, usar `py -3.11` o superior. Comprobar con `python --version`.

```bash
# 1. Clonar el repositorio y entrar a la carpeta
git clone <url-del-repositorio> && cd ToG

# 2. (Opcional) crear un entorno virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instalar dependencias (solo Streamlit, para la interfaz)
pip install -r requirements.txt

# 4. Abrir la interfaz (se abre en http://localhost:8501)
streamlit run app.py
```

Otros comandos:

```bash
python -m unittest discover tests                  # pruebas del algoritmo
python datos/validar_red.py datos/red_principal.json   # reglas del enunciado sobre una red
```

### Uso de la interfaz

1. En la barra lateral, elegir la red, el **origen s** y el **destino t**, y pulsar **Calcular flujo máximo**.
2. El grafo muestra el flujo/capacidad de cada ruta, S en azul, T en naranja y los arcos del corte mínimo en rojo. Debajo aparecen el corte, la tabla de flujo por arco y el detalle de los caminos aumentantes y las comprobaciones.
3. En **Modificar la red** se puede desactivar o activar una ruta, cambiar su capacidad (1–12) o agregar una conexión. Los lazos, los arcos repetidos y los recíprocos se rechazan. Después hay que pulsar **Recalcular**.
4. En **Comparar configuraciones** se guarda cada resultado o se cargan las 3 configuraciones del proyecto en una tabla.

El cálculo de flujo **no** usa bibliotecas: Streamlit y Graphviz (DOT) solo dibujan.

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
   2. Formular las restricciones del flujo (capacidad y conservación), el valor del flujo |x| y el problema de flujo máximo como optimización. ✅
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
        - 2.2d.2 Resumen del modelo completo y tamaño del problema en la red principal (variables y restricciones). ✅
   3. Aplicar el modelo a la red principal: escribir las ecuaciones de conservación de cada centro intermedio y explicar los supuestos e interpretación del modelo.
3. **Teorema de flujo máximo–corte mínimo**: investigarlo, definir c(S, T) y explicar por qué el corte obtenido del grafo residual es mínimo.
4. **Caso de verificación manual (4–6 vértices)**: resolverlo a mano con caminos aumentantes, encontrar un flujo y un corte de igual valor y compararlo con la salida del código (capturas). — borrador listo en [docs/caso_manual.md](docs/caso_manual.md) (revisar)
5. **Verificación de las 3 configuraciones e informe final**: comprobar capacidades, conservación y flujo = corte en la red inicial y sus dos modificaciones; unir las secciones del informe en PDF con las referencias.

### Persona 2 — Investigación e implementación del algoritmo — [docs/tarea_p2_algoritmo.md](docs/tarea_p2_algoritmo.md)

1. Investigar y comparar Ford–Fulkerson (DFS) y Edmonds–Karp (BFS), con fuentes académicas, y justificar la elección. ✅ (incluye comparación empírica: `python scripts/comparar_algoritmos.py`)
2. Implementar con código propio el grafo residual, la búsqueda BFS de caminos aumentantes y Edmonds–Karp (valor máximo y flujo de cada arco original). ✅
3. Implementar el corte mínimo: S = vértices alcanzables desde s en el residual, T = el resto, y los arcos de S hacia T. ✅
4. Implementar las comprobaciones: capacidades, conservación del flujo y valor del flujo = capacidad del corte. ✅
5. Documentar las funciones (entradas, salidas y propósito) y escribir la sección del informe sobre investigación e implementación. ✅

### Persona 3 — Interfaz interactiva y simulación — [docs/tarea3_resultados.md](docs/tarea3_resultados.md)

1. Construir la interfaz que dibuje los centros, las rutas, sus direcciones y capacidades (sin usar funciones de flujo de bibliotecas). ✅
2. Agregar los controles: elegir origen y destino, botón Calcular/Recalcular, mostrar el flujo máximo, flujo/capacidad por arco y la partición S | T resaltando los arcos del corte. ✅
3. Permitir modificaciones desde la interfaz: desactivar una ruta, cambiar su capacidad y agregar una conexión, rechazando arcos inválidos. ✅
4. Definir y analizar las 3 configuraciones (inicial + 2 modificaciones): flujo máximo, corte mínimo e interpretación de las diferencias. ✅ (22 → 15 sin D→H; 22 → 25 con E→T)
5. Preparar el repositorio (README, `requirements.txt`, instrucciones), escribir la sección de resultados con capturas y liderar la demo. ✅ (demo pendiente de ensayo)

## Calendario

| Fecha | Hito |
|---|---|
| 18 nov | Red principal y formato de datos definidos (Juan Pablo) ✅ |
| 21 nov | Algoritmo y corte mínimo funcionando (P2); interfaz básica dibujando la red (P3) ✅ |
| 23 nov | Integración completa y modificaciones funcionando |
| 24 nov | Resultados de las 3 configuraciones y verificación manual comparada con el código |
| 25 nov | Informe armado y ensayo de la presentación (12 min, unos 4 por persona) |
| 26 nov | Presentación y entrega del PDF antes de las 23:00 |
