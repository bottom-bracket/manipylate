#!/usr/bin/env python3

import numpy as np
from manipylate import ifigure

def x(theta,npts,**kwargs):
    th = np.linspace(1,theta,npts)
    return th/50*np.cos(th)
def y(theta,npts,stretch):
    th = np.linspace(1,theta,npts)
    return -th/50*stretch*np.sin(th)

ifig = ifigure(1,1)
ax = ifig.add_plot(axpos=[0,0],x=x,data=y,parameters=[['theta',1,100,1],['stretch',1,2,0.1],['npts',10,1000,1]],fix_lim=True)
ax.set_ylim(-2,2)
ax.set_xlim(-2,2)
ax.set_aspect('equal')
ifig.show()
