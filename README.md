# Sistema inteligente de rutas MIO (Cali)

**Actividad 2 – Búsqueda y sistemas basados en reglas**
Base de conocimiento en **reglas lógicas** + **búsqueda heurística A\*** para encontrar la mejor ruta entre dos estaciones del sistema de transporte masivo MIO.

Los datos de la red son **reales**: se descargaron del [Buscarutas del SIUR](https://servicios.siur.com.co/buscarutas/) (paradas y recorrido de cada línea). La base incluye **81 estaciones** y **9 líneas**: troncales T31, T40, T47, T50, T57, T62 y T12, y expresos E21 y E37.

---

## 1. Requisitos e instalación

- Python **3.8 o superior** (el sistema usa solo la biblioteca estándar, no requiere instalar paquetes).

```bash
git clone https://github.com/AriasDmk/mio-rutas-inteligente.git
cd mio-rutas-inteligente
```

## 2. Ejecución

```bash
# Listar estaciones y las rutas que pasan por cada una
python main.py estaciones

# Mejor ruta de A a B (A* por defecto). Acepta nombres con o sin tildes
python main.py ruta "Andres Sanin" Universidades
python main.py ruta andres_sanin universidades --detalle      # muestra la secuencia de estados

# Elegir algoritmo: astar | ucs | voraz | bfs
python main.py ruta menga capri --algoritmo bfs

# Elegir criterio: tiempo (defecto) | transbordos
python main.py ruta aguablanca univalle --criterio transbordos

# Contexto dinámico: estaciones cerradas / rutas suspendidas
python main.py ruta andres_sanin universidades --cerrar "San Pascual"
python main.py ruta menga universidades --suspender e21 t31

# Comparar los 4 algoritmos (tiempo, transbordos, nodos expandidos, ms)
python main.py comparar canaverales popular

# Consultas lógicas directas a la base de conocimiento (estilo Prolog)
python main.py consultar "sirve(R, centro)"
python main.py consultar "transbordo(centro, t31, R)"

# ¿Por qué? Árbol de prueba de un hecho derivado
python main.py explicar "costo_transbordo(unidad_deportiva, C)"
python main.py explicar "disponible(t40, belalcazar, centro, T)" --cerrar san_pascual

# Ver las reglas y estadísticas de inferencia
python main.py reglas
```

## 3. Pruebas

```bash
python -m unittest discover -s tests -v           # 27 pruebas automáticas (~15 s)
```
El informe con las pruebas y escenarios ejecutados está en `docs/Informe_de_pruebas.pdf`.

## 4. Actualizar los datos del MIO

```bash
python herramientas/descargar_siur.py T31 T40 T47 T50 T57 T62 T12 E21 E37   # requiere Internet
python herramientas/construir_base.py                                       # regenera el .pl
```
`descargar_siur.py` usa la API pública del Buscarutas (`api/paradas.php` y `api/recorrido.php`). Para ordenar las paradas, proyecta cada una sobre la polilínea del recorrido. Luego `construir_base.py` convierte ese orden en hechos lógicos.

## 5. Estructura

```
mio-rutas-inteligente/
├── datos/rutas_siur.json               # paradas reales ordenadas por recorrido (SIUR)
├── herramientas/
│   ├── descargar_siur.py               # descarga desde la API del SIUR
│   └── construir_base.py               # genera la base de conocimiento .pl
├── conocimiento/base_conocimiento.pl   # HECHOS y REGLAS (lenguaje lógico)
├── mio/
│   ├── logica.py      # analizador + motor de inferencia (encadenamiento hacia adelante)
│   ├── busqueda.py    # espacio de estados, heurística, A*, UCS, voraz, BFS
│   └── sistema.py     # integra conocimiento + búsqueda, itinerario legible
├── main.py            # interfaz de línea de comandos
├── tests/             # pruebas unitarias (unittest)
└── docs/              # informe de pruebas
```

## 6. Cómo funciona

### 6.1 Representación del conocimiento
Cláusulas de Horn con sintaxis tipo Prolog (`conocimiento/base_conocimiento.pl`):

| Tipo | Ejemplo |
|---|---|
| Hecho | `tramo(t40, centro, la_ermita, 1.8).` |
| Regla | `sirve(R, E) :- conecta(R, E, _, _).` |
| Negación por fallo | `disponible(R,A,B,T) :- conecta(R,A,B,T), \+ cerrada(A), \+ cerrada(B), \+ suspendida(R).` |
| Recursión | `alcanzable(A, C) :- vecinas(A, B), alcanzable(B, C).` |

Hay 13 reglas (R1–R13): tramos dirigidos en el sentido real del bus, qué rutas sirven cada estación, disponibilidad, **paso sin parada por una estación cerrada (R4)**, transbordos, costo del transbordo (3 min en terminal, 5 en estación), espera promedio (mitad de la frecuencia), vecindad y alcanzabilidad.

**Supuestos:** el SIUR no publica tiempos ni frecuencias. Se usan 20 km/h para troncales y 24 km/h para expresos, y frecuencias de 8 y 10 min. Todo se puede ajustar en `herramientas/construir_base.py`.

### 6.2 Motor de inferencia (`mio/logica.py`)
- **Encadenamiento hacia adelante semi-ingenuo** hasta el punto fijo: en cada vuelta solo se combinan los hechos nuevos. Con 496 hechos base se derivan 8217 hechos en unos 0.3 s.
- **Unificación** de variables, con índice por el primer argumento.
- **Estratificación** automática: la negación (`\+`) se evalúa cuando el predicado negado ya está completo.
- Predicados incorporados: `distinto/2`, `igual/2`, `menor/2`, `mitad/2`, `suma/3`.
- **Explicación**: guarda qué regla y qué hechos produjeron cada conclusión.

### 6.3 Búsqueda (`mio/busqueda.py`)
- **Estado** = (estación, ruta en la que voy). Así el algoritmo "sabe" cuándo cambia de bus.
- **Acciones**: abordar (costo = espera), viajar un tramo (minutos) y transbordo (costo de transbordo + espera).
- **Heurística**: `h(n) = distancia en línea recta al destino / velocidad máxima de la red`.
  Ningún recorrido es más corto que la línea recta ni más rápido que la velocidad máxima. Por eso h **nunca sobreestima**: es **admisible** y A\* es **óptimo**. Se verificó en los 6480 pares de estaciones, y A\* expande un 32 % menos nodos que costo uniforme.
- Se comparan **A\*** (g+h), **costo uniforme** (g), **voraz** (h) y **amplitud** (número de acciones).

### 6.4 Limitaciones
- Una estación con dos sentidos (plataformas A y B) se modela como un solo nodo, así que cambiar de sentido dentro de la estación no tiene costo.
- La regla R4 cubre una estación cerrada entre dos abiertas. No cubre dos estaciones cerradas seguidas.
- No se incluyen alimentadores (A…) ni pretroncales (P…).

## 7. Autores
- José Luis Arias
- Juan Sebastián Gómez Torres
