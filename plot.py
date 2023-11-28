from matplotlib import pyplot as plt
import numpy as np
from pymoo.visualization.scatter import Scatter

plot = Scatter(legend = "True")

result1_array = np.load("./result1.npy")
result2_array = np.loadtxt("./result2.txt")

sort_idx = np.argsort(result1_array[:, 0])

plot.add(result1_array[sort_idx], marker="x", plot_type="line", color="red", alpha=0.7, label="NSGA orginal")
plot.add(result1_array[sort_idx], marker="x", facecolor="none", edgecolor="red", alpha=0.7)

sort_idx = np.argsort(result2_array[:, 0])
plot.add(result2_array[sort_idx], plot_type="line", color="darkblue", alpha=0.7, label="NSGA with TPNA")
plot.add(result2_array[sort_idx], facecolor="none", edgecolor="blue", alpha=0.7)

plot.show()