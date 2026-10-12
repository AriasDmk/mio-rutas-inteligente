"""
Construcción de la matriz de características por estación a partir de la demanda horaria.

Cada estación se describe por la FORMA de su demanda, no por su tamaño, para que
dos estaciones con el mismo patrón queden juntas aunque una mueva más gente:

  e04 … e23   proporción de las entradas de un día laboral que ocurre en cada hora
  s04 … s23   lo mismo para las salidas
  finde       demanda de un día de fin de semana / demanda de un día laboral
  balance_am  (entradas − salidas) / (entradas + salidas) entre las 6 y las 8
  balance_pm  lo mismo entre las 17 y las 19

El volumen medio diario se conserva aparte para describir los grupos.
"""

import numpy as np
import pandas as pd

from .dataset import HORAS


def construir(demanda: pd.DataFrame) -> pd.DataFrame:
    lab = demanda[demanda.tipo_dia == "laboral"]
    fin = demanda[demanda.tipo_dia != "laboral"]
    n_lab = lab.fecha.nunique()
    n_fin = max(fin.fecha.nunique(), 1)

    e = lab.pivot_table(index="estacion", columns="hora", values="entradas", aggfunc="sum")[HORAS]
    s = lab.pivot_table(index="estacion", columns="hora", values="salidas", aggfunc="sum")[HORAS]
    X = pd.concat([e.div(e.sum(axis=1), axis=0).add_prefix("e").rename(columns=lambda c: f"e{int(c[1:]):02d}"),
                   s.div(s.sum(axis=1), axis=0).add_prefix("s").rename(columns=lambda c: f"s{int(c[1:]):02d}")],
                  axis=1)
    tot_lab = (lab.groupby("estacion")[["entradas", "salidas"]].sum().sum(axis=1)) / n_lab
    tot_fin = (fin.groupby("estacion")[["entradas", "salidas"]].sum().sum(axis=1)) / n_fin
    X["finde"] = (tot_fin / tot_lab).reindex(X.index).fillna(0)

    def balance(h0, h1):
        t = lab[(lab.hora >= h0) & (lab.hora <= h1)].groupby("estacion")[["entradas", "salidas"]].sum()
        return ((t.entradas - t.salidas) / (t.entradas + t.salidas)).reindex(X.index)

    X["balance_am"] = balance(6, 8)
    X["balance_pm"] = balance(17, 19)
    X["volumen_diario"] = tot_lab.reindex(X.index).round(0)
    return X


COLUMNAS_MODELO = [f"e{h:02d}" for h in HORAS] + [f"s{h:02d}" for h in HORAS] + ["finde", "balance_am", "balance_pm"]


def estandarizar(X: pd.DataFrame):
    """Z-score columna a columna. Devuelve (matriz numpy, medias, desviaciones)."""
    M = X[COLUMNAS_MODELO].to_numpy(dtype=float)
    mu, sd = M.mean(axis=0), M.std(axis=0)
    sd[sd == 0] = 1
    return (M - mu) / sd, mu, sd
