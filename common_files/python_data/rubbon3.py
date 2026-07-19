import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
import colorsys
from enum import Enum

import time

class Mode(Enum):
    RELATIVE = "relative"
    GLOBAL = "global"

def hex_to_ansi(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"

def generate_colors(n: int) -> list:
    x = np.linspace(0, 256 ** 3, n+2)

    lst = []
    for nb in x[1:-1]:
        nb = int(nb)
        hex_clr = f"#{nb:06X}"
        lst.append(hex_clr)
    return lst

def rubbon_graph(x: list | np.ndarray, 
                 y: list | np.ndarray,
                 fig: go.Figure,
                 *,
                 set_colors: list | None = None,
                 points: int = 200,
                 evolution: Mode = Mode.RELATIVE):

    x = np.asarray(x)
    y = np.asarray(y)

    if x.ndim != 1:
        raise ValueError("x must be 1D")

    if y.ndim != 2:
        raise ValueError("y must be 2D")

    if y.shape[1] != len(x):
        raise ValueError("y must have same number of columns as len(x)")

    y_nb = len(y)
    x_nb = len(x)

    if set_colors is None or len(set_colors) < y_nb:
        set_colors = generate_colors(y_nb) 

    positions = np.arange(y_nb)
    arg_sort = np.argsort(y[:, 0])

    low_value = norm.ppf(0.01, 0, 1)
    high_value = (0 - low_value)
    x_distrib = np.linspace(low_value, high_value, points)
    ref_y = norm.cdf(x_distrib, 
                     0, 
                     1)

    ref_y = (ref_y - ref_y[0]) / (ref_y[-1] - ref_y[0])

    end = positions[arg_sort]

    for i in range(0, x_nb - 1, 1):

        start = end
        cur_col = y[:, i+1]
        arg_sort = np.argsort(cur_col)
        end = positions[np.argsort(arg_sort)]
       
        norm_value = 0
        norm_value2 = 0

        if evolution == Mode.RELATIVE:

            norm_value = y[:, i].max()
            norm_value2 = cur_col.max()

        else:

            norm_value = y[:, i].sum()
            norm_value2 = cur_col.sum()

        cur_x = np.linspace(x[i], x[i+1], points)
        
        for i2 in range(y_nb):
       
            ratio_begin = y[i2, i] / norm_value
            ratio_end = y[i2, i+1] / norm_value2

            ratio = np.linspace(ratio_begin, 
                                ratio_end, 
                                points)

            delta = end[i2] - start[i2]
            cur_y = start[i2] + delta * ref_y

            cur_color = set_colors[i2]

            fig.add_trace(go.Scatter(
                x=cur_x,
                y=cur_y + (ratio * 0.5),
                mode='lines',
                line=dict(width=0, color=cur_color),
                showlegend=False,
            ))

            fig.add_trace(go.Scatter(
                x=cur_x,
                y=cur_y - (ratio * 0.5),
                mode='lines',
                line=dict(width=0, color=cur_color),
                fill="tonexty",
                showlegend=False,
            ))

    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

years = [2000, 2005, 2010, 2015]

values = np.array([
    [1.2, 1.4, 0.9, 2], 
    [0.1, 0.6, 0.5, 0.95], 
    [2, 3, 1.5, 1.3], 
    [2, 1, 3, 1.5], 
    [0.55, 1.95, 1.2, 2.4]
])

fig = go.Figure()

rubbon_graph(years, 
             values,
             fig,
             evolution=Mode.RELATIVE)

fig.write_image("rubbon.pdf")

fig2 = go.Figure()

strt = time.time()

rubbon_graph(years, 
             values,
             fig2,
             evolution=Mode.GLOBAL)

end = time.time()

fig2.write_image("rubbon2.pdf")

print(end-strt)

