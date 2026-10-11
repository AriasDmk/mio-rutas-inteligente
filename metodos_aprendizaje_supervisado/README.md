# Predicción de ocupación de buses del MIO

Clasificación del nivel de ocupación (Baja / Media / Alta) de un bus al llegar a una estación, con árboles de decisión: un ID3 implementado desde cero, un árbol de scikit-learn, Random Forest y una línea base.

## Instalación

```bash
cd metodos_aprendizaje_supervisado
pip install -r requirements.txt
```

## Uso

```bash
python ocupacion.py generar      # crea datos/dataset_ocupacion.csv (8000 registros, semilla 42)
python ocupacion.py explorar     # estadísticas y gráficas en resultados/graficas
python ocupacion.py id3          # entropía y ganancia de información paso a paso
python ocupacion.py entrenar     # entrena y compara modelos; guarda métricas, reglas y modelos
python ocupacion.py reglas       # reglas SI-ENTONCES e inferencia con ../mio/logica.py
python ocupacion.py predecir --estacion Centro --hora 7 --dia lunes --sentido hacia_centro --lluvia si
python ocupacion.py todo         # generar + explorar + entrenar
```

`predecir` acepta estas opciones:

| Opción | Valores |
|---|---|
| `--estacion` | nombre de la estación, con o sin tildes |
| `--hora` | 0 a 23 |
| `--dia` | lunes a domingo, o una fecha AAAA-MM-DD |
| `--sentido` | `hacia_centro` o `hacia_periferia` |
| `--lluvia` | `si` o `no` |
| `--linea` | código de la línea |
| `--evento` | `si` o `no` |
| `--festivo` | sin valor |
| `--json` | sin valor |

## Pruebas

```bash
python -m unittest discover -s tests -v
```

Si no existen el dataset o los modelos, las pruebas los generan antes de ejecutarse.

## Estructura

```
├── ocupacion.py               # interfaz de comandos
├── supervisado/
│   ├── red.py                 # red del MIO (lee ../datos/rutas_siur.json)
│   ├── dataset.py             # generación del dataset (reglas + ruido, reproducible)
│   ├── explorar.py            # análisis exploratorio
│   ├── id3.py                 # ID3: entropía, ganancia, poda, exportación de reglas
│   ├── modelos.py             # entrenamiento, validación cruzada y métricas
│   ├── predecir.py            # predicción con explicación
│   └── estilo.py              # estilo de gráficas
├── datos/dataset_ocupacion.csv
├── tests/
├── resultados/                # se genera con "entrenar"
└── modelos/                   # se genera con "entrenar"
```

## Datos

- **Red real:** las estaciones, las líneas, las coordenadas y el orden del recorrido vienen del SIUR.
- **Ocupación simulada:** la ocupación no es un dato público. Se simula con las reglas de `supervisado/dataset.py`, más ruido gaussiano y un 8 % de etiquetas cambiadas. Por eso las métricas miden qué tan bien el modelo recupera esos patrones.
