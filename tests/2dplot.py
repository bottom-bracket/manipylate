#!/usr/bin/env python3

import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import manipylate
from manipylate import ifigure



x = np.linspace(-5, 5, 200)
y = np.linspace(-3, 3, 100)
z = np.linspace(-4, 4, 80)
X, Y ,Z = np.meshgrid(x, y, z,indexing='ij')
data = np.sinc(X * Y**2 * Z**3)

ifig=ifigure(1,1,figurename='./tmp/2dplot.png')

ifig.add_plot(axpos=[0,0],x=[x,y],data=data,parameters=['x'],plot_ax=[0,1])
ifig.show()
