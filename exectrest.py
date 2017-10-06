import matplotlib.pyplot as plt

fig1, ax = plt.subplots()
ax.plot(range(10))

fig2 = plt.figure()
fig2.axes.append(ax)

fig1.show()
input('dsfas')