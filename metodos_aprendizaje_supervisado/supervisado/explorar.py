"""Análisis exploratorio del dataset (EDA): estadísticas y gráficas."""

import os

import pandas as pd

from .estilo import CLASES, COLOR_CLASE, FONDO, TEXTO_2, aplicar, nota_fuente, plt

CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAFICAS = os.path.join(CARPETA, "resultados", "graficas")


def cargar(ruta):
    return pd.read_csv(ruta)


def resumen(df: pd.DataFrame) -> str:
    l = [f"Registros: {len(df)}   Columnas: {df.shape[1]}   Valores nulos: {int(df.isna().sum().sum())}",
         f"Periodo: {df.fecha.min()} a {df.fecha.max()}   Estaciones: {df.estacion.nunique()}   "
         f"Líneas: {df.linea.nunique()}", "", "Distribución de la variable objetivo (nivel_ocupacion):"]
    vc = df.nivel_ocupacion.value_counts()
    for c in CLASES:
        l.append(f"  {c:<6} {vc.get(c, 0):>5}  ({vc.get(c, 0) / len(df):.1%})")
    l += ["", "Ocupación ALTA por franja horaria:"]
    alta = df.assign(alta=df.nivel_ocupacion.eq("Alta")).groupby("franja").alta.mean()
    for f in ["madrugada", "pico_am", "valle", "pico_pm", "noche"]:
        l.append(f"  {f:<10} {alta.get(f, 0):6.1%}")
    l += ["", "Ocupación ALTA en hora pico según sentido:"]
    pico = df[df.franja.isin(["pico_am", "pico_pm"])]
    t = pico.assign(alta=pico.nivel_ocupacion.eq("Alta")).groupby(["franja", "sentido"]).alta.mean()
    for (f, s), v in t.items():
        l.append(f"  {f:<8} {s:<16} {v:6.1%}")
    return "\n".join(l)


def _barras_apiladas(ax, tabla, titulo, xlabel):
    tabla = tabla.reindex(columns=CLASES).fillna(0)
    abajo = None
    for c in CLASES:
        ax.bar(tabla.index.astype(str), tabla[c], bottom=abajo, color=COLOR_CLASE[c],
               label=c, edgecolor=FONDO, linewidth=1.2, width=0.72)
        abajo = tabla[c] if abajo is None else abajo + tabla[c]
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Proporción de registros")
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.legend(title="Ocupación", loc="upper left", bbox_to_anchor=(1, 1))


def graficar(df: pd.DataFrame, carpeta: str = GRAFICAS):
    """Gráficas del análisis exploratorio. Cada título enuncia el hallazgo."""
    aplicar()
    os.makedirs(carpeta, exist_ok=True)
    rutas = []
    vc = df.nivel_ocupacion.value_counts().reindex(CLASES)
    pr = vc / len(df)

    # 1. distribución de clases
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    barras = ax.bar(CLASES, vc.values, color=[COLOR_CLASE[c] for c in CLASES], width=0.55)
    for b, v in zip(barras, vc.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 45, f"{v:,}".replace(",", ".") + f"  ({v / len(df):.0%})",
                ha="center", color=TEXTO_2, fontsize=9.5)
    ax.set_title(f"{pr.idxmax()} es la clase más frecuente ({pr.max():.0%}); ninguna baja del {pr.min():.0%}")
    ax.set_ylabel("Registros")
    ax.set_ylim(0, vc.max() * 1.2)
    nota_fuente(fig)
    rutas.append(_guardar(fig, carpeta, "01_distribucion_clases.png"))

    # 2. ocupación por hora
    fig, ax = plt.subplots(figsize=(8.8, 3.9))
    t = pd.crosstab(df.hora, df.nivel_ocupacion, normalize="index")
    _barras_apiladas(ax, t, "La ocupación alta se concentra en dos picos: 6–8 h y 17–19 h", "Hora del día")
    nota_fuente(fig)
    rutas.append(_guardar(fig, carpeta, "02_ocupacion_por_hora.png"))

    # 3. pico x sentido
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    pico = df[df.franja.isin(["pico_am", "pico_pm"])]
    t = pd.crosstab([pico.franja, pico.sentido], pico.nivel_ocupacion, normalize="index")
    alta = t["Alta"].max()
    t.index = [f"{'Pico AM' if f == 'pico_am' else 'Pico PM'}\n{s.replace('_', ' ')}" for f, s in t.index]
    _barras_apiladas(ax, t, f"En hora pico el sentido decide: hasta {alta:.0%} de ocupación alta en el sentido "
                     "de la demanda", "")
    nota_fuente(fig)
    rutas.append(_guardar(fig, carpeta, "03_pico_por_sentido.png"))

    # 4. tipo de día y tipo de estación
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.9))
    t = pd.crosstab(df.tipo_dia, df.nivel_ocupacion, normalize="index").reindex(
        ["laboral", "sabado", "domingo_festivo"])
    t.index = ["laboral", "sábado", "domingo /\nfestivo"]
    _barras_apiladas(axs[0], t, "Domingos y festivos: la mitad de la ocupación", "")
    axs[0].get_legend().remove()
    t = pd.crosstab(df.tipo_estacion, df.nivel_ocupacion, normalize="index").reindex(
        ["sencilla", "transbordo", "terminal"])
    _barras_apiladas(axs[1], t, "Las estaciones de transbordo son las más llenas", "")
    nota_fuente(fig)
    rutas.append(_guardar(fig, carpeta, "04_dia_y_estacion.png"))
    return rutas


def _guardar(fig, carpeta, nombre):
    ruta = os.path.join(carpeta, nombre)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(ruta, dpi=160)
    plt.close(fig)
    return ruta
