# Resultados y Análisis de Algoritmos de Búsqueda (MIO)

## 1. Definición de Estado y Heurística de A*
* **Estado:** En este problema, un estado se define como la combinación de la **estación actual** y la **ruta** en la que se encuentra el usuario (ej. `('andres_sanin', 't40')`).
* **Heurística de A*:** Es admisible porque nunca sobreestima el costo real (tiempo o distancia) para llegar desde una estación dada hasta la estación de destino, garantizando encontrar siempre la ruta óptima.

## 2. Resultados de las Pruebas y Comparaciones
Los algoritmos se evaluaron comparando métricas como tiempo total, transbordos y nodos expandidos:
* **A*** encuentra la ruta óptima garantizando el menor costo combinando el costo real y la heurística.
* **Algoritmo Voraz (Greedy):** Tiende a ser muy rápido y expande menos nodos al enfocarse ciegamente en acercarse a la meta, pero **no siempre garantiza la ruta óptima**.

## 3. Contexto Dinámico (Estaciones Cerradas y Criterios)
* **Cierre de estaciones (ej. San Pascual):** El sistema recalcula automáticamente la ruta óptima evitando la estación cerrada, obligando a tomar rutas alternativas o desvíos.
* **Criterio de transbordos:** Al optimizar por transbordos (como se probó de Aguablanca a Univalle), el sistema prioriza minimizar los cambios de ruta sobre el tiempo bruto de viaje.

## 4. Pruebas Automáticas
* Se ejecutaron exitosamente todas las pruebas unitarias del módulo de pruebas (`python -m unittest discover -s tests -v`), obteniendo un total de **27 pruebas pasadas con éxito (OK)**.