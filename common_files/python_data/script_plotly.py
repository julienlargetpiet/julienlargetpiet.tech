import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde
import copy

fig1 = go.Figure()
fig1.add_trace(
    go.Scatterpolar(
        r=[3, 3, 2, 4, 1.5, 1, 2, 3],
        theta=["A", "B", "C", "D", "E", "F", "G", "H"],
        fill="toself"
    )
)

fig2 = go.Figure()
fig2.add_trace(
    go.Bar(y=[2, 3, 1])
)

fig8 = go.Figure()
fig8.add_trace(
    go.Bar(x=[2, 3, 1],
           orientation="h")
)

colors = ["#1f77b4", "#ff7f0e"]

fig6 = go.Figure()
fig6.add_trace(go.Bar(
    name="Produit A",
    x=["Jan", "Feb", "Mar"],
    y=[2, 3, 1],
    marker=dict(color=["red", "green", "blue"])
))

fig6.add_trace(go.Bar(
    name="Produit B",
    x=["Jan", "Feb", "Mar"],
    y=[1, 4, 2],
    marker=dict(color=colors[1])
))

fig6.update_layout(barmode="group")


df_ca_detailed = pd.DataFrame({
    "COUNTRY": ["FR", "FR", "FR", "EN", "EN", "IT", "IT", "IT"],
    "DEALSIZE": ["LARGE", "LARGE", "SMALL", "MEDIUM", "SMALL", "LARGE", "SMALL", "MEDIUM"],
    "CA_TOTAL": [10, 8, 4, 5, 3, 12, 1, 6]  
})


fig3 = px.sunburst(
    df_ca_detailed,
    path=["COUNTRY", "DEALSIZE"],
    values="CA_TOTAL"
)

fig4 = go.Figure()

fig4.add_trace(go.Scatter(
    x=["a", "b", "c"],
    y=[1, 2, 3],
    mode="lines+markers",
    name="Dataset A",
    line=dict(dash="dash", color="red", shape="spline"),
    marker=dict(symbol="star", color="red", size=10)
))

fig4.add_trace(go.Scatter(
    x=["a", "b", "c"],
    y=[2, 0.78, 3.1],
    mode="lines+markers",
    name="Dataset B",
    line=dict(dash="dash", color="blue", shape="spline"),
    marker=dict(symbol="circle", color="blue", size=10),
    fill="tonexty",
    fillcolor="rgba(0, 0, 255, 0.2)"
))

fig4.update_layout(title=dict(text="sample figure",
                              x = 0.5,
                              xanchor="center",
                              font=dict(size=24)),

                   xaxis = dict(title="X axis",
                                tickfont=dict(size=16),
                                title_font=dict(size=16)),

                   yaxis = dict(title="Y axis",
                                tickfont=dict(size=12),
                                title_font=dict(size=16))

                   )

fig5 = go.Figure()

fig5.add_trace(go.Scatter(
    x=["a", "a", "c"],
    y=[1, 2, 3],
    mode="markers",
    name="Dataset",
    showlegend=True,
    marker=dict(symbol="star", color="blue", size=10)
))

fig5.update_layout(
    legend=dict(
        title="My legend",
        x=1.2, y=1,
        xanchor="right",
        yanchor="top",
        )
)

fig7 = go.Figure()

fig7.add_trace(go.Indicator(
    mode="gauge+number",
    value=65,
    title=dict(text = "Performance"),
    gauge=dict(axis = {"range": [0, 100]})
))

data = np.random.normal(loc=0, scale=1, size=1000)
quantile_data = np.quantile(data, np.linspace(0, 1, 25))

fig9 = go.Figure()
fig9.add_trace(
    go.Histogram(x=data, nbinsx=25,
                histnorm = "probability density",
                marker=dict(color="lightblue",
                            line=dict(color="black", width=0.5))
                 )
    )

x_vals = np.linspace(min(data), max(data), 200)
bandwidth = 0.3

y_vals = []

for x in x_vals:
    y = 0
    for xi in data:
        y += np.exp(-0.5 * ((x - xi) / bandwidth)**2)
    y_vals.append(y)

y_vals = np.array(y_vals)
y_vals /= (bandwidth * np.sqrt(2 * np.pi)) # normalisation
y_vals /= len(data) # normalization complete -> because we sumed out al the kernels, but KDE is the ean of all the kernels


fig9.add_trace(
    go.Scatter(
        x = x_vals,
        y = y_vals,
        mode="lines",
        line=dict(color="red")
        )
    )

# or with gaussian_kde from scipy.stats
kde = gaussian_kde(data)
y_vals2 = kde(x_vals)

fig9.add_trace(
    go.Scatter(
        x = x_vals,
        y = y_vals2,
        mode="lines",
        line=dict(color="blue")
        )
    )

fig10 = go.Figure()
fig10.add_trace(
        go.Pie(
            labels = ["A", "B", "C"],
            values=[15, 10, 55],
            marker=dict(colors=["red", "blue", "green"])
            )
        )

fig11 = go.Figure()
fig11.add_trace(
        go.Pie(
            labels = ["A", "B", "C"],
            hole=0.4,
            values=[15, 10, 55],
            marker=dict(colors=["red", "blue", "green"])
            )
        )

fig11.update_layout(
    annotations=[dict(
        text="Total",
        x=0.5, y=0.5,
        font_size=20,
        showarrow=False
    )]
)

data = dict(
    category=["A", "A", "B", "B", "C"],
    subcategory=["A1", "A2", "B1", "B2", "C1"],
    value=[10, 20, 15, 25, 30]
)

fig12 = px.treemap(
    data,
    path=["category", "subcategory"],
    values="value"
)

fig13 = go.Figure()

fig13.add_trace(
        go.Box(y = np.random.normal(0, 1, 1000), 
               name="A"
               )    
    )

fig13.add_trace(
        go.Box(y = np.random.normal(0, 1.5, 1000), 
               name="B"
               )    
    )

fig13.add_trace(
        go.Box(y = np.random.normal(-0.5, 1.1, 1000), 
               name="C",
               marker=dict(color="purple"),
               line=dict(color="black")
               )    
    )

fig14 = go.Figure()

fig14.add_trace(
        go.Box(x = np.random.normal(0, 1, 1000), 
               name="A"
               )    
    )

fig14.add_trace(
        go.Box(x = np.random.normal(0, 1.5, 1000), 
               name="B"
               )    
    )

fig14.add_trace(
        go.Box(x = np.random.normal(-0.5, 1.1, 1000), 
               name="C",
               marker=dict(color="purple"),
               line=dict(color="black")
               )    
    )

data = {
    "A": np.random.normal(0, 1, 500),
    "B": np.random.normal(1, 1.5, 500),
    "C": np.random.normal(-1, 0.5, 500)
}

fig15 = go.Figure()

for key, values in data.items():
    fig15.add_trace(go.Violin(
        y=values,
        name=key,
        box_visible=True,      # mini boxplot inside
        meanline_visible=True  # moyenne
    ))

fig16 = go.Figure()

for key, values in data.items():
    fig16.add_trace(go.Violin(
        x=values,
        name=key,
        box_visible=True,      # mini boxplot inside
        meanline_visible=True  # moyenne
    ))

fig17 = go.Figure()
fig17.add_trace(
        go.Waterfall(x = ["start", "Sales", "Returns", "Profit"],
                     y = [100, 50, -20, 0],
                     measure = ["absolute", "relative", "relative", "total"],
                     increasing = dict(marker=dict(color="green")),  # very inconsistent to just marker=dict(colors=[...])
                     decreasing = dict(marker=dict(color="red")),
                     totals = dict(marker=dict(color="blue"))
                     )
    )

fig21 = go.Figure()
fig21.add_trace(
        go.Waterfall(x = ["start", "Sales", "Returns", "Profit", "Taxes-1", "Taxes-2", "Final Profit"],
                     y = [100, 50, -20, 0, -3, -5, 0],
                     measure = ["absolute", "relative", "relative", "total", "relative", "relative", "total"],
                     increasing = dict(marker=dict(color="green")),  # very inconsistent to just marker=dict(colors=[...])
                     decreasing = dict(marker=dict(color="red")),
                     totals = dict(marker=dict(color="blue"))
                     )
    )


fig18 = go.Figure()
fig18.add_trace(
        go.Funnel(x = [100, 80, 55, 32],
                  y = ["Visitors", "Signup", "Trials", "Purchases"],
                  marker=dict(color=["blue", "purple", "yellow", "green"])
                  )
    )

#fig19 = go.Figure()
#fig19.add_trace(
#        go.Funnel(y = [100, 80, 55, 32],
#                  x = ["Visitors", "Signup", "Trials", "Purchases"])
#    )

x = np.arange(1, 7)

y1 = np.array([10, 18, 14, 22, 19, 27])
y2 = np.array([5, 7, 12, 9, 15, 11])
y3 = np.array([3, 6, 4, 8, 7, 10])

fig20 = go.Figure()

fig20.add_trace(
        go.Scatter(x = x,
                   y = y1,
                   mode="lines",
                   name="A",
                   stackgroup="one")
    )

fig20.add_trace(
        go.Scatter(x = x,
                   y = y2,
                   mode="lines",
                   name="B",
                   stackgroup="one")
    )

fig20.add_trace(
        go.Scatter(x = x,
                   y = y3,
                   mode="lines",
                   name="C",
                   stackgroup="one")
    )

fig22 = go.Figure()
fig22.add_trace(go.Ohlc(
            x = ["2022-03-01", "2022-03-02", "2022-03-03"],
            open = [10, 11, 14],
            high = [15, 14, 16],
            low = [8, 9, 5],
            close = [12, 13, 9]
        )
    )

fig22.update_layout(
    title="OHLC Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False
)

fig23 = go.Figure()
fig23.add_trace(go.Candlestick(
            x = ["2022-03-01", "2022-03-02", "2022-03-03"],
            open = [10, 11, 14],
            high = [15, 14, 16],
            low = [8, 9, 5],
            close = [12, 13, 9]
        )
    )

fig23.update_layout(
    title="candlestick Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False
)
fig23.update_layout(template="plotly_dark")

#>>> import plotly.io as pio
#>>> pio.templates
#Templates configuration
#-----------------------
#    Default template: 'plotly'
#    Available templates:
#        ['ggplot2', 'seaborn', 'simple_white', 'plotly',
#         'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
#         'ygridoff', 'gridon', 'none']

# 🎨 Colors
# default trace colors
# color palettes
# background color
# 🧱 Layout
# grid visibility & style
# axis lines & ticks
# plot background / paper background
# 🔤 Text & fonts
# font family
# font size
# title styling
# 📏 Lines & markers
# default line width
# marker style
# opacity (sometimes via defaults)
# 📊 Trace defaults
# 
# Each chart type gets default styling:
# 
# bar colors
# scatter marker size
# histogram fill

x = ["t1", "t2", "t3", "t4"]
y = ["A", "B", "C"]

z = np.array([
            np.random.normal(0, 1, 4), 
            np.random.normal(1, 1, 4),
            np.random.normal(0, 2, 4)           
            ])

fig24 = go.Figure()
fig24.add_trace(
    go.Heatmap(x = x,
               y = y,
               z = z,
               colorscale="Inferno",
               text=z,
               texttemplate="%{text:.2~f}", # shows up to 2 decimal, .2f -> always shows 2 decimal
               textfont=dict(size=12)
))

fig24.update_layout(title="Heatmap over time", 
                    xaxis_title="time", 
                    yaxis_title="Variable")

fig25 = go.Figure()
fig25.add_trace(
    go.Heatmap(x = y,
               y = x,
               z = z.T,
               colorscale="Inferno",
               text=z.T,
               texttemplate="%{text:.2~f}", # shows up to 2 decimal, .2f -> always shows 2 decimal
               textfont=dict(size=12)
))

fig25.update_layout(title="Heatmap over time", 
                    xaxis=dict(title="Time", side="top"), 
                    yaxis=dict(title="Variable", autorange="reversed"))

# better to reverse in plotly compared to doing it manually

z_data_reversed = z.T[::-1, :]

fig26 = go.Figure()
fig26.add_trace(
    go.Heatmap(x = y,
               y = x[::-1],
               z = z_data_reversed,
               colorscale="Inferno",
               text=z_data_reversed,
               texttemplate="%{text:.2~f}", # shows up to 2 decimal, .2f -> always shows 2 decimal
               textfont=dict(size=12)
))

fig26.update_layout(title="Heatmap over time", 
                    xaxis=dict(title="Time", side="top"), 
                    yaxis=dict(title="Variable"))

fig26.add_annotation(
        x="B", 
        y = "t2", 
        text="This is an annotation", 
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        bgcolor="yellow",
        font=dict(size=16, color="black"),
        bordercolor="black",
        borderwidth=1,
        borderpad=4
        )

x = np.random.randn(100) # équivalent à np.random.normal(0, 1, 100)
y = np.random.randn(100) 
z = np.random.randn(100) 

fig27 = go.Figure()
fig27.add_trace(
    go.Scatter3d(
        x = x,
        y = y,
        z = z,
        mode="markers",
        marker=dict(size=4, color=z, colorscale="Inferno")
    )
)

z = np.random.rand(20, 20) # np.random.rand(N1, N2) -> N1 listes contenant N2 valeurs -> on encode la valeur de x et y pour un point en tant que la position de ce point dans la structure de données, sa valeur de z étant juste la valeur de ce point en z[y][x] = z

fig28 = go.Figure()
fig28.add_trace(
    go.Surface(
        z = z,
    )
)

fig28.update_layout(
    scene=dict(
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
                )
            )
)

fig29 = copy.deepcopy(fig28)

fig29.update_layout(
    scene=dict(
            camera=dict(
                eye=dict(x=0, y=0, z=1.5)
                )
            )
)

fig30 = copy.deepcopy(fig28)

fig30.update_layout(
    scene=dict(
            camera=dict(
                eye=dict(x=1.5, y=0, z=0)
                )
            )
)

fig31 = copy.deepcopy(fig28)

fig31.update_layout(
    scene=dict(
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=0)
                )
            )
)

# 3D mental model

# camera position (eye)
#         ↓
# vector toward center (target)
#         ↓
# projection onto screen

#fig1.write_image("plotly1.png")
#fig2.write_image("plotly2.png")
#fig3.write_image("plotly3.png")
#fig4.write_image("plotly4.png")
#fig5.write_image("plotly5.png")
#fig6.write_image("plotly6.png")
#fig7.write_image("plotly7.png")
#fig8.write_image("plotly8.png")
#fig9.write_image("plotly9.png")
#fig10.write_image("plotly10.png")
#fig11.write_image("plotly11.png")
#fig12.write_image("plotly12.png")
#fig13.write_image("plotly13.png")
#fig14.write_image("plotly14.png")
#fig15.write_image("plotly15.png")
#fig16.write_image("plotly16.png")
#fig17.write_image("plotly17.png")
#fig18.write_image("plotly18.png")
##fig19.write_image("plotly19.png")
#fig20.write_image("plotly20.png")
#fig21.write_image("plotly21.png")
#fig22.write_image("plotly22.png")
#fig23.write_image("plotly23.png")

fig1.write_image("plotly1.pdf")
fig2.write_image("plotly2.pdf")
fig3.write_image("plotly3.pdf")
fig4.write_image("plotly4.pdf")
fig5.write_image("plotly5.pdf")
fig6.write_image("plotly6.pdf")
fig7.write_image("plotly7.pdf")
fig8.write_image("plotly8.pdf")
fig9.write_image("plotly9.pdf")
fig10.write_image("plotly10.pdf")
fig11.write_image("plotly11.pdf")
fig12.write_image("plotly12.pdf")
fig13.write_image("plotly13.pdf")
fig14.write_image("plotly14.pdf")
fig15.write_image("plotly15.pdf")
fig16.write_image("plotly16.pdf")
fig17.write_image("plotly17.pdf")
fig18.write_image("plotly18.pdf")
#fig19.write_image("plotly19.png")
fig20.write_image("plotly20.pdf")
fig21.write_image("plotly21.pdf")
fig22.write_image("plotly22.pdf")
fig23.write_image("plotly23.pdf")
fig24.write_image("plotly24.pdf")
fig25.write_image("plotly25.pdf")
fig26.write_image("plotly26.pdf")
fig27.write_image("plotly27.pdf")
fig28.write_image("plotly28.pdf")
fig29.write_image("plotly29.pdf")
fig30.write_image("plotly30.pdf")
fig31.write_image("plotly31.pdf")





