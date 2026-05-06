import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import time
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf
import plotly.graph_objects as go

data = pd.read_csv('data_sales.csv',
                   sep = ",",
                   encoding='latin1')

print(data.head(5))
print(data.dtypes)

data["ORDERDATE"] = pd.to_datetime(data["ORDERDATE"])

print(data.dtypes)

print("")

set_of_columns = data.columns

for cl in data.columns:
    na_nb = sum(data[cl].isna())
    print(f"For the column: {cl}: there are: {na_nb} NA cells")

nb_doublons = sum(data.duplicated(subset=set_of_columns))

print(f"La dataframe contient: {nb_doublons} doublons")

print("Suppression des doublons:")

if nb_doublons:

    data = data.drop_duplicates(subset = set_of_columns)
    
    nb_doublons = sum(data.duplicated(subset=set_of_columns))
    
    print(f"La dataframe contient maintenant: {nb_doublons} doublons")

col_ca = "CA_TOTAL"

print(f"création de la colonne: {col_ca}")

if not col_ca in set_of_columns:
    data[col_ca] = data["QUANTITYORDERED"] * data["PRICEEACH"]

print(data[col_ca])

print("Statistiques descriptives:")

print(data[set_of_columns].describe())

produits = data["PRODUCTLINE"].unique()

data["CA_PAR_PRODUIT"] = data.groupby("PRODUCTLINE")["CA_TOTAL"].transform("sum")

subset_cols = ["PRODUCTLINE", "CA_PAR_PRODUIT"]

print(data[subset_cols].drop_duplicates())

print("graphique barh")

data_top_ventes = (
    data.groupby("PRODUCTLINE")["CA_TOTAL"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

fig, axis = plt.subplots(4, 2,
                      figsize=(15, 15))

fig2, axis2 = plt.subplots(4, 2,
                           figsize=(15, 15))

fig3, axis3 = plt.subplots(4, 2,
                           figsize=(15, 15))

axis[0][0].barh(data_top_ventes.index, data_top_ventes.values)
axis[0][0].invert_yaxis()
axis[0][0].set_title("Total CA / produits - Top 5")
axis[0][0].set_ylabel("Produits")
axis[0][0].set_xlabel("Ventes")

df_top = data_top_ventes.reset_index()
df_top.columns = ["PRODUCTLINE", "CA_TOTAL"] # because of convertion series -> dataframe, we do that to be defensive
sns.barplot(data = df_top,
           y = "PRODUCTLINE",
           x = "CA_TOTAL",
           ax = axis2[0][0])

#axis2[0][0].invert_yaxis() # no need to do that in seaborn, axes already nicely "inverted"
axis2[0][0].set_title("Total CA / produits - Top 5")
axis2[0][0].set_ylabel("Produits")
axis2[0][0].set_xlabel("Ventes")

print("histogramme")

bins_lst = data["SALES"].quantile(np.linspace(0, 1, 11))

print(list(bins_lst))

axis[0][1].hist(data["SALES"], 
             bins = bins_lst, 
             density=True,
             edgecolor="black")

sns.kdeplot(data["SALES"],
            ax=axis[0][1],
            color="red")

sns.histplot(data = data["SALES"],
             stat = "density",
             bins = bins_lst,
             kde = True,
             ax = axis2[0][1]
             )


axis[0][1].set_title("Distribution des SALES")
axis2[0][1].set_title("Distribution des SALES")

ca_mensuel = data.groupby("MONTH_ID")["CA_TOTAL"].sum()
for mnth, ca in ca_mensuel.items():
    print(mnth, ca)

commandes_mensuel = data.groupby("MONTH_ID").count()

print("###")
print(commandes_mensuel)
print(type(commandes_mensuel))


commandes_mensuel = data.groupby("MONTH_ID").size()
commandes_mensuel *= 0.005 * ca_mensuel.mean()
print(type(commandes_mensuel))

# on n'utilise pas count car count va calculer POUR CHAQUE COLONNE, les valeurs non-nulles

print("commandes mensueles index: ", commandes_mensuel.index)
print("commandes mensueles values: ", commandes_mensuel.values)

axis[1][0].plot(commandes_mensuel.index, 
                commandes_mensuel.values, 
                marker="o", 
                color="red")

# et non
#axis[1][0].plot(commandes_mensuel.index, 
#                commandes_mensuel.values, 
#                marker="o", 
#                color="red")
# car sa signature est
#plot(*args, **kwargs)

mois_liste = ["Jan",
              "Feb",
              "Mars",
              "Avr",
              "Mai",
              "Juin",
              "Juil",
              "Aout",
              "Sept",
              "Oct",
              "Nov",
              "Dec"]

axis[1][0].plot(ca_mensuel.index, ca_mensuel.values, marker="*", linestyle="dashed", color="blue")

axis[1][0].plot(commandes_mensuel.index, 
                commandes_mensuel.values, marker="*", linestyle="dashed", color="red")


axis[1][0].set_xticks(ca_mensuel.index, mois_liste)
axis[1][0].set_title("Evolution mensuel du CA et des commandes")

axis2[1][1].plot(ca_mensuel.index, 
                 ca_mensuel.values,
                 "b*--",
                 commandes_mensuel.index,
                 commandes_mensuel.values,
                 "rp-")

axis2[1][1].fill_between(
        ca_mensuel.index,
        ca_mensuel.values,
        commandes_mensuel.values,
        color="gray",
        alpha=0.3
        )

# linestyle
# "-"    # solid
# "--"   # dashed
# "-."   # dash-dot
# ":"    # dotted

# markers:
# "o" → circles
# "*" → stars
# "s" → squares
# "x" → crosses
# "." → tiny dots

ohlc = data.groupby("MONTH_ID")["PRICEEACH"].agg(
    open="first",
    high="max",
    low="min",
    close="last"
).reset_index()

#ohlc.index = pd.to_datetime(ohlc["MONTH_ID"], format="%m")
#ohlc = ohlc.set_index("MONTH_ID")
#
#mpf.plot(ohlc, type="candle")

ohlc_data = [
        (row["MONTH_ID"], row["open"], row["high"], row["low"], row["close"])
        for _, row in ohlc.iterrows()
        ]

candlestick_ohlc(
    axis2[3][1],
    ohlc_data,
    width = 0.6,
    colorup="green",
    colordown="red"
        )

# safe offset that scale with the delta
offset = (max(h for _,_,h,_,_ in ohlc_data) -
          min(l for _,_,_,l,_ in ohlc_data)) * 0.02

for x, open_val, high, low, close_val in ohlc_data:
    low_body = min(open_val, close_val)
    high_body = max(open_val, close_val)

    # label du bas
    axis2[3][1].text(
        x, low_body - offset,
        f"{low_body:.1f}",
        ha="center", va="top", fontsize=8
    )

    # label du haut
    axis2[3][1].text(
        x, high_body + offset,
        f"{high_body:.1f}",
        ha="center", va="bottom", fontsize=8
    )

# ici piège classique bottom = point en dessous du texte -> on ne pense pas en mode coor points -> coor texte != TikZ LaTeX
# mais plutot, le point est en-dessous du texte
# et inversement pour top

x = np.arange(ca_mensuel.shape[0])
y = ca_mensuel.values

x_smooth = np.linspace(0, ca_mensuel.shape[0] - 1, 300)
y_smooth = make_interp_spline(x, y)(x_smooth)

ax = axis[3][1]

ax.plot(x_smooth, y_smooth)
ax.plot(x, y, marker="o", linestyle="none")

ax.set_xticks(x)
ax.set_xticklabels(ca_mensuel.index, rotation=45)



df_ca_mensuel = ca_mensuel.reset_index()
df_ca_mensuel.columns = ["MONTH_ID", "CA_TOTAL"]

sns.lineplot(data = df_ca_mensuel,
             x = "MONTH_ID",
             y = "CA_TOTAL",
             ax = axis2[1][0])

axis2[1][0].set_xticks(ca_mensuel.index, mois_liste)
axis2[1][0].set_title("Evolution mensuel du CA")

data_dealsize = data.groupby("DEALSIZE")["CA_TOTAL"].apply(list)
axis[1][1].boxplot(data_dealsize.values)
# in matplotlib, boxplot ticks starts at 1 lol, design choice
#axis[1][1].set_xticks(range(1, len(data_dealsize) + 1), data_dealsize.index)
# or OLD-API style
axis[1][1].set_xticks(range(1, len(data_dealsize) + 1))
axis[1][1].set_xticklabels(data_dealsize.index)
axis[1][1].set_title("Distribution du CA par DEALSIZE")




corr_vars = ["QUANTITYORDERED", "PRICEEACH", "SALES", "MSRP"]
subset = data[corr_vars]

corr_matrix = subset.corr()
print(corr_matrix)
print(type(corr_matrix)) # technicaly a dataframe

mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

# the cells whose coordiantes corresponding to the 
# mask matrix one and whose values equal to zero won't be shown
#sns.heatmap(
#        data=corr_matrix,
#        mask=mask,
#        annot=True,
#        fmt=".2f",
#        cmap="coolwarm",
#        ax=axis[2][0]
#        )
#
#axis[2][0].set_title("Correlation matrix")

rng = np.random.default_rng(42)

heat_time = np.array([
    rng.standard_normal(4),
    rng.standard_normal(4),
    rng.standard_normal(4)
    ])

xlb = ["t1", "t2", "t3", "t4"]
ylb = ["A", "B", "C"]

#sns.heatmap(
#    heat_time.T,
#    xticklabels = ylb,
#    yticklabels = xlb,
#    cmap="inferno",
#    annot=True,
#    fmt=".2f",
#    ax=axis[2][0]
#)

## difference wth raw matpotlib

im = axis[2][0].imshow(heat_time.T, cmap="inferno")

axis[2][0].set_xticks(np.arange(len(ylb)))
axis[2][0].set_yticks(np.arange(len(xlb)))

axis[2][0].set_xticklabels(ylb)
axis[2][0].set_yticklabels(xlb)

axis[2][0].set_xlabel("Time")
axis[2][0].set_ylabel("Variables")

for i in range(heat_time.T.shape[0]):
    for j in range(heat_time.T.shape[1]):
        axis[2][0].text(
                j,
                i,
                f"{heat_time.T[i, j]:.2f}",
                ha="center",
                va="center",
                color=(0, 0, 1, 1) # or "blue", you see here rgba like but instead of 0-255, it is 0-1 scale
                )

axis[2][0].xaxis.tick_top()
axis[2][0].xaxis.set_label_position("top")

axis[2][0].invert_xaxis()

order = (
         data.groupby("PRODUCTLINE")["PRICEEACH"]
        .median()
        .sort_values()
        .index
)

print("order:", order)

#sns.violinplot(data=data, 
#               y="PRODUCTLINE", 
#               x="PRICEEACH",
#               order=order,
#               ax=axis[2][1])

## or with atplotlib

groups = [data[data["PRODUCTLINE"]==cat]["PRICEEACH"] for cat in order]

axis[2][1].violinplot(groups, vert=False)

axis[2][1].set_yticks(range(1, len(order) + 1)) # violinplot starts at 1
axis[2][1].set_yticklabels(order)

axis[2][1].set_ylabel("PRODUCTLINE")
axis[2][1].set_xlabel("PRICEEACH")

axis[2][1].set_title("Distribution des prix par PRODUCTLINE")

mean_price = (
        data.groupby("PRODUCTLINE")["PRICEEACH"]
        .mean()
        .loc[order]
        )

axis2[2][0].pie(
        x = mean_price.values,
        labels = mean_price.index,
        autopct = "%1.1f%%"
        )

axis[2][1].set_title("Moyenne des PRICEEACH par PRODUCTLINE")

ca_detailed = data.groupby(["COUNTRY", "DEALSIZE"])["CA_TOTAL"].sum()

print("#####")
print(type(ca_detailed))
cur_country = None

for (country, dealsize), ca in ca_detailed.items(): 
    if country != cur_country:
        cur_country = country
        print(f"--- Country: {country} --- ")
    print(f"Dealsize: {dealsize} - CA: {ca}")


df_ca_detailed = ca_detailed.reset_index() # créer un df avec les items de index comme colonne
print(df_ca_detailed.head())
print(type(df_ca_detailed))


# ites is the pair (index, values), it is why here i break down the 
# index into (country, dealsize), because the entire thin is the ke / index


sns.barplot(data=data,
            y="COUNTRY",
            x="CA_TOTAL",
            hue="DEALSIZE",
            errorbar=None, # no uncertainty, because that is deterministic compute in that case
            ax=axis[3][0])

sns.violinplot(data=data, 
               y="PRODUCTLINE", 
               x="PRICEEACH",
               order=order,
               ax=axis2[2][1])

axis2[2][1].set_title("Distribution des prix par PRODUCTLINE")

mois = np.arange(1, 7)

#produit_A = np.array([10, 15, 20, 25, 30, 35])
#produit_B = np.array([5, 10, 15, 20, 25, 30])
#produit_C = np.array([2, 5, 10, 15, 20, 25])

produit_A = np.array([10, 18, 14, 22, 19, 27])
produit_B = np.array([5, 7, 12, 9, 15, 10])
produit_C = np.array([3, 6, 4, 8, 7, 12])

axis2[3][0].stackplot(
        mois,
        produit_A,
        produit_B,
        produit_C,
        labels = ["Produit A", "Produit B", "Produit C"]
        )

axis2[3][0].set_title("Ca mensuel empilé par produit")
axis2[3][0].set_xlabel("Mois")
axis2[3][0].set_ylabel("CA")

axis2[3][0].legend(loc="upper left")

print(data[["QUANTITYORDERED", "PRICEEACH"]].head(5))

# this one is particular, contrary to other seaborn figures like violiplot
# this one does not accept ax, it creates its own figure / environment
# the figures that act like this are:

# jointplot
# displot
# relplot
# catplot
# pairplot
# lmplot

# if it builds multiple plots -> own figure

j_plot = sns.jointplot(
             data=data,
             x = "QUANTITYORDERED",
             y = "PRICEEACH",
             kind="scatter"
)

j_plot.figure.savefig("j_plot.png")

pair_plot = sns.pairplot(data=subset)
pair_plot.figure.savefig("pair_plot.png",
                         dpi=300)

displot_hist = sns.displot(data = data, 
                           x = "PRICEEACH",
                           kind="hist")
displot_hist.figure.savefig("displot_hist.png")

displot_kde = sns.displot(data = data, 
                          x = "PRICEEACH",
                          kind="kde")
displot_kde.figure.savefig("displot_kde.png")

displot_ecdf = sns.displot(data = data, # CDF
                           x = "PRICEEACH",
                           kind="ecdf")
displot_ecdf.figure.savefig("displot_ecdf.png")

values = data["PRICEEACH"].to_numpy()

q1 = np.percentile(values, 25)
q3 = np.percentile(values, 75)

bandwidth = 0.9 * min(np.std(values),  (q3 - q1)/ 1.34) * data.shape[0] ** (-1/5) # Silverman's rule
print("bandwidth: ", bandwidth)

xmin = values.min() - 4 * bandwidth
xmax = values.max() + 4 * bandwidth

x_pts = np.linspace(xmin, xmax, 200)

y_pts = []

# here we have to choose a balanced bandwidth, if too high -> too smooth 
# / loses structure / under fitting, if to small -> overfitting
#bandwidth = 4 

for x in x_pts:
    y = 0
    for xi in values:
        y += np.exp(-0.5 * ((x - xi) / bandwidth)**2)
    y_pts.append(y)

y_pts = np.array(y_pts)
y_pts /= (bandwidth * np.sqrt(2 * np.pi)) # normalisation
y_pts /= data.shape[0]

axis3[0][0].plot(x_pts,
                 y_pts,
                 color="red")

cdf_p = 0
y_cdf = []

dx = x_pts[1] - x_pts[0]

#for i in range(len(y_pts)):
#    cdf_p += (y_pts[i] * x_spacing)
#    y_cdf.append(cdf_p)

y_cdf = np.cumsum(y_pts) * dx

axis3[0][1].plot(x_pts,
                 y_cdf,
                 color="red")

axis3[0][1].set_title("PRICEEACH CDF")

print("CDF max: ", y_cdf[-1])

print(x_pts[56], x_pts[57])
print("mean:", (x_pts[56] + x_pts[57]) / 2)

# Now, to approx a CDf at a not computed CDF point, we do:
# For example for points between 56 and 57:

print("CDF point: ", y_cdf[56] + (dx / 2) * ((y_pts[56] + y_pts[57]) / 2))

# ou alors, moyenne de l'aire entre point 56 et 57, ce qui se rapproche plus des data réelles
# car la premiière méthode fait le parie que l'acrt de y_56 et y_57 est plutôt linéaire

print("CDF point (other method): ", (y_cdf[56] + y_cdf[57]) / 2)

# that is:
# integrating a rougher function (PDF)
# vs
# interpolating a smoother one (CDF)

relplot_fig = sns.relplot(data=data,
                         x="QUANTITYORDERED",
                         y="PRICEEACH",
                         hue="PRODUCTLINE",
                         kind="scatter")

relplot_fig.savefig("relplot.png")

relplot_fig = sns.relplot(data=data,
                         x="QUANTITYORDERED",
                         y="PRICEEACH",
                         hue="SALES",
                         kind="scatter")

relplot_fig.savefig("relplot2.png")

relplot_fig = sns.relplot(data=data,
                         x="QUANTITYORDERED",
                         y="PRICEEACH",
                         col="PRODUCTLINE",
                         hue="SALES",
                         style="COUNTRY",
                         size="DEALSIZE",
                         kind="scatter")

relplot_fig.savefig("relplot3.png")

relplot_fig = sns.relplot(data=data,
                         x="QUANTITYORDERED",
                         y="PRICEEACH",
                         col="PRODUCTLINE",
                         hue="DEALSIZE",
                         style="COUNTRY",
                         size="SALES",
                         kind="scatter")

relplot_fig.savefig("relplot4.png")

# the area we see around the line may appear if multipl y per x, it is the uncertainty value
# here the uncertainty value is:
# U = std(y values for for a x) / sqrt(n) * 1.96
# then we plot mean(ys) AND top area is mean(ys) + U AND bottom area is mean(ys) - U
# That is sample mean and centra limit theorem, the spread of the sampe means folow a Normal distribution of N(u, std**2/n)
# And in normal distribution, we got Value at Qn = u + std * Value at Qn for N(0, 1)
# here std is replaced by the std of the sample means --> std / sqrt(n)
relplot_fig = sns.relplot(data=data,
                         x="QUANTITYORDERED",
                         y="PRICEEACH",
                         kind="line")

relplot_fig.savefig("relplot5.png")


# catplot when x is categorical
catplot = sns.catplot(data=data,
                      x = "PRODUCTLINE",
                      y = "PRICEEACH",
                      kind="strip",
                      hue="COUNTRY"
                      )
catplot.savefig("catplot.png")

#catplot = sns.catplot(data=data,
#                      x = "PRODUCTLINE",
#                      y = "PRICEEACH",
#                      kind="swarm",
#                      hue="COUNTRY"
#                      )
#catplot.savefig("catplot2.png")

catplot = sns.catplot(data=data,
                      x = "PRODUCTLINE",
                      y = "PRICEEACH",
                      kind="box",
                      hue="COUNTRY"
                      )
catplot.savefig("catplot3.png")

catplot = sns.catplot(data=data,
                      x = "PRODUCTLINE",
                      y = "PRICEEACH",
                      kind="box",
                      )
catplot.savefig("catplot4.png")

catplot = sns.catplot(data=data,
                      x = "PRODUCTLINE",
                      y = "PRICEEACH",
                      kind="boxen",
                      )
catplot.savefig("catplot5.png")

catplot = sns.catplot(data=data,
                      x = "PRODUCTLINE",
                      y = "PRICEEACH",
                      kind="point",
                      )
catplot.savefig("catplot6.png")

catplot = sns.catplot(data=data,
                      x = "PRODUCTLINE",
                      y = "PRICEEACH",
                      kind="bar",
                      )
catplot.savefig("catplot7.png")

# closing a figure -> free some memory
plt.close(catplot.fig)

lmplot = sns.lmplot(data=data,
            x = "QUANTITYORDERED",
            y = "PRICEEACH",
            hue="DEALSIZE")

lmplot.savefig("lmplot.png")

plt.close(lmplot.fig)

lmplot = sns.lmplot(data=data,
            x = "QUANTITYORDERED",
            y = "PRICEEACH",
            col="DEALSIZE")

lmplot.savefig("lmplot2.png")


fig.tight_layout()
fig.savefig("pic2.png", dpi = 100)

fig2.tight_layout()
fig2.savefig("pic3.png", dpi = 100)

fig3.tight_layout()
fig3.savefig("pic4.png", dpi = 100)



