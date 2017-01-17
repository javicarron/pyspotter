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


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.CreateStatusBar()
        
        #Menus
        filemenu=wx.Menu()
        menuOpen= filemenu.Append(wx.ID_OPEN, "&Open", "Open text file")
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
        #for i in range(1,6:
         #   self.buttons.append(wx.Button(self, 0, "Button &"+str(i)))
         #   self.sizerbut.Add(self.buttons[i], 1, wx.EXPAND)
            
        But.append(wx.Button(self, 1, "Exit"))
        self.sizerbut.Add(But[1], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, But[0])
        self.Bind(wx.EVT_BUTTON, self.OnExit, But[1])
        
        
        
        #Figure
        image=fits.open("red.fits")
        header=image['PRIMARY'].header
        data=image['PRIMARY'].data
        image.close()
        wcs=WCS(header)
        
        self.fig=plt.figure()
        ax=self.fig.add_axes([0.1,0.1,0.8,0.8], projection=wcs)
        ax.set_xlabel('RA')
        ax.set_ylabel('Dec')
        ax.imshow(data, cmap='gist_heat', origin='lower')
        ra=ax.coords[0]
        ra.set_major_formatter('hh:mm:ss')
        dec=ax.coords[1]
        dec.set_major_formatter('dd:mm:ss');
        
        
#        np.sqrt(1+np.sqrt(fits.getdata('red.fits')+2))
#        self.figure=plt.imshow(image, cmap='gist_heat', origin='lower')
#        plt.colorbar();
        
        #
#        self.figure =Figure()
#        self.axes = self.figure.add_subplot(111)
#        t=np.arange(0.0, 3.0, 0.01)
#        s=np.sin(2*np.pi*t)
#        
#        self.axes.plot(t,s)
        self.canvas = FigureCanvas(self, 0, self.fig)
        
        
        
        #Layout
        self.mainSizer=wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.sizerbut, 0, wx.EXPAND)
        self.mainSizer.Add(self.fig, 1, wx.EXPAND)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        #self.sizer.Fit(self)     
        self.SetSize((500,400))
        
        self.Show(True)
        
    
        
        
        
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
            f = open(os.path.join(self.dirname, self.filename), 'r')
            #self.control.SetValue(f.read())
            self.axes
            f.close()
        dlg.Destroy
        
        
app = wx.App(False)
frame = MainWindow(None, "Pyspotter")
app.MainLoop()