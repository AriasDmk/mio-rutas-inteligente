"""Análisis exploratorio de la demanda horaria."""

import os

import pandas as pd

from .dataset import HORAS
from .estilo import NEUTRO, TINTA, aplicar, nota_fuente, plt

CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAFICAS = os.path.join(CARPETA, "resultados", "graficas")
EJEMPLOS = ["Nuevo Latir", "Plaza de Cayzedo", "Calipso", "Univalle", "Estadio"]


def resumen(d: pd.DataFrame) -> str:
    dia = d.groupby(["estacion", "fecha", "tipo_dia"])[["entradas", "salidas"]].sum().reset_index()
    dia["total"] = dia.entradas + dia.salidas
    lab = dia[dia.tipo_dia == "laboral"].groupby("estacion").total.mean()
    l = [f"Registros: {len(d):,}".replace(",", ".") + f"   Estaciones: {d.estacion.nunique()}   "
         f"Días: {d.fecha.nunique()} ({d.fecha.min()} a {d.fecha.max()})   Horas: {d.hora.min()} a {d.hora.max()}",
         f"Valores nulos: {int(d.isna().sum().sum())}   Entradas totales: {int(d.entradas.sum()):,}".replace(",", ".")
         + f"   Salidas totales: {int(d.salidas.sum()):,}".replace(",", "."),
         "", "Movimiento diario (entradas + salidas) en día laboral, por estación:",
         f"  mínimo {int(lab.min()):,}  ({lab.idxmin()})".replace(",", "."),
         f"  mediana {int(lab.median()):,}".replace(",", "."),
         f"  máximo {int(lab.max()):,}  ({lab.idxmax()})".replace(",", "."),
         "", "Promedio por tipo de día (movimiento por estación):"]
    for t, v in dia.groupby("tipo_dia").total.mean().reindex(["laboral", "sabado", "domingo_festivo"]).items():
        l.append(f"  {t:<16} {int(v):,}".replace(",", "."))
    return "\n".join(l)


def graficar(d: pd.DataFrame, carpeta: str = GRAFICAS):
    aplicar()
    os.makedirs(carpeta, exist_ok=True)
    lab = d[d.tipo_dia == "laboral"]
    n = lab.fecha.nunique()
    fig, axs = plt.subplots(1, len(EJEMPLOS), figsize=(3.0 * len(EJEMPLOS), 3.2), sharey=False)
    for ax, e in zip(axs, EJEMPLOS):
        s = lab[lab.estacion == e].groupby("hora")[["entradas", "salidas"]].sum() / n
        ax.plot(HORAS, s.entradas.reindex(HORAS), color=TINTA, lw=2, label="entradas")
        ax.plot(HORAS, s.salidas.reindex(HORAS), color=NEUTRO, lw=1.8, ls="--", label="salidas")
        ax.set_title(e, fontsize=11)
        ax.set_xticks([6, 12, 18])
        ax.set_xlabel("Hora")
    axs[0].set_ylabel("Personas por hora (promedio)")
    axs[0].legend(loc="upper right", fontsize=8.5)
    fig.suptitle("Cinco estaciones, cinco formas de demanda en un día laboral", x=0.01, ha="left", fontsize=12.5,
                 color=TINTA)
    nota_fuente(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    ruta = os.path.join(carpeta, "01_perfiles_ejemplo.png")
    fig.savefig(ruta, dpi=160)
    plt.close(fig)
    return [ruta]
