# Jain Jai Sandeep - 2017A7PS1585H
# Prateek Hiranandani - 2017B4A70578H
# Sahil Nair - 2017B5A71317H
# Jatin Arora - 2018A7PS0551H
# Rusabh Rakesh Parikh - 2018A7PS1217H

import matplotlib.pyplot as plt
import seaborn as sns

plt.rc("font", size=14)
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)

x_axis = [10, 20, 30, 40, 50, 60, 70, 80, 90]
y_axis = [

    175335.341,
    108598.595,
    80377.3173,
    54453.2230,
    38959.1231,
    27199.8231,
    11391.5725,
    9787.32988,
    5023.36392

]

plt.plot(x_axis, y_axis)
plt.xlabel('Packet Loss (per cent)')
plt.ylabel('Throughput (bytes/sec)')
plt.title('Throughput Vs Packet Loss')
plt.savefig('./graphs/Throughput Vs Packet Loss.jpg', bbox_inches='tight', dpi=300)
