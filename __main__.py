#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comment
"""

import wx
import os
from astropy.io import fits
#from astropy.utils.data import download_file
import matplotlib.pyplot as plt
from astropy.wcs import WCS
#from astropy.coordinates import SkyCoord
#from astropy.nddata import Cutout2D
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure


class CanvasPanel(wx.Panel):
    def __init__(self, parent, image=fits.open("horse.fits"),option="Normal"):
        wx.Panel.__init__(self, parent)
        self.SetImage(fits.open("horse.fits"))
        
        
    def SetImage(self, image):
        header=image['PRIMARY'].header
        self.data=image['PRIMARY'].data
        image.close()
        wcs=WCS(header)
        
        self.fig=plt.figure()
        self.ax=self.fig.add_axes([0.1,0.1,0.8,0.8], projection=wcs)
        self.ax.set_xlabel('RA')
        self.ax.set_ylabel('Dec')   
        
        self.ax.imshow(self.data, cmap='gist_heat', origin='lower')
        ra=self.ax.coords[0]
        ra.set_major_formatter('hh:mm:ss')
        dec=self.ax.coords[1]
        dec.set_major_formatter('dd:mm:ss');
        self.canvas =FigureCanvas(self,-1,self.fig)
        
        
    def SetOption(self, option, color='gist_heat'):
        if option=="Root":
            self.ax.imshow(np.sqrt(1+self.data), cmap=color, origin='lower')
        elif option=="Logarithmic":
            self.ax.imshow(np.log(1+self.data), cmap=color, origin='lower')
        else:
            self.ax.imshow(self.data, cmap=color, origin='lower')
        self.canvas.draw()
        

        
        
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.CreateStatusBar()
        
        
        #Menus
        filemenu=wx.Menu()
        menuOpen= filemenu.Append(wx.ID_OPEN, "&Open", "Open a FITS file in the computer")
        filemenu.AppendSeparator()
        menuExit= filemenu.Append(wx.ID_EXIT,"E&xit", "Terminate this program")
        
        helpmenu=wx.Menu()
        menuAbout= helpmenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        
        menuBar=wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        
        
        #Buttons        
        self.sizerbut=wx.BoxSizer(wx.HORIZONTAL)
        But=self.buttons =[]
        But.append(wx.Button(self, 0, "Open"))
        self.sizerbut.Add(But[0], 1, wx.EXPAND)
        But.append(wx.Button(self, 1, "Exit"))
        self.sizerbut.Add(But[1], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, But[0])
        self.Bind(wx.EVT_BUTTON, self.OnExit, But[1])
        
        
        #Options
        self.revinten = False
        self.color = "gist_heat"
        self.inten = "Normal"
        
        self.rbint = wx.RadioBox(self, label="Set intensity", choices=['Normal', 'Root', 'Logarithmic'])
        self.Bind(wx.EVT_RADIOBOX, self.OnInten, self.rbint)
        
        self.revint= wx.CheckBox(self, label="Inverse intensity")
        self.Bind(wx.EVT_CHECKBOX, self.OnRevInten, self.revint)
        
        self.colorque = wx.StaticText(self, label="Set colormap")
        cmaps = ['%Perceptually Uniform Sequential','viridis', 'inferno', 'plasma', 'magma','%Sequential','Blues', 'BuGn', 'BuPu','GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd','PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', '%Sequential (2)', 'afmhot', 'autumn', 'bone', 'cool', 'copper', 'gist_heat', 'gray', 'hot', 'pink', 'spring', 'summer', 'winter', '%Diverging', 'BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'seismic', '%Qualitative', 'Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2', 'Set1', 'Set2', 'Set3', 'Vega10', 'Vega20', 'Vega20b', 'Vega20c', '%Miscellaneous', 'gist_earth', 'terrain', 'ocean', 'gist_stern', 'brg', 'CMRmap', 'cubehelix', 'gnuplot', 'gnuplot2', 'gist_ncar', 'nipy_spectral', 'jet', 'rainbow', 'gist_rainbow', 'hsv', 'flag', 'prism']
        self.colorlist=wx.ComboBox(self, choices=cmaps, style=wx.CB_DROPDOWN, value='gist_heat')
        self.Bind(wx.EVT_COMBOBOX, self.OnColor, self.colorlist)
                           
#        self.rbcolor=wx.ColourPickerCtrl(self)
#        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnColor, self.rbcolor)
        
        
        #Figure
        self.panel=CanvasPanel(self)
        
        
        
        #Layout
        sizeropt=wx.BoxSizer(wx.HORIZONTAL)
        sizeropt.Add(self.rbint, 0, wx.EXPAND)
        sizeropt.Add(self.revint, 0, wx.EXPAND)
        sizeropt.Add(self.colorque, 1, wx.EXPAND)
        sizeropt.Add(self.colorlist, 1, wx.EXPAND)
        
        self.mainSizer=wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.sizerbut, 0, wx.EXPAND)
        self.mainSizer.Add(self.panel, 1, wx.EXPAND)
        self.mainSizer.Add(sizeropt, 0, wx.EXPAND)
#        self.mainSizer.Add(self.rbcolor, 0, wx.EXPAND)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        #self.sizer.Fit(self)     
        self.SetSize((650,600))
        
        self.Show(True)
        
    def OnColor(self,event):
#        color=self.rbcolor.GetColour()
#        print(color)
        if self.revinten:
            self.color=event.GetString()+"_r"
        else:
            self.color=event.GetString()
        self.panel.SetOption(self.inten, self.color)
        
    def OnInten(self, event):
        self.inten= self.rbint.GetStringSelection()
        self.panel.SetOption(self.inten, self.color)
        
    def OnRevInten(self, event):
        self.revinten= self.revint.GetValue()
        if self.revinten:
            self.color=self.color+"_r"
        else:
            self.color=self.color[:-2]
        self.panel.SetOption(self.inten, self.color)
        
    def OnAbout(self,e):
        dlg = wx.MessageDialog(self, "A small astronomical image analyzer", "About Pyspotter", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnExit(self,e):
        self.Close(True)
        
    def OnOpen(self,e):
        self.dirname=''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.fits", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            img = fits.open(os.path.join(self.dirname, self.filename))
#            option= self.rbint.GetStringSelection()
            self.panel.SetImage(img)
            self.panel.SetOption(self.inten,self.color)
            self.panel.Show()
        dlg.Destroy()
        
        
app = wx.App(False)
frame = MainWindow(None, "Pyspotter")
app.MainLoop()