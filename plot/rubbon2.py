import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
import colorsys

def generate_colors(n):
    x = np.linspace(0, 256 ** 3, n+2)
    lst = []
    for nb in x[1:len(x) - 2]:
        nb = int(nb)
        hex_clr = f"{nb:06X}"
        lst.append(hex_clr)
    return lst

def generate_colors2(n):
    colors = []
    for i in range(n):
        h = i / n
        r, g, b = colorsys.hsv_to_rgb(h, 0.7, 0.9)
        colors.append(f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}")
    return colors

def rubbon_graph(x, 
                 y, 
                 img_name, 
                 points = 200):

    y_nb = len(y)
    x_nb = len(x)

    set_colors = generate_colors2(y_nb) 

    positions = np.arange(y_nb)
    arg_sort = np.argsort(y[:, 0])

    fig = go.Figure()

    for i in range(0, x_nb - 1, 1):

        cur_col = y[:, i+1]

        start = positions[arg_sort]
        arg_sort = np.argsort(cur_col)
        end = positions[np.argsort(arg_sort)]
        
        max_value = cur_col.max()
        cur_x = np.linspace(x[i], x[i+1], 200)
        
        for i2 in range(y_nb):
       
            ratio = y[i2, i] / max_value
            print(ratio, start[i2], end[i2])
            
            cur_mu = (start[i2] + end[i2]) / 2

            low_value = norm.ppf(0.01, cur_mu, 1)
            high_value = cur_mu + (cur_mu - low_value)
            x_distrib = np.linspace(low_value, high_value, points)

            cur_y = norm.cdf(x_distrib, 
                             cur_mu, 
                             1)

            if end[i2] < start[i2]: 
                cur_y = 1 - cur_y

            cur_color = set_colors[i2]

            fig.add_trace(go.Scatter(
                x=cur_x,
                y=cur_y + ratio * 0.5,
                mode='lines',
                line=dict(width=0, color=cur_color),
                showlegend=False,
            ))

            fig.add_trace(go.Scatter(
                x=cur_x,
                y=cur_y - ratio * 0.5,
                mode='lines',
                line=dict(width=0, color=cur_color),
                fill="tonexty",
                showlegend=False,
            ))

    fig.write_image(img_name)

years = [2000, 2005]

values = np.array([
    [1.2, 1.4], 
    [0.1, 0.6], 
    [2, 3], 
    [2, 1], 
    [0.55, 1.95]
])

rubbon_graph(years, 
            values, 
             "rubbon.pdf")



