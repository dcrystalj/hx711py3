import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('vaga.txt', sep="\t", header=None)
data.columns = ["date", "val", "temp"]

data['val'] = -data['val']
data = data[data['val'] < 50000]

data.plot(x='temp', y='val', kind='scatter')
plt.savefig('graph.png')
