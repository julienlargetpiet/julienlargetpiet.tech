import plotly.graph_objects as go

years = [2000, 2005]

# Baseline (e.g. starting GDP or reference level)
baseline = [1.2, 0.1, 2, 0.2, 0.55]

# Growth over time (can go up or down)
growth = [0.2, 0.5, 1.0, 0.8, 1.4]

# Top of ribbon = baseline + growth
top = [b + g for b, g in zip(baseline, growth)]

fig = go.Figure()

# Top line

for i in range(len(top)):

    fig.add_trace(go.Scatter(
        x=years,
        y=[baseline[i], top[i]],
        mode='lines',
        line=dict(width=2),
        showlegend=True
    ))

# Baseline + fill → ribbon thickness = growth
#fig.add_trace(go.Scatter(
#    x=years,
#    y=baseline,
#    mode='lines',
#    fill='tonexty',
#    fillcolor='rgba(0,200,100,0.3)',
#    line=dict(width=0),
#    name='Growth band'
#))

fig.update_layout(
    title="Ribbon = Growth from Baseline",
    xaxis_title="Year",
    yaxis_title="Value"
)

fig.write_image("rubbon.pdf")



