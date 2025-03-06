#!/usr/bin/env python
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

data = pd.read_csv("energies_out.csv", skipinitialspace=True)
sns.relplot(data=data, x="i", y="energy", row="method", col="basis", hue="core")
plt.savefig("energies.pdf", transparent=True)
plt.show()
