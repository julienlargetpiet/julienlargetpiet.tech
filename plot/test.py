import matplotlib.pyplot as plt
import matplotlib

#matplotlib.use('Qt5Agg')

x = {"B": 1, 
     "C": 2, 
     "D": 3, 
     "E": 4, 
     "F": 5, 
     "G": 14}

y = {"B2": 23, 
     "C2": 12, 
     "D2": 45, 
     "E2": 11, 
     "F2": 7, 
     "G2": 33}


x_values = list(x.values())   
x_labels = list(x.keys())       

y_values = list(y.values())   
y_labels = list(y.keys())       

fig, axes = plt.subplots(1, 
                         2, 
                         figsize=(10, 5)) # width, height

axes[0].plot(x_values, y_values)
axes[0].set_xticks(x_values, x_labels)
axes[0].set_yticks(y_values, y_labels)
axes[0].set_title("title grph1")
axes[0].set_xlabel("Letters instead of numbers")
axes[0].set_ylabel("Y")

axes[1].bar(x_values, y_values)
axes[1].set_xticks(x_values, x_labels)

plt.title("TITLE")

axes[1].set_title("title grph2")

plt.tight_layout()

plt.savefig("pic.png", 
            dpi=100) # pixel scale of dimensions (cf: figsize)



