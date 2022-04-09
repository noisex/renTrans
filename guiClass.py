import os
import re
import time
import logging

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from colour import Color
# from mycolorpy import colorlist as mcp
from yoFrames import YoProgress
from settings import settings


myBlack = '#292929'
myGreay = '#e1e1e1'
myRed   = 'red'
# myBrown = '#bbb'
myBrown = '#ccc'


class YoButton( ttk.Button):
    _frames = []

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        bStyle = rStyle = ttk.Style()
        bStyle.configure('bSlyle.TButton', foreground=myBlack)
        rStyle.configure('rSlyle.TButton', foreground=myRed)
        self._frames.append( self)
        self.bind('<Button-1>', self._lastIsRed)

    def _lastIsRed(self, _event):
        for btn in self._frames:
            btn.configure( style='bSlyle.TButton')
        self.configure( style='rSlyle.TButton')


class YoTextBox(tk.Text):
    re = re.compile(r'`(\w+?)`(.+?)`')

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        # self.re = re.compile( r'`(\w+?)`(.+?)`')
        self.lastLine = 0
        self.lastString = ''
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.bind('<<TextModified>>', self.__textchanged__)

        self.configure( font=("Consolas", 8), fg=myBlack, bg=myGreay)
        self.tag_configure("bold",  font=("Consolas", 8, 'bold'), foreground=myBlack)
        self.tag_configure("big",   font=("Consolas", 11, 'bold'), foreground='navy')
        self.tag_configure("red",   font=("Consolas", 8, 'bold'), foreground='red')
        self.tag_configure("green", font=("Consolas", 8, 'bold'), foreground='green')
        self.tag_configure("navy",  font=("Consolas", 8, 'bold'), foreground='navy')
        colors = list( Color("forestgreen").range_to(Color("indigo"), 101))
        for tagID in range( 101):
            self.tag_configure( f'rain{tagID}', font=("Consolas", 8, "bold"), foreground=f'{colors[tagID]}')   #  copper  gist_rainbow  brg
        # for tagID, col in enumerate( mcp.gen_color(cmap="jet", n=101), False):
        #     self.tag_configure(f'rain{tagID}', font=("Consolas", 8, "bold"), foreground=f'{col}')

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call( cmd)
        self.lastString = args
        # print( command, args)
        if command in "insert":   #, "replace"):
            self.event_generate("<<TextModified>>")
        return result

    def __textchanged__(self, evt):
        self.lastLine += self.lastString[1].count( '\n')
        line = evt.widget.get( f'{self.lastLine}.0', 'end-2c')
        fix  = re.findall( self.re, line)
        if len( fix) >= 1:
            dicTags = {}
            for ind, tagFind in enumerate( fix):
                tag, tagText = tagFind
                if tag in evt.widget.tag_names() and len( tagText) >= 1:
                    m = line.find( f"`{tag}`")
                    dicTags[ind] = { 'tag': tag, 'start': m, 'end': m + len( tagText)}
                line = line.replace(f'`{tag}`', '', 1).replace('`', '', 1)
            self.replace(f'{self.lastLine}.0', 'end-2c', line)

            for _, tags in dicTags.items():
                self.tag_add(tags["tag"], f'{self.lastLine}.{tags["start"]}', f'{self.lastLine}.{tags["end"]}')


class YoListBox(tk.Listbox):
    def __init__(self, parent, **kwargs):
        # self.app = None
        kwargs['bg'] = myGreay
        kwargs['fg'] = myBlack
        kwargs['font'] = ( 'Microsoft JhengHei UI', 10)

        super().__init__(parent, **kwargs)
        self.bind('<Double-Button-1>',  self.callback)
        self.app = YoFrame()
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        # print( cmd)
        result = self.tk.call(cmd)
        if command in "insert":  # , "delete", "replace"):
            gamesPath = self.app.cbGameFolder.get()
            gameTLPath = gamesPath + args[1] + '\\game\\tl\\rus\\'
            # print(gameTLPath)
            if not os.path.exists( gameTLPath):
                self.itemconfig( 'end', fg="#f00")
            else:
                self.itemconfig( 'end', fg=myBlack)
        return result

    # todo переписать на юзать листобсовые итемы, а не Резалт
    def callback(self, _event):
        result = self.get(0, tk.END)
        selected = self.selection_get()
        self.configure(foreground='#00f')
        for i, _ in enumerate(result):
            self.itemconfig(i, bg=myGreay)
            if result[i] == selected:
                self.itemconfig(i, bg=myBrown)
            # if os.path.exists( self.game.)
        # print (        u'Нажата кнопка', event) #.widget['text'])


class YoTreeView(ttk.Treeview):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind( '<Double-1>', self.doubleClick)
        self.arrow      = False
        self.sortColumn = '#0'
        self.selected   = None
        self.app        = YoFrame()
        self._orig      = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

        style = ttk.Style()
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 10, 'bold'), rowheight=10)  # Modify the font of the headings
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 8), rowheight=15)  # Modify the font of the body
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'NWSE'})])  # Remove the borders

        self.tag_configure('odd', background=myRed, foreground=myGreay, font=('Calibri', 9, 'bold'))  # '#E8E8E8')
        self.tag_configure('even', background=myGreay, foreground=myBlack)  # '#DFDFDF')
        self.configure( style="mystyle.Treeview",  selectmode='browse')

    def _proxy(self, command, *args):
        
        if command in "insert":  # , "delete", "replace"):
            itemText = args[3]
            if ( self.selected) and ( itemText in self.selected):
                args = args + ( '-tags', 'odd')
        elif command in 'column':
            columnID = args[0]
            if columnID in '#0':
                textName = self.names[0]
            else:
                textName = self.names[int(columnID)]
            self.heading( columnID, text=textName, anchor=tk.W, command=lambda c=columnID: self.headerClick(c))

        cmd = (self._orig, command) + args
        # print( command, args)
        result = self.tk.call(cmd)
        return result

    def updateData(self):
        if len( self.data) < 1:
            return
        sortID = int( self.sortColumn) if self.sortColumn not in '#0' else 0

        try:
            _listSorted = sorted( self.data, key=lambda x: x[sortID], reverse=self.arrow)
        except IndexError:
            return
        self.delete( *self.get_children())
        for data in _listSorted:
            textData = ()
            for ind in range( 1, len(data)):
                textData = textData + ( data[ind],)
            self.insert('', "end", None, text=data[0], values=textData)

    def insertData(self, data):
        self.data = data
        self.updateData()

    def treeReset( self):
        self.headerClear()
        self.selected   = None
        self.sortColumn = '#0'

    def treeTagsReset( self, tagNameOld: str, tagNameNew=''):
        tagList = self.tag_has(tagNameOld, item=None)
        for itemID in tagList:
            self.item(itemID, tags=(tagNameNew,))

    def doubleClick( self, event):
        region = self.identify("region", event.x, event.y)  # header/tree/cell
        if region in ('tree', 'cell'):
            self.treeTagsReset( 'odd', '')

            selected = self.focus()
            item = self.item(selected)
            self.item(selected, tags=('odd',))
            self.selected = item['text']
            # print(selected, item, region, self.selected)

    def toggleArrow( self):
        self.arrow = not self.arrow
        return ' ' + chr(8593) if self.arrow else ' ' + chr(8595)  # chr( 24) chr( 25) 30 31

    def setArrow( self):
        self.arrow = False
        return ' ' + chr(8595)

    def headerClear( self, headerID=None):
        if headerID:
            headerData = self.heading(headerID)
            headerText = headerData['text'].split(' ')[0]
            self.heading(headerID, text=headerText)
        else:
            headerData = self.heading('#0')
            headerText = headerData['text'].split(' ')[0]
            self.heading('#0', text=headerText)
        
            for headID, headerName in enumerate(self["columns"]):
                headerData = self.heading(headID)
                headerText = headerData['text'].split(' ')[0]
                # print( headerName, headerText)
                self.heading(headID, text=headerText)

    def headerClick( self, headerID):    #command=lambda c=2:    self.treeGames.headerClick(c)
        if headerID != self.sortColumn:
            self.headerClear(self.sortColumn)

        headerData = self.heading(headerID)
        headerSplitText = headerData['text'].split(' ')
        headerText = headerSplitText[0]

        if len(headerSplitText) > 1:
            arrow = self.toggleArrow()
        else:
            arrow = self.setArrow()

        self.heading(headerID, text=headerText + arrow)
        self.sortColumn = headerID
        self.updateData()
        # print( headerID, headerData, self.treeGames.sortColumn)
        

class YoFrame(tk.Tk):
    _init = None
    _instance = None

    def __new__(cls):
        if not cls._instance:
            #  if not hasattr(cls, 'instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if self._init:
            return

        self._init = self._instance
        super().__init__( *args, **kwargs)

        try:
            os.mkdir( settings['folderLOGS'])
        except FileExistsError:
            pass

        logFileName = f"{settings['folderLOGS']}mainlog_{time.strftime('%Y.%m.%d')}.log"
        logging.basicConfig(filename=logFileName, format='%(asctime)s %(message)s', datefmt='%Y.%m.%d %H:%M:%S', encoding='utf-8', level=logging.INFO)

        self.log     = logging
        self.testRun = tk.BooleanVar()
        self.testRun.set( False)

        self.allExctract = tk.BooleanVar()
        self.allExctract.set( False)

        self.languages = [
            "auto",
            "en",
            "es",
            "ru",
            "de",
            "it",
            "ko",
        ]

        self.lang = tk.StringVar()
        self.lang.set( self.languages[1])

        self.trans = tk.StringVar()
        self.trans.set( self.languages[3])

        self.gameFolder = tk.StringVar()
        self.gameFolder.set( settings['gameFolderList'][0])

        _gameSot = ('by name', 'by date')
        self.gameSort = tk.StringVar()
        self.gameSort.set( _gameSot[0])  # = sort by name

        self.minsize( 1300, 400)
        self.geometry("1450x650")

        self.columnconfigure(3, weight=1, minsize=50)
        self.rowconfigure(   0, weight=2, pad=5)
        self.rowconfigure(   1, weight=0, pad=5)

        self.menubar    = tk.Menu( self, background=myGreay)
        self.filemenu   = tk.Menu( self.menubar, tearoff=0, background=myGreay, foreground=myBlack)
        self.filemenu.add_command(label="Open")
        # self.filemenu.add_command(label="Find & Replace")
        # self.filemenu.add_command(label="WordDIC replacer")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)

        self.menubar.add_cascade(label="Tools", menu=self.filemenu)
        self.config(menu=self.menubar)

        #######################################################################################################
        #                                           1
        #######################################################################################################
        groupGames = tk.LabelFrame(self, padx=3, pady=3, text="Game select")
        groupGames.grid(row=0, column=0, padx=3, pady=3, sticky='NWES')
        groupGames.columnconfigure(0, weight=2, minsize=25)
        groupGames.rowconfigure( 2, weight=2, pad=0)

        frameCombo = ttk.Frame( groupGames)
        frameCombo.columnconfigure(0, weight=50)
        frameCombo.grid( row=1, column=0, sticky='NWES', padx=0, pady=3)

        self.lbGameSelected  = ttk.Label(    groupGames, text="None")  #, font=('Microsoft JhengHei UI', 12))
        self.cbGameFolder    = ttk.Combobox( frameCombo, textvariable=self.gameFolder, values=settings['gameFolderList'], state='readonly')
        self.cbGamesSort     = ttk.Combobox( frameCombo, textvariable=self.gameSort,   values=_gameSot,          width=8, state='readonly')
        self.listGames       = YoListBox(    groupGames, selectmode=tk.NORMAL, height=4, width=32, )
        self.btnGameRescan   = YoButton(   groupGames, text="rescan game list")  #, command= lambda: self.btnClickCTRL( 'btnGameRescan' ))#, command= gamesScan)
        self.btnExtract      = YoButton(   groupGames, text="extract rpyc/fonts")  #, command= buttonExtract)
        self.btnDecompile    = YoButton(   groupGames, text="decompile rpyc->rpy")  #, command= buttonDecompile)
        self.btnRunRenpy     = YoButton(   groupGames, text="run SDK to translate")  #, command= btnRunSDKClick)
        self.btnFontsCopy    = YoButton(   groupGames, text="non rus fonts + myStuff")  #, command= scanInputFolder)
        self.btnMenuFinder   = YoButton(   groupGames, text="make menu finder")  #, command= findMenuStart)
        self.btnCopyTL       = YoButton(   groupGames, text="copy tl files to translate")  #, command= copyTLStuff)
        # self.btnWordDic      = YoButton(   groupGames, text="word dic in tl folder")  # , command= lambda: makeRPYFiles())

        self.lbGameSelected.grid(row=0, column=0, sticky="N", padx=3, pady=3)
        self.cbGameFolder.grid(  row=0, column=0, sticky='NWES', padx=3)
        self.cbGamesSort.grid(   row=0, column=1, sticky='NWES', padx=3)
        self.listGames.grid(     row=2, column=0, sticky="NWES", padx=3, pady=3, columnspan=1)
        self.btnGameRescan.grid( row=3, column=0, sticky='NWES')
        self.btnExtract.grid(    row=4, column=0, sticky='NWES')
        self.btnDecompile.grid(  row=5, column=0, sticky='NWES')
        self.btnFontsCopy.grid(  row=6, column=0, sticky='NWES')
        self.btnMenuFinder.grid( row=7, column=0, sticky='NWES')
        self.btnRunRenpy.grid(   row=8, column=0, sticky='NWES')
        self.btnCopyTL.grid(     row=9, column=0, sticky='NWES')
        # self.btnWordDic.grid(    row=10, column=0, sticky='NWES')

        self.lbGameSelected.configure( font=('Microsoft JhengHei UI', 12))
        #######################################################################################################
        #                                           2
        #######################################################################################################
        groupFiles = tk.LabelFrame(self, padx=3, pady=3, text="File List")
        groupFiles.grid(row=0, column=1, padx=3, pady=3, sticky='NWES')
        groupFiles.columnconfigure(0, weight=2, minsize=25)
        groupFiles.rowconfigure( 0, weight=2, pad=0)

        self.tabControl = ttk.Notebook( groupFiles)
        tab1            = ttk.Frame( self.tabControl)
        tab1.rowconfigure(0, weight=2, minsize=25)
        self.tabControl.add(tab1, text='Current')
        self.tabControl.grid(    row=0, column=0, sticky="NWES", padx=0, pady=0)

        self.tabList = {}
        for tName in settings['folderList']:
            tab = ttk.Frame( self.tabControl)
            sb  = ttk.Scrollbar( tab, orient=tk.VERTICAL)
            lb  = tk.Listbox( tab, selectmode=tk.NORMAL, height=4, width=45, font=("Consolas", 8), yscrollcommand=sb.set, bg=myGreay, fg=myBlack)

            lb.grid(row=0, column=0, sticky="NWES", padx=0, pady=0)
            lb.lastScan = 0
            sb.grid( row=0, column=1, sticky="NS")
            sb.config(command=lb.yview)
            tab.rowconfigure(0, weight=2, minsize=25)

            self.tabControl.add( tab, text=tName)
            self.tabList[tName] = {'tab': tab, 'sb': sb, 'lb': lb, }

        self.listFileSCy    = ttk.Scrollbar(tab1, orient=tk.VERTICAL)
        self.listFile       = tk.Listbox(   tab1, selectmode=tk.NORMAL, height=4, width=45, font=("Consolas", 8), yscrollcommand=self.listFileSCy.set)

        self.listFile.grid(    row=0, column=0, sticky="NWES", padx=0, pady=0)
        self.listFileSCy.grid( row=0, column=1, sticky="NS")
        self.listFileSCy.config(command=self.listFile.yview)

        lbPanel = ttk.Frame( groupFiles)  # , background="#99fb99")
        lbPanel.grid(row=1, column=0, sticky='NWES')  #, columnspan=2)
        lbPanel.columnconfigure(0, weight=2, minsize=10)

        self.btnTLScan      = YoButton(lbPanel, text="rescan tl folder")  # , command= lambda: rescanFolders())
        self.btnMakeTemp    = YoButton(lbPanel, text="make temp files")  # , command= lambda: makeTempFiles( fileStat))
        self.btnTranslate   = YoButton(lbPanel, text="translate temp files")  # , command= lambda: treatTranslate())
        self.btnMakeRPY     = YoButton(lbPanel, text="make renpy files")  # , command= lambda: makeRPYFiles())
        self.btnCopyRPY     = YoButton(lbPanel, text="copy renpy files back")  # , command= lambda: makeRPYFiles())
        self.btnRunGame     = YoButton(lbPanel, text="run selected game ")  # , command= btnRunGameClick)

        self.btnTLScan.grid(   row=0, column=0, sticky='NWES')
        self.btnMakeTemp.grid( row=1, column=0, sticky='NWES')
        self.btnTranslate.grid(row=2, column=0, sticky='NWES')
        self.btnMakeRPY.grid(  row=3, column=0, sticky='NWES')
        self.btnCopyRPY.grid(  row=4, column=0, sticky='NWES')
        self.btnRunGame.grid(  row=5, column=0, sticky='NWES')

        #######################################################################################################
        #                                           3
        #######################################################################################################
        groupTags = tk.LabelFrame(self, padx=3, pady=3, text="Tags list", width=15)
        groupTags.grid( row=0, column=2, padx=3, pady=3, sticky='NWES')

        groupTags.columnconfigure(0, weight=2, minsize=5)
        groupTags.columnconfigure(1, weight=2, minsize=5)
        groupTags.rowconfigure(   0, weight=2, pad=0)
        groupTags.rowconfigure(   1, weight=0, pad=0)

        self.textTag         = tk.Text( groupTags, font=("Consolas", 8), width=15)
        self.textEng         = tk.Text( groupTags, font=("Consolas", 8), width=15)

        self.textTag.grid( row=0, column=0, sticky='NWES', padx=5, columnspan=2)

        btnPanel            = ttk.Frame(groupTags)
        btnPanel.grid( row=2, column=0, columnspan=2, sticky='NWES')
        btnPanel.columnconfigure(0, weight=1)

        self.btnTagCopy      = YoButton( btnPanel, text=">>>>")
        self.btnTagClear     = YoButton( btnPanel, text="<<<<")
        self.btnTempRepl     = YoButton( btnPanel, text="tag replace")

        self.btnTagCopy.grid(  row=0, column=0, sticky='NWES', padx=0)
        self.btnTagClear.grid( row=1, column=0, sticky='NWES', padx=0)
        self.btnTempRepl.grid( row=2, column=0, sticky='NWES', padx=0)

        #######################################################################################################
        #                                           4
        #######################################################################################################
        groupComm       = tk.LabelFrame(self, text="Common", padx=3, pady=3)
        # groupComm       = ttk.LabelFrame(self, padx=3, pady=3, text="Common")
        groupComm.grid(row=0, column=3, padx=3, pady=3, sticky='NWES')
        groupComm.columnconfigure(0, weight=1, minsize=30)
        groupComm.rowconfigure(   2, weight=2, pad=0)

        lbPanel         = ttk.Frame( groupComm)  #, background="#99fb99")
        lbPanel.columnconfigure(6, weight=1, pad=5)
        lbPanel.columnconfigure(5, weight=0, pad=5)
        lbPanel.columnconfigure(4, weight=0, pad=5)
        lbPanel.grid( row=0, column=0, sticky='NWES')

        lbEnd           = ttk.Label( lbPanel, text="Закончим:")
        lbThou          = ttk.Label( lbPanel, text="Через:"   )
        lbLine          = ttk.Label( lbPanel, text="Строка:"  )
        lbSize          = ttk.Label( lbPanel, text="Размер:"  )

        self.lbStart    = ttk.Label( lbPanel, text="", width=8)  #.grid( row=0, sticky=tk.W, column=1)
        self.lbEnd      = ttk.Label( lbPanel, text="", width=8)  #.grid(   row=1, sticky=tk.W, column=1)
        self.lbLine     = ttk.Label( lbPanel, text="", width=17)  #.grid(  row=0, sticky=tk.W, column=3)
        self.lbLines    = ttk.Label( lbPanel, text="", width=17)  #.grid( row=1, sticky=tk.W, column=3)
        self.chTest     = ttk.Checkbutton( lbPanel, text="test Run", variable=self.testRun, onvalue=1, offvalue=0)
        self.chAllEcxt  = ttk.Checkbutton( lbPanel, text="extract all files", variable=self.allExctract, onvalue=1, offvalue=0)

        lbFrom          = ttk.Label(lbPanel, text="from:")
        llbTo           = ttk.Label(lbPanel, text="to:")
        self.optLang    = ttk.Combobox(  lbPanel, textvariable=self.lang,  values=self.languages, width=5, state='readonly')
        self.optTrans   = ttk.Combobox(  lbPanel, textvariable=self.trans, values=self.languages, width=5, state='readonly')

        self.pbTotal    = YoProgress( groupComm, mode="determinate", length=200, rootTitle=self)  # style='lbPBar')
        self.textLogsSCy = ttk.Scrollbar(groupComm, orient=tk.VERTICAL)
        self.textLogs   = YoTextBox( groupComm, height=4, width=53, yscrollcommand=self.textLogsSCy.set)
        self.textLogsSCy.config(command=self.textLogs.yview)

        lbEnd.grid(         row=0, sticky=tk.E)
        lbThou.grid(        row=1, sticky=tk.E)
        lbLine.grid(        row=0, column=2, sticky=tk.E)
        lbSize.grid(        row=1, column=2, sticky=tk.E)
        self.lbStart.grid(  row=0, column=1, sticky=tk.W)
        self.lbEnd.grid(    row=1, column=1, sticky=tk.W)
        self.lbLine.grid(   row=0, column=3, sticky=tk.W)
        self.lbLines.grid(  row=1, column=3, sticky=tk.W)
        self.chTest.grid(   row=0, column=6, sticky=tk.W)
        self.chAllEcxt.grid(row=1, column=6, sticky=tk.W)
        lbFrom.grid(        row=0, column=4, sticky=tk.E)
        llbTo.grid(         row=1, column=4, sticky=tk.E)
        self.optLang.grid(  row=0, column=5, sticky=tk.W)
        self.optTrans.grid( row=1, column=5, sticky=tk.W)

        self.pbTotal.grid(  row=1, column=0, sticky="NWSE", padx=5, pady=5, columnspan=2)
        self.textLogs.grid( row=2, column=0, sticky="NWSE", padx=5, pady=5)
        self.textLogsSCy.grid( row=2, column=1, sticky="NS")

        #######################################################################################################
        #                                                   5 test
        #######################################################################################################
        groupTest = tk.LabelFrame(self, text="Test frame", padx=3, pady=3)
        # groupTest.grid(row=0, column=4, padx=3, pady=3, sticky='NWES')
        groupTest.columnconfigure(0, weight=1, minsize=30)
        groupTest.rowconfigure(0, weight=2, pad=0)
        groupTest['bg'] = myGreay
        groupTest['fg'] = myBlack

        self.treeGames = YoTreeView( groupTest)
        self.treeGames.grid( row=0, column=0, sticky='NWES')
       
        self.treeGames["columns"] = ( 1, 2, 3, 4)
        self.treeGames.names      = ( "Name", "Date", "Type", "Size", 'New')

        self.treeGames.column("#0", width=95, minwidth=15, stretch=tk.NO, anchor=tk.W)
        self.treeGames.column( 1,   width=95, minwidth=15, stretch=tk.NO)
        self.treeGames.column( 2,   width=65, minwidth=15, stretch=tk.NO)
        self.treeGames.column( 3,   width=45, minwidth=15, stretch=tk.NO, anchor=tk.E)
        self.treeGames.column( 4,   width=75, minwidth=15, stretch=tk.NO, anchor=tk.N)

        data = []
        data.append(( "Folder 2", "23-Jun-17 11:05", "File folder", '', 'qwerty', ""))
        data.append(( "text.txt", "23-Jun-17 11:25", "TXT file", "1 KB", 'dasdas'))
        data.append(( "photo1.png", "23-Jun-17 11:28", "PNG file", "2.6 KB", '331'))
        data.append(( "photo2.png", "23-Jun-17 11:29", "PNG file", "3.2 KB", 312312))
        data.append(( "photo3.png", "23-Jun-17 11:30", "PNG file", "3.1 KB", 4444))
        data.append(( "photo4.png", "22-Jun-17 11:30", "PNG file", "4.1 KB", 5533))
        data.append(( "photo5.png", "23-Jun-17 11:28", "PNG file", "2.6 KB"))
        data.append(( "photo6.png", "23-Jun-17 11:29", "PNG file", "3.2 KB"))
        data.append(( "photo7.png", "23-Jun-17 11:30", "PNG file", "3.1 KB"))
        data.append(( "photo8.png", "22-Jun-17 11:30", "PNG file", "4.1 KB"))
        self.treeGames.insertData( data)
        # << TreeviewSelect >>
        # << TreeviewOpen >>
        # << TreeviewClose >>
        # A data column number is an index into an item’s option values list; a display column number is the column number in the tree where the values are displayed.Tree
        # labels are displayed in column  #0. If option displaycolumns is not set, then data column n is displayed in column #n+1. Again, column #0 always refers to the tree column.
        # https://docs.python.org/3/library/tkinter.ttk.html#treeview
        #######################################################################################################
        #                                                   6 test
        #######################################################################################################
        # vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        # vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        # vscrollbar.grid(row=0, column=4, padx=3, pady=3, sticky='NWES')
        #
        # canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        # canvas.grid(row=0, column=4, padx=3, pady=3, sticky='NWES')
        # vscrollbar.config(command=canvas.yview)
        #
        # # reset the view
        # canvas.xview_moveto(0)
        # canvas.yview_moveto(0)
        #
        # # create a frame inside the canvas which will be scrolled with it
        # self.interior = interior = tk.Frame(canvas)
        # interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        #######################################################################################################
        #                                                   style
        #######################################################################################################
        self['bg']          = myGreay
        self.listFile['bg'] = myGreay
        self.listFile['fg'] = myBlack
        self.textTag['bg']  = myGreay
        self.textEng['bg']  = myGreay
        self.textTag['fg']  = myBlack
        self.textEng['fg']  = myBlack

        groupComm['bg']     = myGreay
        groupTags['bg']     = myGreay
        groupGames['bg']    = myGreay
        groupFiles['bg']    = myGreay
        groupComm['fg']     = myBlack
        groupTags['fg']     = myBlack
        groupGames['fg']    = myBlack
        groupFiles['fg']    = myBlack

        style = ttk.Style( self)
        style.configure('TFrame', foreground=myBlack, background=myGreay)
        style.configure('TLabel', foreground=myBlack, background=myGreay)
        style.configure('TCheckbutton', foreground=myBlack, background=myGreay, activebackground=myRed, highlightbackground=myRed)
        style.configure('TButton', foreground=myBlack, background=myGreay, activebackground=myRed, highlightbackground=myRed)
        style.configure('TCombobox', foreground=myBlack, background=myGreay)
        style.configure('Treeview', foreground=myBlack, background=myGreay)
        style.configure('Horizontal.TProgressbar', foreground='red', background=myGreay)
        style.configure('Vertical.TScrollbar', foreground='red', background=myGreay, troughcolor=myRed)
        style.configure('TLabelFrame', foreground=myBlack, background=myGreay)
        style.configure('TNotebook', foreground=myBlack, background=myGreay)

        style.map('TCheckbutton', indicatoron=[('pressed', '#ececec'), ('selected', '#4a6984')])
        #######################################################################################################

    def askClearFolder(self, filePath, txt):
        import filesClass as files
        msgBox = mb.askquestion( 'Clear folder before run SDK?', txt) #, icon='question')
        if msgBox == 'yes':
            files.clearFolder( filePath, '*')

    def gameNameLabelReset( self):
        self.listGames.delete(0, tk.END)
        self.lbGameSelected.configure( foreground=myRed)
        self.lbGameSelected['text'] = 'None'

    def gameNameLabelSet(self):
        selected = self.listGames.selection_get()
        self.lbGameSelected.configure( foreground='#00f')
        self.lbGameSelected['text'] = selected[0:25]

    def listTLupdate( self, currentFile=0):
        if currentFile <= 0 or not isinstance( currentFile, int):
            result = self.listFile.get(0, tk.END)
            for i in range( len(result)):
                self.listFile.itemconfig( i, bg=myGreay)
        else:
            self.listFile.itemconfig( currentFile, bg=myBrown)

            if self.listFile.focus_get() is not self.listFile:
                self.listFile.see(currentFile)

    def tagsCopy( self):
        self.textTag.grid( row=0, column=0, sticky='NWES', padx=5, columnspan=1)
        self.textEng.grid( row=0, column=1, sticky='NWES', padx=5)

    def tagsClear( self, _event):
        self.textEng.delete( '1.0', tk.END)
        self.textEng.grid_forget()
        self.textTag.grid( row=0, column=0, sticky='NWES', padx=5, columnspan=2)

    def labelsSet(self, tl=0, ts=0, cl=0, cs=0, st=0, et=0 ):
        self.lbStart["text"]    = st
        self.lbEnd["text"]      = et
        self.lbLine['text']     = f'{cl:,} из {tl:,}'
        self.lbLines['text']    = f'{cs:,} из {ts:,}'

    def listFileUpdate( self, fileList, lb=None):
        i = 0
        totalSize = 0
        totalLine = 0
        if lb and isinstance( lb, tk.Listbox):
            listBox = lb
        else:
            listBox = self.listFile

        listBox.delete( 0, tk.END)
        listBox.insert(tk.END, f"  №|{'File':^25}|{'Size':^8}|{'Line':^6}")

        for _, fileValue in fileList.items():
            i += 1
            if 'lines' in fileValue:
                tLine = fileValue['lines']
                totalLine += tLine
            else:
                tLine = 0

            if 'size' in fileValue:
                tSize = fileValue['size']
                totalSize += tSize
            else:
                tSize = 0
            listBox.insert( tk.END, f"{i:3}|{fileValue['fileName']:<25.25}|{tSize:>8,}|{tLine:>6}")
        # if lb is None:
        #     self.labelsSet( totalLine, totalSize)

    def print( self, line, newLine=False, lastLine=False, tag=None):
        self.textLogs['state'] = tk.NORMAL
        if newLine:
            self.textLogs.insert( tk.END, f'[{time.strftime("%H:%M:%S")}]\n')

        self.textLogs.insert( tk.END, f'[{time.strftime("%H:%M:%S")}] {str( line)}\n', tag)
        logging.info( line)

        if lastLine:
            self.textLogs.insert( tk.END, f'[{time.strftime("%H:%M:%S")}]\n')

        if self.textLogs.focus_get() is not self.textLogs:
            self.textLogs.see( tk.END)
        self.textLogs['state'] = tk.DISABLED

    def updateUI( self):
        try:
            self.update()
            self.after(1000, self.updateUI)
        except KeyboardInterrupt:
            print('error')
            self.destroy()


def main():
    pass


if __name__ == "__main__":
    main()

    # s = ttk.Style()
    # style.configure('Wild.TButton', parent='claim',
    #             background='black',
    #             foreground='white',
    #             highlightthickness='20',
    #             font=('Helvetica', 8, 'bold'))
    # style.map('Wild.TButton',
    #       foreground=[('disabled', 'yellow'),
    #                   ('pressed', 'red'),
    #                   ('active', 'blue')],
    #       background=[('disabled', 'magenta'),
    #                   ('pressed', '!focus', 'cyan'),
    #                   ('active', 'green')],
    #       highlightcolor=[('focus', 'green'),
    #                       ('!focus', 'red')],
    #       relief=[('pressed', 'groove'),
    #               ('!pressed', 'ridge')])
    #
    # self.btnDecompile.configure( style='Wild.TButton')

    # _frame = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if not cls._frame:
    #         # print( '-=> New dic = ', cls._frame)
    #         cls._frame = object.__new__(cls)
    #     # else:
    #         # print( '-=> Take olld dic = ', cls._frame)
    #     # print( '-=> current dic = ', cls._frame)
    #     return cls._frame

    # from toolTip import CreateToolTip
    # def __new__(cls, *args, **kwargs):
    #     key = args[0]
    #     if not key in cls._dic:
    #         cls._dic[key] = object.__new__(cls)
    #     return cls._dic[key]
    #
    # def __new__(cls, *args, **kwargs):
    #     # if cls not in cls._frames:
    #     # print( '-=> New dic = ', cls._frames, cls)
    #     key = object.__new__(cls)
    #     cls._frames.append( key)
    #     # print("args = ", cls, args, __class__.__name__)
    #     return key

    # def __applytag__(lineID, line, tags, regex, widget):
    #     indexes = [(m.start(), m.end()) for m in re.finditer(regex, line)]
    #     if len( indexes) > 0:
    #         print( indexes, tags, regex, line)
    #     for ind, x in enumerate( indexes):
    #         print( ind, tags[ind])
    #         widget.tag_add( tags[ind], f'{lineID + 1}.{x[0]}', f'{lineID + 1}.{x[1]}')
    #         widget.tag_add( tags[ind], f'{lineID + 1}.{x[0]}', f'{lineID + 1}.{x[1]}')

# button1_ttp = CreateToolTip(self.btnTLScan,      'Делается автоматически при старте программы.\n Можно тыкать, если поменялись файлы в папке tl или просто скучно...')
# button2_ttp = CreateToolTip(self.btnMakeTemp,    'Делаем временные (temp) файлы в одноименной папке.\n Можно тыкать, если поменялись файлы в папке tl или накосячили с тэгами.'\
#                                                 ' Временные файлы создаются заново, считываясь из файлов в папке tl, ничего страшного.')
# button3_ttp = CreateToolTip(self.btnTempRepl,    'Замена тэгов во временных (temp) файлах на разумный текст.\n' \
#                                                 'Заменяем теги в квадратных скобках на свой вариант на английском (!!!) языке, для более качественного перевода, '\
#                                                 'например "[sister]" -=> "sister" ( что на что менять ищем в коде игры или вангуем).' \
#                                                 'Если пошло что-то не так то обновляем временные файлы предыдущей кнопкой, меняем тэги и тыкаем заново.\n' \
#                                                 'Если не меняли, то нажимать это и не надо...\n\n' \
#                                                 '!u - tag uppercase ("[mom!u]" = "MOM"),\n' \
#                                                 '!l - tag lowercase ("[MOM!l]" = "mom"),\n' \
#                                                 '!c - only first character ("[mom!c]" = "Mom")')
# button4_ttp = CreateToolTip(self.btnTranslate,   'Перевод временных файлов (temp) на русский язык (transl).')
# button5_ttp = CreateToolTip(self.btnMakeRPY,     'Сборка переведенных файлов (transl) в Ренпайские файлы (rpy) в папке transl.')
# button6_ttp = CreateToolTip(self.btnALL,         'Одна кнопка для всего. Нажимаем - получаем. Все просто и без затей.')
