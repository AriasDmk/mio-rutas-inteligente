# Agrupamiento de estaciones del MIO por perfil de demanda

Este módulo agrupa las 81 estaciones de la red del MIO según la forma de su demanda horaria. Las entradas y salidas por hora sirven para saber si una estación es origen de viajes, destino, punto de intercambio, zona de estudio o zona recreativa.

Se usan tres métodos:
- K-means implementado desde cero, con inicio k-means++ y varias repeticiones.
- K-means de scikit-learn.
- Agrupamiento jerárquico con el método de Ward.

## Instalación

```bash
cd metodos_aprendizaje_no_supervisado
pip install -r requirements.txt
```

## Uso

```bash
python agrupamiento_mio.py generar             # crea datos/demanda_horaria.csv (45.360 registros, semilla 7)
python agrupamiento_mio.py explorar            # estadísticas y perfiles de ejemplo
python agrupamiento_mio.py kmeans              # K-means paso a paso: inercia y cambios por iteración
python agrupamiento_mio.py elegir-k            # método del codo y coeficiente de silueta (k = 2 … 9)
python agrupamiento_mio.py agrupar             # agrupa, compara modelos, valida y grafica
python agrupamiento_mio.py estacion "Univalle" # grupo de una estación y las estaciones más parecidas
python agrupamiento_mio.py todo                # generar + explorar + agrupar
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Estructura

```
├── agrupamiento_mio.py         # interfaz de comandos
├── agrupamiento/
│   ├── red.py                  # red del MIO (lee ../datos/rutas_siur.json)
│   ├── dataset.py              # demanda horaria por estación (reproducible)
│   ├── caracteristicas.py      # 43 variables de forma de la demanda por estación
│   ├── kmeans.py               # K-means (Lloyd + k-means++) y silueta
│   ├── modelos.py              # elección de k, comparación, validación, gráficas
│   ├── explorar.py             # análisis exploratorio
│   └── estilo.py               # estilo de gráficas
├── datos/
│   ├── demanda_horaria.csv     # estación, fecha, tipo de día, hora, entradas, salidas
│   └── perfil_oculto.csv       # perfil de generación (solo para validación externa)
└── tests/
```

## Datos

- **Red real:** las estaciones, las líneas y las coordenadas vienen del SIUR.
- **Demanda simulada:** las entradas y salidas por hora no son públicas. Se generan con perfiles de uso documentados en `agrupamiento/dataset.py`. Cada estación combina su perfil con una parte de otro perfil y tiene ruido de Poisson.
- **Perfil oculto:** `perfil_oculto.csv` guarda el perfil con el que se generó cada estación. Los modelos no lo usan. Sirve únicamente para medir con el índice de Rand ajustado si el agrupamiento recupera la estructura.
