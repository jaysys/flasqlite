import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def test():
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    line, = ax.plot(x, y, color='k')

    def update(num, x, y, line):
        line.set_data(x[:num], y[:num])
        line.axes.axis([0, 10, 0, 1])
        return line,

    ani = animation.FuncAnimation(fig, update, len(x), fargs=[x, y, line],
                                interval=25, blit=True)
    ani.save('test.gif')
    plt.show()

import plotext as plt
def test2():
    l = 10 ** 4
    y = plt.sin(periods = 2, length = l)

    plt.plot(y)

    plt.xscale("log")    # for logarithmic x scale
    plt.yscale("linear") # for linear y scale
    plt.grid(0, 1)       # to add vertical grid lines

    plt.title("Logarithmic Plot")
    plt.xlabel("logarithmic scale")
    plt.ylabel("linear scale")

    plt.show()

class Todo():
    '''
    DB table
    '''
    id = 324234234234

    def __repr__(self):
        a = '<Task %r>' % self.id
        return a


if __name__ == "__main__":

    test2()

    if False:
        task = Todo()
        print("start!")
        print(task.__repr__())

