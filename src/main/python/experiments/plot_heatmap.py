import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
fix, ax = plt.subplots()
#data = np.loadtxt(open("10by10.csv","r"),delimiter=",",skiprows=1,index_col=0)
data = pd.read_csv(open("10by10.csv","r"), index_col=0)
#data = data.sort("Utah", ascending=True)
x_labels = ["ACM EC","AU","GMU","KSU","LSU","PDX","RPI","SC","Stanford","Utah","UTK"]
y_labels = x_labels
heatmap = ax.pcolor(data, cmap=plt.cm.Blues, alpha=0.8)
fig = plt.gcf()
fig.set_size_inches(10,10)
ax.set_frame_on(False)
ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)
ax.set_xticks(np.arange(data.shape[1]) + 0.5, minor=False)
ax.invert_yaxis()
ax.xaxis.tick_top()
ax.set_xticklabels(x_labels, minor=False)
ax.set_yticklabels(data.index, minor=False)
ax.grid(False)
plt.xticks(rotation=90)
ax = plt.gca()
for t in ax.xaxis.get_major_ticks():
    t.tick1On = False
    t.tick2On = False
for t in ax.yaxis.get_major_ticks():
    t.tick1On = False
    t.tick2On = False
plt.tight_layout(pad=4, w_pad=4, h_pad=4)
plt.show()
