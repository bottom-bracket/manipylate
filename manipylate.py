#!/usr/bin/env python3

#
###############################################################################
# The MIT License (MIT)

# Copyright (c)  2022 Philip Heringlake

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
###############################################################################


import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
from matplotlib.widgets import Slider
from matplotlib.gridspec import GridSpec,GridSpecFromSubplotSpec


slider_height_inches = 0.1

class lineplot(object):
    """Single line plot instance
    """

    def __init__(self, ax, x, data, variables,**kwargs):
        """
        
        Arguments:
        - `ax`: axis instance
        - `x`: x values
        - `data`: data array to be sliced
        - `variables`: dimension variables (len = ndim-1)
        - `plotax` (0): plot which dimension of array (axis)
        """
        self._ax = ax
        self._data = data
        self._dimvar = {}
        self._variables=variables

        if len(data.shape)-1 != len(variables):
            raise(Exception("not enough dimension variables "))

        self._vnames= [v.name for v in variables]
        for v in variables:
            self._dimvar[v.name]=v

        self.line, = self._ax.plot(x, self.get_line(),**kwargs)

    def get_line(self):
        idx = tuple([v.value for v in self._variables])
        ldat = self._data[idx]
        return ldat

    def vchanged(self):
        for v in self._variables:
            if v.changed():
                return True
        return False

    def plot(self):
        if self.vchanged():
            self.line.set_ydata(self.get_line())
            self._ax.relim()
            self._ax.autoscale_view()
        return
            
class plot2d(object):
    """
    """

    def __init__(self, ax, x, y, data, variables,**kwargs):
        """
        
        Arguments:
        - `ax`:
        - `x`:
        - `y`:
        - `data`:
        - `variables`:
        - `**kwargs`:
        """
        self._ax = ax
        self._x = x
        self._y = y
        self._data = data
        self._variables = variables
        self._dimvar = {}
        
        if len(data.shape)-2 != len(variables):
            raise(Exception("not enough or too many dimension variables "))

        self._vnames= [v.name for v in variables]
        for v in variables:
            self._dimvar[v.name]=v

        if not 'origin' in kwargs:
            kwargs['origin']='lower'
        self.im = self._ax.imshow(self.get_map(),extent=[x.min(),x.max(),y.min(),y.max()],**kwargs)

    def get_map(self):
        idx = tuple([v.value for v in self._variables])
        ldat = self._data[idx]
        return ldat

    def vchanged(self):
        for v in self._variables:
            if v.changed():
                return True
        return False

    def plot(self):
        if self.vchanged():
            self.im.set_data(self.get_map())
            self._ax.relim()
            self._ax.autoscale_view()
        return

class dimvar(object):
    """Manipulatable variable
    """

    def __init__(self, name, vmin=0, vmax=None):
        """
        
        Arguments:
        - `name`:
        - `vmin`:
        - `vmax`:
        """
        self.name = name
        self.vmin = vmin
        self.vmax = vmax
        self._value = 0
        self._slider=None
        self._changed=False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,new_value):
        if not self.vmin<new_value<self.vmax:
            print('Value invalid')
            return
        else:
            self._value = new_value
            
    def add_slider(self,slider):
        self._slider=slider
        
    def get_changed(self):
        if self._slider.val!=self._value:
            self._value=self._slider.val
            self._changed = True
        else:
            self._changed = False
    
    def changed(self):
        return self._changed

class man_lineplot(object):
    """Plot an interactive line plot
    """

    def __init__(self, rows, columns, **kwargs):
        """
        
        Arguments:
        - `rows`:
        - `columns`:
        - `**kwargs`:
        """
        self._rows = rows
        self._columns = columns
        self._kwargs = kwargs

        self.fg = plt.figure(constrained_layout=True)
        self.gs0 = GridSpec(3,1,figure=self.fg)
        self.gs = GridSpecFromSubplotSpec(rows,columns,subplot_spec=self.gs0[0:2,:])
        self.gss = GridSpecFromSubplotSpec(1,1,subplot_spec=self.gs0[1,:])
        self.axs = dict()
        self.variables=dict()
        self.plots=[]
        self._axpos=[]
        self.saxs=[]

        
    def add_plot(self,axpos, x, data, variables, plot_ax=0, twinx=False, **kwargs):
        """ Add a single line plot to one of the figures axis
        Keyword Arguments:
        axpos     -- 
        x         -- 
        data      -- 
        variables -- 
        plot_ax (0) --
        **kwargs  -- 
        """

        axposn = f"{axpos}"
        axposn += 'y' if twinx else ''
        if not axposn in self.axs:
            if twinx and not axposn[:-1] in self.axs:
                return self.add_plot(axpos,x,data,variables,plot_ax,False,**kwargs)
            elif twinx:
                ax=self.axs[axposn[:-1]].twinx()
            else:    
                ax = self.fg.add_subplot(self.gs[tuple(axpos)])
            self.axs[axposn]=ax
        else:
            ax = self.axs[axposn]

        is2d = len(variables)==(len(data.shape)-2)
        if is2d:
            data = np.moveaxis(data,plot_ax,(len(data.shape)-2,len(data.shape)-1))
        else:
            data = np.moveaxis(data,plot_ax,len(data.shape)-1)
        varlist=[]
        for ii,v in enumerate(variables):
            vmin=0
            vmax=data.shape[ii]-1
            name=''
            if isinstance(v,list):  
                name = v[0]
                if len(v)==2:
                    vmin=v[1]
                if len(v)==3:
                    vmax=v[2]
            elif isinstance(v,str):
                name=v
            self._add_var(name,vmin,vmax)
            varlist.append(self.variables[v])

        if is2d:
            self.plots.append(plot2d(ax,x[0],x[1],data,varlist,**kwargs))
        else:
            self.plots.append(lineplot(ax,x,data,varlist,**kwargs))

    def _add_var(self,vname,vmin,vmax):
        if not vname in self.variables.keys():
            self.variables[vname]=dimvar(vname,vmin,vmax)
            fs = self.fg.get_size_inches()
            self.fg.set_size_inches([fs[0],fs[1]+slider_height_inches])

    def show(self):
        vlen = len(self.variables)
        self.gss=GridSpecFromSubplotSpec(vlen,1,self.gs0[2,0])
        for i,v in enumerate(self.variables.items()):
            ax = self.fg.add_subplot(self.gss[i,:])
            self.saxs.append(ax)
            sl = Slider(ax,v[0],v[1].vmin,v[1].vmax,valinit=0,valstep=1)
            sl.on_changed(self.update)
            v[1].add_slider(sl)
        # self.fg.subplots_adjust(left=0.15, bottom=0.25)
        plt.show()

         
    def update(self,val):
        for v in self.variables.values():
            v.get_changed()
        for plot in self.plots:
            plot.plot()
        self.fg.canvas.draw()
            

