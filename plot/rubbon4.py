import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
import colorsys
from enum import Enum

import time

class Mode(Enum):
    RELATIVE = "relative"
    GLOBAL = "global"

def hex_to_ansi(hex_color: str) -> str:
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

def invert_hex(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = 255 - r
    g = 255 - g
    b = 255 - b

    return f"#{r:02X}{g:02X}{b:02X}"

def get_text_color(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    luminance = 0.299*r + 0.587*g + 0.114*b
    
    return "#000000" if luminance > 128 else "#FFFFFF"

def rubbon_graph(x: list | np.ndarray, 
                 y: list | np.ndarray,
                 fig: go.Figure,
                 *,
                 set_colors: list | None = None,
                 points: int = 200,
                 evolution: Mode = Mode.RELATIVE,
                 scale_font: bool = True,
                 image_set: list = []):

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

    inverted_colors = [get_text_color(x) for x in set_colors]

    positions = np.arange(y_nb)
    arg_sort = np.argsort(y[:, 0])

    low_value = norm.ppf(0.01, 0, 1)
    high_value = (0 - low_value)
    x_distrib = np.linspace(low_value, high_value, points)
    ref_y = norm.cdf(x_distrib, 
                     0, 
                     1)

    ref_y = (ref_y - ref_y[0])
    ref_y *= (1 / ref_y[-1]) # from equation: ref_y[-1] * x = 1

    X = []
    end_ref = np.empty((y_nb, x_nb))

    order = np.argsort(y[:, 0])
    end_ref[order, 0] = np.arange(y_nb)

    ratio_ref = np.empty((y_nb, x_nb))

    for i in range(x_nb - 1):
        cur_x = np.linspace(x[i], x[i+1], points)
        X.append(cur_x)

        cur_col = y[:, i+1]
        order = np.argsort(cur_col)
        end = np.empty_like(order)
        end_ref[order, i+1] = np.arange(y_nb)

        if evolution == Mode.RELATIVE:
            norm_value = y[:, i].max()
        else:
            norm_value = y[:, i].sum()

        for i2 in range(y_nb):
            ratio_ref[i2, i] = y[i2, i] / norm_value

    X = np.concatenate(X)
    X_poly = np.concatenate([X, X[::-1]]) 

    if evolution == Mode.RELATIVE:
        norm_value = y[:, x_nb - 1].max()
    else:
        norm_value = y[:, x_nb - 1].sum()

    for i in range(y_nb):
        ratio_ref[i, x_nb - 1] = y[i, x_nb - 1] / norm_value

    for i2 in range(y_nb):
    
        Y_top = []
        Y_bot = []
  
        inv_color = inverted_colors[i2]

        if len(image_set) >= y_nb:
            x_scale = (x[-1] - x[0])
            size_x_ = x_scale * 0.05
            fig.add_layout_image(
                dict(
                    source=image_set[i2],
                    xref="x",
                    yref="y",
                    x=x[0] + 0.02 * x_scale,
                    y=end_ref[i2, 0],
                    sizex=max(size_x_ * ratio_ref[i2, 0], size_x_ * 0.4),
                    sizey=1,
                    xanchor="left",
                    yanchor="middle",
                    opacity=1
                )
            )

        for i in range(x_nb - 1):
    
            # here, it creates a view, not a copy
            # because no fancy - reorder indexing (same order)
            start = end_ref[:, i]
            end = end_ref[:, i + 1]
    
            ratio_begin = ratio_ref[i2, i]
            ratio_end   = ratio_ref[i2, i+1] 
            ratio = np.linspace(ratio_begin, ratio_end, points)
   
            cur_size = max(ratio_begin * 12, 1) if scale_font else 12

            fig.add_annotation(x = x[i], 
                               y = start[i2], 
                               text=f"{y[i2, i]}",
                               showarrow=False,
                               xanchor="left" if i == 0 else "center",
                               font=dict(color=inv_color, 
                                         size=cur_size)
            )

            delta = end[i2] - start[i2]
            cur_y = start[i2] + delta * ref_y
    
            Y_top.append(cur_y + ratio * 0.5)
            Y_bot.append(cur_y - ratio * 0.5)

        cur_size = max(ratio_end * 12, 1) if scale_font else 12

        fig.add_annotation(x = x[x_nb - 1], 
                           y = end[i2], 
                           text=f"{y[i2, x_nb - 1]}",
                           showarrow=False,
                           xanchor="right",
                           font=dict(color=inv_color, 
                                     size=cur_size)
        )

        Y_top = np.concatenate(Y_top)
        Y_bot = np.concatenate(Y_bot)
    
        # creates a polygon -> fillable
        Y_poly = np.concatenate([Y_top, Y_bot[::-1]])
   
        fig.add_trace(go.Scatter(
            x=X_poly,
            y=Y_poly,
            fill="toself",
            mode="lines",
            line=dict(width=0),
            fillcolor=set_colors[i2],
            showlegend=False,
            opacity=0.8
        ))
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)

years = [2000, 2005, 2010, 2015]

values = np.array([
    [1.2, 1.4, 0.9, 2], 
    [0.1, 3.6, 0.5, 0.95], 
    [2, 3, 1.5, 1.3], 
    [1.7, 1, 3, 1.5], 
    [0.55, 1.95, 1.2, 2.4]
])

fig = go.Figure()

image_set = ["france.png",
             "england.png",
             "italy.png",
             "spain.png",
             "germany.png"]

rubbon_graph(years, 
             values,
             fig,
             evolution=Mode.RELATIVE,
             image_set=image_set)

labels = np.array(["FR", "EN", "IT", "ESP", "GR"])
labels[np.argsort(values[:, 0])] = labels
labels = labels[::-1]

fig.update_yaxes(tickvals=np.arange(len(labels)),
                 ticktext=labels)

fig.write_image("rubbon.pdf")

fig.write_html("rubbon.html")

fig2 = go.Figure()

strt = time.time()

rubbon_graph(years, 
             values,
             fig2,
             evolution=Mode.GLOBAL)

end = time.time()

fig2.write_image("rubbon2.pdf")

fig2.write_html("rubbon2.html")


print(end - strt)


