# MIO Cali: rutas inteligentes y predicción de ocupación

Dos módulos en Python sobre la red del sistema de transporte masivo MIO (Cali), construida con datos del Buscarutas del SIUR.

| Módulo | Carpeta | Qué hace |
|---|---|---|
| Rutas | raíz | Reglas lógicas, motor de inferencia propio y búsqueda A* para la mejor ruta entre dos estaciones |
| Ocupación | [`metodos_aprendizaje_supervisado/`](metodos_aprendizaje_supervisado/README.md) | Árboles de decisión (ID3 propio y scikit-learn) para predecir el nivel de ocupación de un bus |

## Requisitos

Python 3.8 o superior. El módulo de rutas usa solo la biblioteca estándar.

## Uso del módulo de rutas

```bash
python main.py estaciones
python main.py ruta "Andres Sanin" Universidades --detalle
python main.py ruta menga capri --algoritmo bfs            # astar | ucs | voraz | bfs
python main.py ruta aguablanca univalle --criterio transbordos
python main.py ruta andres_sanin universidades --cerrar "San Pascual"
python main.py ruta menga universidades --suspender e21 t31
python main.py comparar canaverales popular
python main.py consultar "transbordo(centro, t31, R)"
python main.py explicar "costo_transbordo(unidad_deportiva, C)"
python main.py reglas
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Actualizar los datos de la red

```bash
python herramientas/descargar_siur.py T31 T40 T47 T50 T57 T62 T12 E21 E37   # requiere Internet
python herramientas/construir_base.py                                       # regenera el .pl
```

## Estructura

```
├── datos/rutas_siur.json               # paradas ordenadas por recorrido (SIUR)
├── herramientas/
│   ├── descargar_siur.py               # descarga desde la API del SIUR
│   └── construir_base.py               # genera la base de conocimiento
├── conocimiento/base_conocimiento.pl   # hechos y reglas (sintaxis tipo Prolog)
├── mio/
│   ├── logica.py      # analizador + encadenamiento hacia adelante semi-ingenuo
│   ├── busqueda.py    # espacio de estados, heurística, A*, UCS, voraz, BFS
│   └── sistema.py     # integra conocimiento y búsqueda
├── main.py            # interfaz de línea de comandos
├── tests/
└── metodos_aprendizaje_supervisado/
```

## Diseño

- **Conocimiento:** cláusulas de Horn con negación por fallo estratificada y reglas recursivas. Trece reglas derivan conexiones, disponibilidad, transbordos, costos y alcanzabilidad.
- **Inferencia:** encadenamiento hacia adelante semi-ingenuo, con un índice por el primer argumento y la explicación de cada hecho derivado.
- **Búsqueda:** el estado es el par (estación, ruta actual). La heurística es la distancia en línea recta dividida por la velocidad máxima de la red. Es admisible, así que A\* es óptimo.
- **Supuestos:** el SIUR no publica tiempos ni frecuencias. Se usan 20 km/h para troncales y 24 km/h para expresos, con frecuencias de 8 y 10 min. Todo se puede ajustar en `herramientas/construir_base.py`.
