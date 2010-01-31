#!/usr/bin/python
# -*- coding: utf-8 -*-

# author : Benjamin Toueg
# date : 25/11/09

# FIXME : table view overwrites standard view in edition ref-case

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

import os,sys,time

sys.path.append(sys.path[0]+'/source')

import MyAsciiParser
from MySheet import MySheet
from MyTreeCtrl import MyTreeCtrl
from MyMenuBar import *
from MyCalculation import MyCalculation
from MyFilterPanel import MyFilterPanel
from MyTable import MyTableColumn
from MyFindReplaceDialog import MyFindReplaceDialog

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
    defaultDir = os.path.dirname(self.tree.GetItemText(root))
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
    filePath = os.path.expanduser(file)
    if not(os.path.isfile(filePath)):
      self.SetStatusText("Warning : "+filePath+" is not a file")
      return
    self.SetStatusText("Loading "+filePath+" ...")
    self.Update()
    start = time.time()
    self.tree.recoverAsciiFile(filePath)
    end = time.time()
    elapsed = end - start
    self.SetStatusText(filePath+" loaded in "+str(elapsed)+"s")
    self.Update()
    self.tree.bind(self)
    self.tree.SetFocus()

  def OnAbout(self, event):
    dlg = wx.MessageDialog(self, "Author : Benjamin Toueg\nDate : 01/12/2009","About Me", wx.OK | wx.ICON_INFORMATION)
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
    myCalculation = eltData.content
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
    parentId = self.tree.GetItemParent(eltId)
    parentData = self.tree.GetPyData(parentId)
    eltDataLabel = ''
    eltDataContent = None
    if eltId != self.tree.GetRootItem():
      eltDataLabel = eltData.label
      eltDataContent = eltData.content

    if eltDataLabel == "CALCULATIONS" and eltData.content != []:
      # second time a calculation node is selected
      self.OnMyCalculation(eltData)
      self.Bind(wx.EVT_BUTTON, self.OnClickedCalculation)
    elif eltDataLabel == 'CALCULATIONS' and eltData.content == []:
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
    elif eltDataContent!= None and len(eltData.content)>0:
      self.rightPanel.Show()
      self.filterPanel.Hide()
      # with table controler
      if eltData.table == None:
        eltData.table = MyTableColumn(eltData.label,eltData.content)
      self.sheet.SetTable(eltData.table)
      self.sheet.autosizeRowLabel()
      self.sheet.resetSize()
      # without table controler
      #self.sheet.SetNumberRows(len(eltData.content))
      #self.sheet.SetNumberCols(1)
      #self.sheet.SetColLabelValue(0,eltData.label)
      #self.sheet.pasteCol(0,0,eltData.content)
      if eltData.contentType == 1:
        self.sheet.SetColFormatNumber(0)
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
  def __init__(self, parent=None):
    # This is a recipe to a the screen.
    # Modify the following variables as necessary.
    aBitmap = wx.Image(name = sys.path[0]+'/splash.jpg').ConvertToBitmap()
    splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
    splashDuration = 1000 # milliseconds
    # Call the constructor with the above arguments in exactly the
    # following order.
    wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                              splashDuration, parent)
    self.Bind(wx.EVT_CLOSE, self.OnExit)
    wx.Yield()

  def OnExit(self, evt):
    # MainWindow is the main frame.
    frame = MainWindow(None,-1,'The DRAGON multicompo viewer')
    app.SetTopWindow(frame)
    try:
      file = sys.argv[1]
    except IndexError:
      file = './MultiCompo'
    frame.OpenFile(file)
    self.Hide()
    frame.Show(True)
    # The program will freeze without this line.
    evt.Skip()  # Make sure the default handler runs too...

#----------------------------------------------------------------------#

class MyApp(wx.App):
  def OnInit(self):
      MySplash = MySplashScreen()
      MySplash.Show()

      return True

#----------------------------------------------------------------------#

if __name__ == "__main__":
  app = MyApp()
  app.MainLoop()