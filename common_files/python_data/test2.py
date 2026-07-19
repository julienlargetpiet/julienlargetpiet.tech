import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data_sales.csv", 
                 sep=",",
                 encoding='latin1')



data["CA_TOTAL"] = data["QUANTITYORDERED"] * data["PRICEEACH"]

print(data.columns)

r_month = data.groupby("MONTH_ID")["CA_TOTAL"]

print(r_month.size())

print("###")

print(type(r_month))


r_month2 = data.groupby("MONTH_ID")["CA_TOTAL"].count()

print(r_month2)
print(type(r_month2))

print("####")

print(data.count())

print("####")


print(data.size)

revenue_detailed = data.groupby(["COUNTRY", "DEALSIZE"])["CA_TOTAL"].sum()


print(revenue_detailed.index)

print("###")

print(revenue_detailed.values)


df_revenue_detailed = revenue_detailed.reset_index() 
print(df_revenue_detailed.head())
print(type(df_revenue_detailed))

#r_month2 = 0.5 * data.groupby("MONTH_ID")["CA_TOTAL"].sum()

#fig, axis = plt.subplots(4, 
#                         2, 
#                         figsize=(15, 15))
#
#axis[0][0].plot(r_month.index,
#                r_month.values,
#                "b*--",
#                r_month2.index,
#                r_month2.values,
#                "b*--")
#
##axis[0][0].plot(r_month2.index,
##                 r_month2.values,
##                 "ro-")
#
#fig.savefig("test2.png")

