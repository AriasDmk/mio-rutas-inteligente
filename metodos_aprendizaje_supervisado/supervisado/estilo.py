"""
Estilo editorial común (gráficas y documentos).

Paleta sobria: tinta azul marino para lo esencial, grises para lo secundario y
un único azul de acento reservado para el hallazgo más importante de cada figura.
Tipografía: Carlito (métrica de Calibri) para texto y Caladea (métrica de
Cambria) para títulos; ambas libres y compatibles con Word/PDF.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

# ---- colores (sistema editorial) ----
FONDO = "#FFFFFF"
TINTA = "#051C2C"          # títulos y anclas visuales
TEXTO = "#303841"          # texto principal
TEXTO_2 = "#626A70"        # ejes, notas, metadatos
SUPERFICIE = "#F3F4F5"
BORDE = "#D9DDE0"
ACENTO = "#2251FF"         # uso excepcional: un solo hallazgo por figura
NEUTRO = "#9AA8B4"         # barras de contexto

# Clases ordinales: un solo tono (azul marino), de claro a oscuro (validado: contraste y ΔL)
CLASES = ["Baja", "Media", "Alta"]
COLOR_CLASE = {"Baja": "#9AA8B4", "Media": "#4A6074", "Alta": "#051C2C"}

# compatibilidad con nombres anteriores
SERIE = TINTA
SECUNDARIO = NEUTRO
GRILLA = BORDE

CROSEXTRA = "/usr/share/fonts/truetype/crosextra"
FUENTES = {
    "texto": os.path.join(CROSEXTRA, "Carlito-Regular.ttf"),
    "texto_b": os.path.join(CROSEXTRA, "Carlito-Bold.ttf"),
    "texto_i": os.path.join(CROSEXTRA, "Carlito-Italic.ttf"),
    "titulo": os.path.join(CROSEXTRA, "Caladea-Regular.ttf"),
    "titulo_b": os.path.join(CROSEXTRA, "Caladea-Bold.ttf"),
}


def familia_texto() -> str:
    """Registra Carlito en matplotlib si está instalada; si no, usa una sans genérica."""
    if os.path.exists(FUENTES["texto"]):
        for clave in ("texto", "texto_b", "texto_i"):
            font_manager.fontManager.addfont(FUENTES[clave])
        return "Carlito"
    return "DejaVu Sans"


def aplicar():
    fam = familia_texto()
    plt.rcParams.update({
        "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
        "font.family": fam, "font.size": 10.5, "text.color": TEXTO,
        "axes.edgecolor": BORDE, "axes.labelcolor": TEXTO_2, "axes.titlecolor": TINTA,
        "axes.titlesize": 12.5, "axes.titleweight": "normal", "axes.titlelocation": "left",
        "axes.titlepad": 12, "axes.labelsize": 10, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
        "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "axes.grid": True, "axes.grid.axis": "y",
        "grid.color": BORDE, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "xtick.major.size": 0, "ytick.major.size": 0,
        "legend.frameon": False, "legend.fontsize": 9.5, "figure.dpi": 110,
    })


def nota_fuente(fig, texto="Fuente: dataset de prueba sobre la red real del SIUR (n = 8000)."):
    fig.text(0.01, 0.01, texto, fontsize=8, color=TEXTO_2, ha="left", va="bottom")
