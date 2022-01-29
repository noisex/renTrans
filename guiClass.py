# import os
import os
import re
import time
import logging

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from settings import settings
# from toolTip import CreateToolTip


class YoTextBox(tk.Text):
    def __init__(self, *args, **kwargs):
        self.re = re.compile( r'`(\w+?)`(.+?)`')

        kwargs['bg'] = '#e1e1e1'
        kwargs['fg'] = '#292929'
        kwargs['font'] = ("Consolas", 8)

        tk.Text.__init__(self, *args, **kwargs)

        self.lastLine = 0
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.bind('<<TextModified>>', self.__textchanged__)

        self.tag_configure("bold", font=("Consolas", 8, 'bold'), foreground='#292929')
        self.tag_configure("red", font=("Consolas", 8, 'bold'), foreground='red')
        self.tag_configure("green", font=("Consolas", 8, 'bold'), foreground='green')
        self.tag_configure("navy", font=("Consolas", 8, 'bold'), foreground='navy')

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)
        # print( command, args)
        if command in "insert":   #, "replace"):
            self.event_generate("<<TextModified>>")
        return result

    def __textchanged__(self, evt):
        self.lastLine += 1
        line = evt.widget.get( f'{self.lastLine}.0', 'end-2c')
        fix  = re.findall( self.re, line)
        if len( fix) >= 1:
            dicTags = {}
            for ind, tagFind in enumerate( fix):
                tag, tagText = tagFind
                if tag in evt.widget.tag_names() and len( tagText) >= 1:
                    m = line.find( f"`{tag}`")
                    dicTags[ind] = { 'tag': tag, 'start': m, 'end': m + len( tagText)}
                # тут, если неправилььный тэг, то надо тоже его вырезать
                line = line.replace(f'`{tag}`', '', 1).replace('`', '', 1)
            self.replace(f'{self.lastLine}.0', 'end-2c', line)

            for _, tags in dicTags.items():
                self.tag_add(tags["tag"], f'{self.lastLine}.{tags["start"]}', f'{self.lastLine}.{tags["end"]}')

    # def __applytag__(lineID, line, tags, regex, widget):
        # indexes = [(m.start(), m.end()) for m in re.finditer(regex, line)]
        # if len( indexes) > 0:
        #     print( indexes, tags, regex, line)
        # for ind, x in enumerate( indexes):
            # print( ind, tags[ind])
            # widget.tag_add( tags[ind], f'{lineID + 1}.{x[0]}', f'{lineID + 1}.{x[1]}')
            # widget.tag_add( tags[ind], f'{lineID + 1}.{x[0]}', f'{lineID + 1}.{x[1]}')


class YoListBox(tk.Listbox):
    def __init__(self, parent, **kwargs):
        myGreay = '#e1e1e1'
        myBlack = '#292929'
        kwargs['bg'] = myGreay
        kwargs['fg'] = myBlack
        kwargs['font'] = ( 'Microsoft JhengHei UI', 10)

        super().__init__(parent, **kwargs)
        self.bind('<Double-Button-1>',  self.callback)

    # todo переписать на юзать листобсовые итемы, а не Резалт
    def callback(self, _event):
        result = self.get(0, tk.END)
        selected = self.selection_get()
        self.configure(foreground='#00f')
        for i, _ in enumerate(result):
            self.itemconfig(i, fg="#000", bg='#e1e1e1')
            if result[i] == selected:
                self.itemconfig(i, fg="#000", bg='#bbb')
        # print (        u'Нажата кнопка', event) #.widget['text'])


class YoFrame(tk.Tk):
    _frame = None

    def __new__(cls, *args, **kwargs):
        if not cls._frame:
            # print( '-=> New dic = ', cls._frame)
            cls._frame = object.__new__(cls)
        # else:
            # print( '-=> Take olld dic = ', cls._frame)
        # print( '-=> current dic = ', cls._frame)
        return cls._frame

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

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
        ]

        self.lang = tk.StringVar()
        self.lang.set( self.languages[1])

        self.trans = tk.StringVar()
        self.trans.set( self.languages[3])

        self.gameFolder = tk.StringVar()
        self.gameFolder.set( settings['gameFolderList'][0])

        self.minsize( 1300, 400)
        self.geometry("1450x650")

        self.columnconfigure(3, weight=1, minsize=50)
        self.rowconfigure(   0, weight=2, pad=5)
        self.rowconfigure(   1, weight=0, pad=5)

        #######################################################################################################
        #                                           1
        #######################################################################################################
        groupGames = tk.LabelFrame(self, padx=3, pady=3, text="Game select")
        groupGames.grid(row=0, column=0, padx=3, pady=3, sticky='NWES')
        groupGames.columnconfigure(0, weight=2, minsize=25)
        groupGames.rowconfigure( 2, weight=2, pad=0)

        self.lbGameSelected  = ttk.Label(    groupGames, text="None")  #, font=('Microsoft JhengHei UI', 12))
        self.cbGameFolder    = ttk.Combobox( groupGames, textvariable=self.gameFolder,  values=settings['gameFolderList'], width=5, state='readonly')
        self.listGames       = YoListBox(    groupGames, selectmode=tk.NORMAL, height=4, width=32, )
        self.btnGameRescan   = ttk.Button(   groupGames, text="rescan game list")  #, command= lambda: self.btnClickCTRL( 'btnGameRescan' ))#, command= gamesScan)
        self.btnExtract      = ttk.Button(   groupGames, text="extract rpyc/fonts")  #, command= buttonExtract)
        self.btnDecompile    = ttk.Button(   groupGames, text="decompile rpyc->rpy")  #, command= buttonDecompile)
        self.btnRunRenpy     = ttk.Button(   groupGames, text="run SDK to translate")  #, command= btnRunSDKClick)
        self.btnFontsCopy    = ttk.Button(   groupGames, text="non rus fonts + myStuff")  #, command= scanInputFolder)
        self.btnMenuFinder   = ttk.Button(   groupGames, text="make menu finder")  #, command= findMenuStart)
        self.btnCopyTL       = ttk.Button(   groupGames, text="copy tl files to translate")  #, command= copyTLStuff)
        self.btnWordDic      = ttk.Button(   groupGames, text="word dic in tl folder")  # , command= lambda: makeRPYFiles())

        self.lbGameSelected.grid(row=0, column=0, sticky="N", padx=3, pady=3)
        self.cbGameFolder.grid(  row=1, column=0, sticky='NWES', padx=3, pady=3)
        self.listGames.grid(     row=2, column=0, sticky="NWES", padx=3, pady=3, columnspan=1)
        self.btnGameRescan.grid( row=3, column=0, sticky='NWES')
        self.btnExtract.grid(    row=4, column=0, sticky='NWES')
        self.btnDecompile.grid(  row=5, column=0, sticky='NWES')
        self.btnFontsCopy.grid(  row=6, column=0, sticky='NWES')
        self.btnMenuFinder.grid( row=7, column=0, sticky='NWES')
        self.btnRunRenpy.grid(   row=8, column=0, sticky='NWES')
        self.btnCopyTL.grid(     row=9, column=0, sticky='NWES')
        self.btnWordDic.grid(    row=10, column=0, sticky='NWES')

        self.lbGameSelected.configure( font=('Microsoft JhengHei UI', 12))
        #######################################################################################################
        #                                           2
        #######################################################################################################
        groupFiles = tk.LabelFrame(self, padx=3, pady=3, text="File List")
        groupFiles.grid(row=0, column=1, padx=3, pady=3, sticky='NWES')
        groupFiles.columnconfigure(0, weight=2, minsize=25)
        groupFiles.rowconfigure( 0, weight=2, pad=0)

        self.listFileSCy    = ttk.Scrollbar(groupFiles, orient=tk.VERTICAL)
        self.listFile       = tk.Listbox(   groupFiles, selectmode=tk.NORMAL, height=4, width=45, font=("Consolas", 8), yscrollcommand=self.listFileSCy.set)

        self.listFile.grid(    row=0, column=0, sticky="NWES", padx=5, pady=5)
        self.listFileSCy.grid( row=0, column=1, sticky="NS")
        self.listFileSCy.config(command=self.listFile.yview)

        lbPanel = ttk.Frame( groupFiles)  # , background="#99fb99")
        lbPanel.grid(row=1, column=0, sticky='NWES', columnspan=2)
        lbPanel.columnconfigure(0, weight=2, minsize=10)

        self.btnTLScan      = ttk.Button(lbPanel, text="rescan tl folder")  # , command= lambda: rescanFolders())
        self.btnMakeTemp    = ttk.Button(lbPanel, text="make temp files")  # , command= lambda: makeTempFiles( fileStat))
        self.btnTranslate   = ttk.Button(lbPanel, text="translate temp files")  # , command= lambda: treatTranslate())
        self.btnMakeRPY     = ttk.Button(lbPanel, text="make renpy files")  # , command= lambda: makeRPYFiles())
        self.btnCopyRPY     = ttk.Button(lbPanel, text="copy renpy files back")  # , command= lambda: makeRPYFiles())
        self.btnRunGame     = ttk.Button(lbPanel, text="run selected game ")  # , command= btnRunGameClick)

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

        self.btnTagCopy      = ttk.Button( btnPanel, text=">>>")
        self.btnTagClear     = ttk.Button( btnPanel, text="xxx")
        self.btnTempRepl     = ttk.Button( btnPanel, text="tag replace")

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
        lbPanel.columnconfigure(6, weight=1, minsize=10)
        lbPanel.grid( row=0, column=0, sticky='NWES')

        lbEnd   = ttk.Label( lbPanel, text="Закончим:")
        lbThou  = ttk.Label( lbPanel, text="Через:"   )
        lbLine  = ttk.Label( lbPanel, text="Строка:"  )
        lbSize  = ttk.Label( lbPanel, text="Размер:"  )

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

        lbEnd.grid( row=0, sticky=tk.E)
        lbThou.grid(row=1, sticky=tk.E)
        lbLine.grid(row=0, sticky=tk.E, column=2)
        lbSize.grid(row=1, sticky=tk.E, column=2)
        lbFrom.grid(row=0, sticky=tk.E, column=5)
        llbTo.grid( row=1, sticky=tk.E, column=5)

        self.lbStart.grid(  row=0, column=1, sticky=tk.W)
        self.lbEnd.grid(    row=1, column=1, sticky=tk.W)
        self.lbLine.grid(   row=0, column=3, sticky=tk.W)
        self.lbLines.grid(  row=1, column=3, sticky=tk.W)
        self.chTest.grid(   row=0, column=4, sticky=tk.W)
        self.chAllEcxt.grid(row=1, column=4, sticky=tk.W)
        self.optLang.grid(  row=0, column=6, sticky=tk.W)
        self.optTrans.grid( row=1, column=6, sticky=tk.W)

        self.stPBar          = ttk.Style( groupComm)
        self.stPBar.layout(   "lbPBar", [('lbPBar.trough', {'children': [('lbPBar.pbar', {'side': 'left', 'sticky': 'ns'}), ("lbPBar.label", {"sticky": "ns"})], 'sticky': 'NWSE'})])
        self.stPBar.configure("lbPBar", text="0%")  #, relief='sunken')

        self.pbTotal        = ttk.Progressbar( groupComm, mode="determinate", length=200, style='lbPBar')
        self.textLogsSCy    = ttk.Scrollbar(groupComm, orient=tk.VERTICAL)
        self.textLogs       = YoTextBox( groupComm, height=4, width=53, yscrollcommand=self.textLogsSCy.set)

        self.pbTotal.grid(   row=1, column=0, sticky="NWSE", padx=5, pady=5, columnspan=2)
        self.textLogs.grid(  row=2, column=0, sticky="NWSE", padx=5, pady=5)
        self.textLogsSCy.grid( row=2, column=1, sticky="NS")
        self.textLogsSCy.config(command=self.textLogs.yview)

        #######################################################################################################
        #                                                   style
        #######################################################################################################
        myGreay = '#e1e1e1'
        myBlack = '#292929'
        myRed = 'red'

        self['bg'] = myGreay
        self.listFile['bg'] = myGreay
        self.listFile['fg'] = myBlack

        groupComm['bg']       = myGreay
        groupTags['bg']       = myGreay
        groupGames['bg']      = myGreay
        groupFiles['bg'] = myGreay
        groupComm['fg']       = myBlack
        groupTags['fg']       = myBlack
        groupGames['fg']      = myBlack
        groupFiles['fg'] = myBlack

        # self.textLogs['bg'] = myGreay
        self.textTag['bg'] = myGreay
        self.textEng['bg'] = myGreay
        # self.textLogs['fg'] = myBlack
        self.textTag['fg'] = myBlack
        self.textEng['fg'] = myBlack

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

        style.map('TCheckbutton', indicatoron=[('pressed', '#ececec'), ('selected', '#4a6984')])
        # groupComm.configure( style='groupComm.TLabelFrame')

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
        #######################################################################################################

    def gameNameLabelSet(self):
        selected = self.listGames.selection_get()
        self.lbGameSelected.configure( foreground='#00f')
        self.lbGameSelected['text'] = selected[0:25]

    def listTLupdate( self, currentFile=0):
        if currentFile <= 0 or not isinstance( currentFile, int):
            result = self.listFile.get(0, tk.END)
            for i in range( len(result)):
                self.listFile.itemconfig( i, fg="#000", bg='#e1e1e1')
        else:
            self.listFile.itemconfig( currentFile, fg="#000", bg='#bbb')

            if self.listFile.focus_get() is not self.listFile:
                self.listFile.see(currentFile)

    def tagsCopy( self):
        self.textTag.grid( row=0, column=0, sticky='NWES', padx=5, columnspan=1)
        self.textEng.grid( row=0, column=1, sticky='NWES', padx=5)

    def tagsClear( self, _event):
        self.textEng.delete( '1.0', tk.END)
        self.textEng.grid_forget()
        self.textTag.grid( row=0, column=0, sticky='NWES', padx=5, columnspan=2)

    def pbReset( self):
        self.pbTotal['value'] = 0
        self.stPBar.configure("lbPBar", text="0%      ")

    def pbSet( self, percent=0, titleText=''):
        percentStr = str( round( percent, 2))
        self.pbTotal['value'] = percentStr
        self.title( f'{percentStr}% [{titleText}]')
        self.stPBar.configure("lbPBar", text=percentStr + "%      ")
        if percent >= 100:
            self.print('Work complete.', True)
            if not self.focus_get():  # is not self.textLogs:
                mb.showinfo( "Work", 'Work complete!')
        return percentStr

    def listFileUpdate( self, fileStat):
        i = 0
        totalSize = 0
        totalLine = 0
        self.listFile.delete( 0, tk.END)
        self.listFile.insert( tk.END, f"  №|{'File':^25}|{'Size':^8}|{'Line':^6}")

        for _, fileValue in fileStat.items():
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
            self.listFile.insert( tk.END, f"{i:3}|{fileValue['fileName']:<25.25}|{tSize:>8,}|{tLine:>6}")

        self.lbLine['text']  = f'{0:,} из {totalLine:,}'
        self.lbLines['text'] = f'{0:,} из {totalSize:,}'

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
