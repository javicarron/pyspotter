#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Small program with graphical interface to visualize astronomical images in FITS
format. It is able to change the way the intensity is visualized and the color 
of image. It loads local images and search for images in SkyView archive with
its built-it search function, that allows the specification of the survey used.
"""

import wx
import os
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.wcs import WCS
from astroquery.skyview import SkyView
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import surveys


class CanvasPanel(wx.Panel):
    """Panel in which all the images are plotted."""
    def __init__(self, parent, image=fits.open("horse.fits"),option="Normal"):
        wx.Panel.__init__(self, parent)
        self.SetImage(fits.open("horse.fits"))
        
    def SetImage(self, image):
        """Set an image to the canvas, setting the axes automatically"""
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
        """Change the method to display the intensity and the colormap"""
        if option=="Root":
            self.ax.imshow(np.sqrt(1+self.data), cmap=color, origin='lower')
        elif option=="Logarithmic":
            self.ax.imshow(np.log(1+self.data), cmap=color, origin='lower')
        else:
            self.ax.imshow(self.data, cmap=color, origin='lower')
        self.canvas.draw()
        
        
        
class MainWindow(wx.Frame):
    """Main window of the program"""
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        self.CreateStatusBar()
        
        #Initialize variables
        self.revinten = False
        self.color = "gist_heat"
        self.inten = "Normal"
        self.band = "Optical:SDSS"
        self.survey = "SDSSg"
        
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
        
        
        #Figure
        self.panel=CanvasPanel(self)
        
        
        #Open button        
        self.ButOpen=wx.Button(self, 0, "Open FITS file")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.ButOpen)        
        
        
        #Intensity options
        self.rbint = wx.RadioBox(self, label="Set intensity", choices=['Normal', 'Root', 'Logarithmic'])
        self.Bind(wx.EVT_RADIOBOX, self.OnInten, self.rbint)
        
        self.revint= wx.CheckBox(self, label="Inverse intensity")
        self.Bind(wx.EVT_CHECKBOX, self.OnRevInten, self.revint)
        
        self.colorque = wx.StaticText(self, label="Set colormap")
        cmaps = ['%PERCEPTUALLY UNIFORM SEQUENTIAL','viridis', 'inferno', 'plasma', 'magma','%SEQUENTIAL','Blues', 'BuGn', 'BuPu','GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd','PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', '%SEQUENTIAL (2)', 'afmhot', 'autumn', 'bone', 'cool', 'copper', 'gist_heat', 'gray', 'hot', 'pink', 'spring', 'summer', 'winter', '%DIVERGING', 'BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'seismic', '%QUALITATIVE', 'Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2', 'Set1', 'Set2', 'Set3', 'Vega10', 'Vega20', 'Vega20b', 'Vega20c', '%MISCELLANEOUS', 'gist_earth', 'terrain', 'ocean', 'gist_stern', 'brg', 'CMRmap', 'cubehelix', 'gnuplot', 'gnuplot2', 'gist_ncar', 'nipy_spectral', 'jet', 'rainbow', 'gist_rainbow', 'hsv', 'flag', 'prism']
        self.colorlist=wx.ComboBox(self, choices=cmaps, style=wx.CB_DROPDOWN, value='gist_heat')
        self.Bind(wx.EVT_COMBOBOX, self.OnColor, self.colorlist)
            

        #Search
        self.searchque = wx.StaticText(self, label="Object to search: ")
        self.searchbox=wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.searchbox)
        self.searchbut=wx.Button(self, 1, "Search")
        self.Bind(wx.EVT_BUTTON, self.OnSearch, self.searchbut)
        
#        self.surveyque = wx.StaticText(self, label="Band and survey")
        self.surv=surveys.list()
        self.bandlist=wx.ComboBox(self, choices=self.surv.keys(), style=wx.CB_DROPDOWN, value='Optical:SDSS')
        self.Bind(wx.EVT_COMBOBOX, self.OnBand, self.bandlist)
        self.surveylist=wx.ComboBox(self, choices=self.surv[self.band], style=wx.CB_DROPDOWN, value="Choose a survey")
        self.Bind(wx.EVT_COMBOBOX, self.OnSurvey, self.surveylist)
        
        
        #Layout
        sizeropt1=wx.BoxSizer(wx.HORIZONTAL)
        sizeropt1.Add(self.rbint, 1, wx.EXPAND|wx.ALL, border=5)
        sizeropt1.Add(self.revint, 1, wx.EXPAND|wx.ALL, border=5)
        sizeropt2=wx.BoxSizer(wx.HORIZONTAL)
        sizeropt2.Add(self.colorque, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=15)
        sizeropt2.Add(self.colorlist, 0, wx.EXPAND|wx.ALL, border=15)
        sizeropt=wx.BoxSizer(wx.VERTICAL)
        sizeropt.Add(sizeropt1, 0, wx.EXPAND)
        sizeropt.Add(sizeropt2, 0, wx.EXPAND|wx.CENTER)
        
        sizersearch1=wx.BoxSizer(wx.HORIZONTAL)
        sizersearch1.Add(self.searchque, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, border=10)
        sizersearch1.Add(self.searchbox, 1, wx.EXPAND|wx.ALL, border=10)
        sizersearch1.Add(self.searchbut, 1, wx.EXPAND|wx.ALL, border=10)
#        sizersearch2.Add(self.surveyque, 0, wx.EXPAND)
        sizersearch2=wx.BoxSizer(wx.HORIZONTAL)
        sizersearch2.Add(self.bandlist, 1, wx.EXPAND|wx.ALL, border=10)
        sizersearch2.Add(self.surveylist, 1, wx.EXPAND|wx.ALL, border=10)
        sizersearch=wx.BoxSizer(wx.VERTICAL)
        sizersearch.Add(sizersearch1, 0, wx.EXPAND)
        sizersearch.Add(sizersearch2, 0, wx.EXPAND)

        sizerright=wx.BoxSizer(wx.VERTICAL)
        sizerright.Add(self.ButOpen, 0, wx.ALL|wx.CENTER, border=50)
        sizerright.Add(sizeropt, 1, wx.EXPAND|wx.ALL, border=25)
        sizerright.Add(sizersearch, 1, wx.EXPAND|wx.ALL, border=25)
        
        self.mainSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.panel, 1, wx.EXPAND | wx.ALIGN_CENTER)
        self.mainSizer.Add(sizerright, 1, wx.EXPAND, border=5)

        self.SetSizer(self.mainSizer)
        self.SetAutoLayout(1)
        self.mainSizer.Fit(self)     
        self.SetSize((1100,555))
        
        self.Show(True)
        
    def OnColor(self,event):
        """Get the colormap selected en the list"""
        if self.revinten:
            self.color=event.GetString()+"_r"
        else:
            self.color=event.GetString()
        self.panel.SetOption(self.inten, self.color)
        
    def OnInten(self, event):
        """Get the method to display the intensity"""
        self.inten= self.rbint.GetStringSelection()
        self.panel.SetOption(self.inten, self.color)
        
    def OnRevInten(self, event):
        """Get the choice of the user to revert or not the intensity"""
        self.revinten= self.revint.GetValue()
        if self.revinten:
            self.color=self.color+"_r"
        else:
            self.color=self.color[:-2]
        self.panel.SetOption(self.inten, self.color)
        
    def OnSearch(self,event):
        """Make an online search with SkyView"""
        self.search=self.searchbox.GetValue()
        image = SkyView.get_images(position=self.search, survey=self.survey)[0]
        self.panel.SetImage(image)
        self.panel.SetOption(self.inten,self.color)
        
    def OnBand(self, event):
        """Get the prefered band in which the search has to be done"""
        self.band=event.GetString()
        self.survey=self.surv[self.band][0]
        self.surveylist.Clear()
        self.surveylist.AppendItems(self.surv[self.band])
        self.surveylist.SetValue(self.survey)
        
    def OnSurvey(self, event):
        """Get the survey to use in the search"""
        self.survey=event.GetString()
        
    def OnAbout(self,e):
        """Show the About Menu"""
        dlg = wx.MessageDialog(self, "A small astronomical image analyzer by Javier Carrón Duque in 2017.\n \nViewer with graphical interface to visualize astronomical images in FITS format. It is able to change the way the intensity is visualized and the color of image. It loads local images and search for images in SkyView archive with its built-it search function, that allows the specification of the survey used. \n \nModules used: wx, os, astropy, astroquery, matplotlib, numpy. All credits to the original authors", "About Pyspotter", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnExit(self,e):
        """Terminate the program"""
        self.Close(True)
        
    def OnOpen(self,e):
        """Open a FITS file"""
        self.dirname=''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.fits", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            img = fits.open(os.path.join(self.dirname, self.filename))
            self.panel.SetImage(img)
            self.panel.SetOption(self.inten,self.color)
            self.panel.Show()
        dlg.Destroy()
        
#My python folder weights too much: it weights Pi tons.        
app = wx.App(False)
frame = MainWindow(None, "Pyspotter")
app.MainLoop()