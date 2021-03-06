#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 25/11/09

# FIXME : table view overwrites standard view in edition ref-case

import os,sys,time
from operator import isSequenceType

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

import lcmviewer
from lcmviewer import CONFIG
from lcmviewer.MySheet import MySheet
from lcmviewer.MyTreeCtrl import MyTreeCtrl
from lcmviewer.MyMenuBar import *
from lcmviewer.MyFilterPanel import MyFilterPanel
from lcmviewer.MyTable import MyTableColumn, MySummaryTable
from lcmviewer.MyFindReplaceDialog import MyFindReplaceDialog

ID_BUTTON = 100

class MainWindow(wx.Frame):
  def __init__(self,parent,id,title):
    wx.Frame.__init__(self,parent,id,title,pos=(500,500))
    self.SetSize((300,300)) # does not work, why ?
    self.Centre()
    self.initialize()
    self.searchedNode = None
    self.findDlg = MyFindReplaceDialog(self)
    self.findDlg.Bind(wx.EVT_FIND, self.OnFind)
    self.findDlg.Bind(wx.EVT_FIND_NEXT, self.OnFindNext)

  def initialize(self):
    self.SetMenuBar(MyMenuBar())
    self.CreateStatusBar()
    self.SetStatusText("Welcome !")

    self.panel = wx.Panel(self,-1)
    self.splitter = wx.SplitterWindow(self.panel, -1, style=wx.SP_3D)
    self.splitter.SetMinimumPaneSize(150)
    self.tree = MyTreeCtrl(self.splitter)
    self.rightPanel = wx.Panel(self.splitter,-1)
    self.sheet = MySheet(self.rightPanel)
    self.splitter.SplitVertically(self.tree,self.rightPanel)
    self.filterPanel = MyFilterPanel(self.rightPanel,-1)

    self.sizerRightPanel = wx.BoxSizer(wx.VERTICAL)
    self.sizerRightPanel.Add(self.filterPanel,0,wx.EXPAND)
    self.sizerRightPanel.Add(self.sheet,1,wx.EXPAND)
    self.rightPanel.SetSizer(self.sizerRightPanel)
    self.sizerRightPanel.Fit(self.rightPanel)

    self.mainSizer = wx.BoxSizer(wx.VERTICAL)
    self.mainSizer.Add(self.splitter,1,wx.EXPAND)
    self.panel.SetSizer(self.mainSizer)
    self.mainSizer.Fit(self)

    self.rightPanel.Hide()

    wx.EVT_MENU(self, ID_OPEN, self.OnOpenFile)
    wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
    wx.EVT_MENU(self, ID_EXIT,  self.OnQuit)
    wx.EVT_MENU(self, ID_EXPAND_ALL,  self.OnExpandAll)
    wx.EVT_MENU(self, ID_COLLAPSE_ALL,  self.OnCollapseAll)
    wx.EVT_MENU(self, ID_COLLAPSE_CHILDREN,  self.OnCollapseChildren)
    wx.EVT_MENU(self, ID_SEARCH,  self.OnSearch)
    self.Bind(wx.EVT_KEY_DOWN,self.OnKeyDown)

  def OnKeyDown(self,evt):
    keyCode = evt.GetKeyCode()
    if keyCode == wx.WXK_F3 and self.searchedNode == None:
      # key 'F3'
      findEvt = wx.FindDialogEvent()
      if evt.ShiftDown():
        self.OnFindPrev(findEvt)
      else:
        self.OnFindNext(findEvt)
    if evt.ControlDown():
      if keyCode == 70:
        # key 'f'
        self.OnSearch(evt)
    evt.Skip()

  def refresh(self):
    """Tip to refresh the window"""
    # following code resolves the problem of the sheet scroll bars when the window is not maximized
    w,h = self.GetSize()
    if not(self.IsMaximized()):
      self.SetSize((w+1,h))
      self.SetSize((w,h))
    else:
      self.SetSize((w+1,h))
      self.SetSize((w,h))
    # following line partly solves the problem of redrawing the tree when window is resized when tree vertical scroll bar is down
    self.tree.Refresh()


  def OnSearch(self,event):
    # FIXME always works with ShowModal() and crashes often wih Show()
    self.findDlg.ShowModal()

  def OnFind(self,event):
    findData = self.findDlg.GetData()
    down,wholeWord,matchCase = self.findDlg.getFlag()
    searchString = event.GetFindString()
    #if not matchCase: searchString.lower()
    root = self.tree.GetRootItem()
    self.findDlg.setResult(self.tree.find(root,searchString))
    item = self.findDlg.getCurrentFind()
    self.showItem(item)

  def OnFindNext(self,event):
    item = self.findDlg.getNextFind()
    self.showItem(item)

  def OnFindPrev(self,event):
    item = self.findDlg.getPrevFind()
    self.showItem(item)

  def showItem(self,item):
    if item != None :
      nodeId,idx = item
      self.tree.SelectItem(nodeId)
      self.sheet.ClearSelection()
      if idx > -1:
        self.sheet.SelectBlock(idx, 0, idx, 0, True)
        self.sheet.MakeCellVisible(idx, 0)
    else:
      dlg = wx.MessageDialog(self, 'The string "'+self.findDlg.GetData().GetFindString()+'" has not been found !',"Find", wx.OK | wx.ICON_EXCLAMATION)
      dlg.ShowModal()
      dlg.Destroy()

  def OnExpandAll(self, event):
    """In the doc there is a self.tree.ExpandAll method for TreeCtrl but my version of wxPython is not up to date"""
    selectedNode = self.tree.GetSelection()
    self.SetStatusText("Expanding all nodes from "+self.tree.GetItemText(selectedNode)+" ...")
    self.Update()
    self.tree.expandAllChildren(selectedNode)
    self.tree.Expand(selectedNode)
    self.SetStatusText("All nodes expanded from "+self.tree.GetItemText(selectedNode))

  def OnCollapseAll(self, event):
    """In the doc there is a self.tree.ExpandAll method for TreeCtrl but my version of wxPython is not up to date"""
    selectedNode = self.tree.GetSelection()
    self.SetStatusText("Collapsing all nodes from "+self.tree.GetItemText(selectedNode)+" ...")
    self.Update()
    self.tree.collapseAllChildren(selectedNode)
    self.tree.Collapse(selectedNode)
    self.SetStatusText("All nodes collapsed from "+self.tree.GetItemText(selectedNode))

  def OnCollapseChildren(self, event):
    """In the doc there is a self.tree.ExpandAll method for TreeCtrl but my version of wxPython is not up to date"""
    selectedNode = self.tree.GetSelection()
    self.SetStatusText("Collapsing all children from "+self.tree.GetItemText(selectedNode)+" ...")
    self.Update()
    self.tree.collapseChildren(selectedNode)
    self.SetStatusText("All children collapsed from "+self.tree.GetItemText(selectedNode))

  def OnOpenFile(self, event):
    root = self.tree.GetRootItem()
    if root.IsOk():
      defaultDir = os.path.dirname(self.tree.GetItemText(root))
    else:
      defaultDir = os.path.abspath('.')
    filedlg = wx.FileDialog(self, style = wx.CHANGE_DIR, defaultDir = defaultDir)
    if filedlg.ShowModal() == wx.ID_OK:
      filePath = filedlg.GetDirectory()+'/'+filedlg.GetFilename()
      if self.tree.GetRootItem():
        self.tree.Delete(self.tree.GetRootItem())
      self.SetStatusText("Opening file "+filePath+" ...")
      self.Update()
      self.OpenFile(filePath)
      self.SetStatusText(filePath+" opened")
    filedlg.Destroy()

  def OpenFile(self,file):
    filePath = os.path.abspath(file)
    if not(os.path.isfile(filePath)):
      self.SetStatusText("Warning : "+filePath+" does not exist or is not a file")
      return
    self.SetStatusText("Loading "+filePath+" ...")
    self.Update()
    start = time.time()
    self.tree.recoverAsciiFile(filePath)
    end = time.time()
    elapsed = end - start
    self.SetStatusText(filePath+" loaded in "+str(elapsed)+"s")
    # save last opened file in configuration file
    CONFIG['lastfile']=filePath
    lcmviewer.saveConfig()
    self.Update()
    self.tree.bind(self)
    self.tree.SetFocus()

  def OnAbout(self, event):
    about_message = """
GUI for viewing XSM files generated by DRAGON/DONJON and APOLLO neutronic codes.
Copyright (C) 2009-2011 Benjamin Toueg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
    dlg = wx.MessageDialog(self, about_message, "About Me", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()

  def OnQuit(self, event):
    self.Close(True)

  def OnMyCalculation(self,eltData):
    """
    eltData should be an instance of MyCalculation
    sheet should not have a table set otherwise it has the priority
    """
    self.rightPanel.Show()
    self.filterPanel.Show()
    self.filterPanel.clear()
    myCalculation = eltData.content.getContent()
    self.filterPanel.setComboBoxes(myCalculation.getComboBoxesList())
    self.filterPanel.initialize2()
    self.filterPanel.bind(myCalculation.OnApplyFilter)
    myCalculation.setFilterPanel(self.filterPanel)
    # with table controler
    self.sheet.SetTable(myCalculation.getTable())
    self.sheet.autosizeRowLabel()
    self.sheet.resetSize()
    # without table controler
    #self.sheet.displayCalculation(myCalculation)

  def OnClickedCalculation(self,evt):
    self.refresh()
    eltId = self.tree.GetSelection()
    eltData = self.tree.GetPyData(eltId)
    self.OnMyCalculation(eltData)

  def OnClickedRefcase(self,evt):
    self.refresh()
    eltId = self.tree.GetSelection()
    eltData = self.tree.GetPyData(eltId)
    self.rightPanel.Show()
    self.filterPanel.Show()
    self.filterPanel.clear()
    myCalculation = eltData.content
    self.filterPanel.setComboBoxes(myCalculation.getComboBoxesList())
    self.filterPanel.initialize2()
    self.filterPanel.bind(myCalculation.OnApplyFilter)
    myCalculation.setFilterPanel(self.filterPanel)
    self.sheet.displayRefcase(myCalculation,myCalculation.filteredXS,[1,2])

  def OnItemExpanded(self, evt):
    self.SetStatusText("OnItemExpanded: "+self.tree.GetItemText(evt.GetItem()))

  def OnItemCollapsed(self, evt):
    self.SetStatusText("OnItemCollapsed:"+self.tree.GetItemText(evt.GetItem()))

  def OnSelChanged(self, evt, computationTime = True):
    if computationTime:
      self.SetStatusText("Computing... Please wait")
      self.Update()
      start = time.time()
    self.refresh()
    eltId = evt.GetItem()
    eltData = self.tree.GetPyData(eltId)
    if eltId == self.tree.GetRootItem():
      eltDataLabel = ''
      eltDataContent = None
      parentId = None
      parentData = None
    else:
      eltDataLabel = eltData.label
      eltDataContentObject = eltData.content
      if isSequenceType(eltDataContentObject):
        eltDataContent = eltDataContentObject
      else:
        eltDataContent = eltDataContentObject.getContent()
      parentId = self.tree.GetItemParent(eltId)
      parentData = self.tree.GetPyData(parentId)

    if eltDataLabel == "CALCULATIONS" and eltDataContent != []:
      # second time a calculation node is selected
      self.OnMyCalculation(eltData)
      self.Bind(wx.EVT_BUTTON, self.OnClickedCalculation)
    elif eltDataLabel == 'CALCULATIONS' and eltDataContent == []:
      # first time a calculation node is selected
      self.tree.computeMulticompoCalculation(eltId,eltData,parentId,parentData)
      self.OnSelChanged(evt,False)
    elif eltDataLabel == 'REF-CASE   1' and eltData.content != None:
      self.rightPanel.Show()
      self.filterPanel.Show()
      self.filterPanel.clear()
      myRefcase = eltData.content
      self.filterPanel.setComboBoxes(myRefcase.getComboBoxesList())
      self.filterPanel.initialize2()
      self.filterPanel.bind(myRefcase.OnApplyFilter)
      self.Bind(wx.EVT_BUTTON, self.OnClickedRefcase)
      myRefcase.setFilterPanel(self.filterPanel)
      self.sheet.displayRefcase(myRefcase,myRefcase.filteredXS,[1,2])
    elif eltDataLabel == 'REF-CASE   1' and eltData.content == None:
      self.tree.computeEditionRefcase(eltId,eltData,parentId,parentData)
      self.OnSelChanged(evt,False)
    elif eltDataLabel == 'GROUP' and eltData.content != []:
      print 'coucou_not_none'
    elif eltDataLabel == 'GROUP' and eltData.content == []:
      # try to compute reaction rate
      reactionRate = ( self.tree.find(eltId,'FLUX-INTG'.lower(),searchAll=False) != [] )
      if reactionRate:
        self.tree.computeReactionRate(eltId,eltData,parentId,parentData)
      #self.tree.computeFluxMap(eltId,eltData,parentId,parentData)
    elif eltDataContent!= None and len(eltDataContent)>0:
      self.rightPanel.Show()
      self.filterPanel.Hide()
      # with table controler
      if eltData.table == None:
        eltData.table = MyTableColumn(eltData.label,eltDataContent)
      self.sheet.SetTable(eltData.table)
      self.sheet.autosizeRowLabel()
      self.sheet.resetSize()
      if eltData.contentType == 1:
        self.sheet.SetColFormatNumber(0)
    elif self.tree.ItemHasChildren(eltId):
      if eltData.table == None:
        eltData.table = MySummaryTable(self.tree.getSummary(eltId))
      self.sheet.SetTable(eltData.table)
      self.sheet.autosizeRowLabel()
      self.sheet.resetSize()
      self.sheet.setColFormat(eltData.table.summary)
      self.rightPanel.Show()
      self.filterPanel.Hide()
    else:
      self.rightPanel.Hide()
      self.filterPanel.Hide()

    self.refresh()
    if computationTime:
      end = time.time()
      elapsed = end - start
      self.SetStatusText("Computation finished in "+str(elapsed)+" s")
      self.Update()

  def OnActivated(self, evt):
      self.SetStatusText("OnActivated:    "+self.tree.GetItemText(evt.GetItem()))
      self.tree.Toggle(evt.GetItem())

#----------------------------------------------------------------------#

class MySplashScreen(wx.SplashScreen):
  """
  Create a splash screen widget.
  """
  def __init__(self, parent, appLauncher):
    self.appLauncher = appLauncher
    aBitmap = wx.Image(name = sys.path[0]+'/splash.jpg').ConvertToBitmap()
    splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
    splashDuration = 1000 # milliseconds
    # Call the constructor with the above arguments in exactly the
    # following order.
    wx.SplashScreen.__init__(self, aBitmap, splashStyle, splashDuration, parent)
    self.Bind(wx.EVT_CLOSE, self.OnExit)
    wx.Yield()

  def OnExit(self, evt):
    self.appLauncher()
    self.Hide()
    # The program will freeze without this line.
    evt.Skip()  # Make sure the default handler runs too...

#----------------------------------------------------------------------#

class MyApp(wx.App):
  def __init__(self,file):
    self.file = file
    wx.App.__init__(self)

  def OnInit(self):
    if CONFIG["splash"]:
      MySplash = MySplashScreen(None, self.LaunchMainWindow)
      MySplash.Show()
    else:
      self.LaunchMainWindow()
    return True

  def LaunchMainWindow(self):
    # MainWindow is the main frame.
    frame = MainWindow(None,-1,'The DRAGON multicompo viewer')
    #app.SetTopWindow(frame)
    frame.OpenFile(self.file)
    frame.Show(True)

#----------------------------------------------------------------------#

if __name__ == "__main__":
  try:
    lastfile = sys.argv[1]
  except IndexError:
    lastfile = CONFIG["lastfile"]
  # launch main window
  app = MyApp(lastfile)
  app.MainLoop()
  
