# import os
import time
import logging

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mb

# from toolTip import CreateToolTip
from datetime import datetime


class YoFrame(tk.Tk):
    _frame = False

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

        logFileName = "logs\\mainlog_" + time.strftime("%Y.%m.%d") + '.log'

        logging.basicConfig(filename=logFileName, format='%(asctime)s %(message)s', datefmt='%Y.%m.%d %H:%M:%S', encoding='utf-8', level=logging.INFO)

        self.log     = logging
        self.testRun = tk.BooleanVar()
        self.testRun.set(0)

        self.allExctract = tk.BooleanVar()
        self.allExctract.set(0)

        self.languages = [
            "auto",
            "en",
            "es",
            "ru",
        ]

        self.lang = tk.StringVar()
        self.lang.set( self.languages[1])

        self.trans = tk.StringVar()
        self.trans.set( self.languages[3])

        self.minsize( 1300, 400)
        self.geometry("1500x600")

        self.columnconfigure(0, weight=0, minsize=50)
        self.columnconfigure(1, weight=0, minsize=50)
        self.columnconfigure(2, weight=0, minsize=50)
        self.columnconfigure(3, weight=1, minsize=50)
        self.rowconfigure(   0, weight=2, pad=5)
        self.rowconfigure(   1, weight=0, pad=5)

        #######################################################################################################
        groupGames = tk.LabelFrame(self, padx=3, pady=3, text="Game select")
        groupGames.grid(row=0, column=0, padx=3, pady=3, sticky='NWES')
        groupGames.columnconfigure(0, weight=2, minsize=25)
        groupGames.rowconfigure( 1, weight=2, pad=0)

        self.lbGameSelected  = tk.Label(   groupGames, text="None", font=('Tahoma', 12))
        self.listGames       = tk.Listbox( groupGames, selectmode=tk.NORMAL, height=4, width=32, font=( 'Tahoma', 10))
        self.btnGameRescan   = ttk.Button( groupGames, text="rescan game list")  #, command= lambda: self.btnClickCTRL( 'btnGameRescan' ))#, command= gamesScan)
        self.btnExtract      = ttk.Button( groupGames, text="extract rpyc/fonts")  #, command= buttonExtract)
        self.btnDecompile    = ttk.Button( groupGames, text="decompile rpyc->rpy")  #, command= buttonDecompile)
        self.btnRunRenpy     = ttk.Button( groupGames, text="run SDK to translate")  #, command= btnRunSDKClick)
        self.btnFontsCopy    = ttk.Button( groupGames, text="non rus fonts + myStuff")  #, command= scanInputFolder)
        self.btnMenuFinder   = ttk.Button( groupGames, text="make menu finder")  #, command= findMenuStart)
        self.btnCopyTL       = ttk.Button( groupGames, text="copy TL files to translate")  #, command= copyTLStuff)

        self.lbGameSelected.grid(row=0, column=0, sticky="N", padx=3, pady=3)
        self.listGames.grid(     row=1, column=0, sticky="NWES", padx=3, pady=3, columnspan=1)
        self.btnGameRescan.grid( row=2, column=0, sticky='NWES')
        self.btnExtract.grid(    row=3, column=0, sticky='NWES')
        self.btnDecompile.grid(  row=4, column=0, sticky='NWES')
        self.btnFontsCopy.grid(  row=5, column=0, sticky='NWES')
        self.btnMenuFinder.grid( row=6, column=0, sticky='NWES')
        self.btnRunRenpy.grid(   row=7, column=0, sticky='NWES')
        self.btnCopyTL.grid(     row=8, column=0, sticky='NWES')
        # self.listGames.bind('<Double-1>', listGamesDClick)
        #######################################################################################################
        self.groupFiles = tk.LabelFrame(self, padx=3, pady=3, text="File List")
        self.groupFiles.grid(row=0, column=1, padx=3, pady=3, sticky='NWES')
        self.groupFiles.columnconfigure(0, weight=2, minsize=25)
        self.groupFiles.rowconfigure( 0, weight=2, pad=0)

        self.listFileSCy    = tk.Scrollbar(self.groupFiles, orient=tk.VERTICAL, width=12)
        self.listFile       = tk.Listbox(  self.groupFiles, selectmode=tk.NORMAL, height=4, width=45, font=("Consolas", 8), yscrollcommand=self.listFileSCy.set)

        self.listFile.grid(    row=0, column=0, sticky="NWES", padx=5, pady=5)
        self.listFileSCy.grid( row=0, column=1, sticky="NS")

        self.listFileSCy.config(command=self.listFile.yview)

        #######################################################################################################
        groupTags = tk.LabelFrame(self, padx=3, pady=3, text="Tags list", width=31)
        groupTags.grid( row=0, column=2, padx=3, pady=3, sticky='NWES')

        groupTags.columnconfigure(0, weight=2, minsize=10)
        groupTags.columnconfigure(1, weight=2, minsize=10)
        groupTags.rowconfigure(   0, weight=2, pad=0)
        groupTags.rowconfigure(   1, weight=0, pad=0)

        self.textTag         = tk.Text( groupTags, font=("Consolas", 8), width=31)
        self.textEng         = tk.Text( groupTags, font=("Consolas", 8), width=25)

        self.textTag.grid( row=0, column=0, sticky='NWES', padx=5, columnspan=2)

        btnPanel = tk.Frame(groupTags, background="#99fb99")
        btnPanel.grid( row=2, column=0, columnspan=2, sticky='NWES')
        btnPanel.columnconfigure(0, weight=1, minsize=20)
        btnPanel.columnconfigure(1, weight=1, minsize=20)
        btnPanel.columnconfigure(2, weight=1, minsize=20)

        self.btnTagCopy      = ttk.Button( btnPanel, text=">>>>")
        self.btnTagClear     = ttk.Button( btnPanel, text="xxxx")
        self.btnTempRepl     = ttk.Button( btnPanel, text="tags replace")

        self.btnTagCopy.grid(  row=0, column=0, sticky='NWES', padx=0)
        self.btnTagClear.grid( row=0, column=1, sticky='NWES', padx=0)
        self.btnTempRepl.grid( row=0, column=2, sticky='NWES', padx=0)
        #######################################################################################################

        groupComm       = tk.LabelFrame(self, padx=3, pady=3, text="Common")
        groupComm.grid(row=0, column=3, padx=3, pady=3, sticky='NWES')
        groupComm.columnconfigure(0, weight=1, minsize=30)
        groupComm.rowconfigure(   2, weight=2, pad=0)

        lbPanel         = tk.Frame( groupComm)  #, background="#99fb99")
        lbPanel.columnconfigure(6, weight=1, minsize=10)
        lbPanel.grid( row=0, column=0, sticky='NWES')

        tk.Label( lbPanel, text="Закончим:").grid(row=0, sticky=tk.E)
        tk.Label( lbPanel, text="Через:"   ).grid(row=1, sticky=tk.E)
        tk.Label( lbPanel, text="Строка:"  ).grid(row=0, sticky=tk.E, column=2)
        tk.Label( lbPanel, text="Размер:"  ).grid(row=1, sticky=tk.E, column=2)

        self.lbStart    = tk.Label( lbPanel, text="", width=8)  #.grid( row=0, sticky=tk.W, column=1)
        self.lbEnd      = tk.Label( lbPanel, text="", width=8)  #.grid(   row=1, sticky=tk.W, column=1)
        self.lbLine     = tk.Label( lbPanel, text="", width=17)  #.grid(  row=0, sticky=tk.W, column=3)
        self.lbLines    = tk.Label( lbPanel, text="", width=17)  #.grid( row=1, sticky=tk.W, column=3)
        self.chTest     = tk.Checkbutton( lbPanel, text="test Run", variable=self.testRun, onvalue=1, offvalue=0).grid(row=0, column=4, sticky=tk.W)
        self.chAllEcxt  = tk.Checkbutton( lbPanel, text="extract all files", variable=self.allExctract, onvalue=1, offvalue=0)

        tk.Label(lbPanel, text="from:").grid(row=0, column=5, sticky=tk.E)
        tk.Label(lbPanel, text="to:").grid(  row=1, column=5, sticky=tk.E)
        self.optLang    = tk.OptionMenu(  lbPanel, self.lang,  *self.languages).grid(row=0, column=6, sticky=tk.W)
        self.optTrans   = tk.OptionMenu(  lbPanel, self.trans, *self.languages).grid(row=1, column=6, sticky=tk.W)

        self.lbStart.grid(  row=0, sticky=tk.W, column=1)
        self.lbEnd.grid(    row=1, sticky=tk.W, column=1)
        self.lbLine.grid(   row=0, sticky=tk.W, column=3)
        self.lbLines.grid(  row=1, sticky=tk.W, column=3)
        self.chAllEcxt.grid(row=1, column=4, sticky=tk.W)

        self.stPBar          = ttk.Style( groupComm)
        self.stPBar.layout(   "lbPBar", [('lbPBar.trough', {'children': [('lbPBar.pbar', {'side': 'left', 'sticky': 'ns'}), ("lbPBar.label", {"sticky": ""})], 'sticky': 'nswe'})])
        self.stPBar.configure("lbPBar", text="0 %      ")

        self.pbTotal        = ttk.Progressbar( groupComm, mode="determinate", length=200, style='lbPBar')
        self.textLogsSCy    = tk.Scrollbar(groupComm, orient=tk.VERTICAL, width=12)
        self.textLogs       = tk.Text( groupComm, height=4, width=53, font=("Consolas", 8), yscrollcommand=self.textLogsSCy.set)

        self.pbTotal.grid(   row=1, column=0, sticky="NWSE", columnspan=2)
        self.textLogs.grid(  row=2, column=0, sticky="NWSE", padx=5, pady=5)
        self.textLogsSCy.grid( row=2, column=1, sticky="NS")
        self.textLogsSCy.config(command=self.textLogs.yview)

        self.textLogs.tag_configure("bold", font=("Consolas", 8, 'bold'), foreground='navy')
        self.textLogs.tag_configure("red", font=("Consolas", 8, 'bold'), foreground='red')

        #######################################################################################################
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

        # print( '\n'.join( dir( self.textLogs)))
    # def btnClickCTRL( self, btn):
    #     print( btn)
    #     from renTransFile import mainBtnClickCTR
    #     mainBtnClickCTR( self, btn)
    def gameListSet( self):
        result   = self.listGames.get(0, tk.END)
        selected = self.listGames.selection_get()

        self.lbGameSelected['fg'] = '#00f'
        self.lbGameSelected['text'] = selected[0:25]

        for i in range( len( result)):
            self.listGames.itemconfig( i, fg="#000", bg='#fff')
            if result[i] == selected:
                self.listGames.itemconfig( i, fg="#000", bg='#ddd')

    def listTLupdate( self, currentFile=0):

        if currentFile <= 0 or type( currentFile) != int:
            result = self.listFile.get(0, tk.END)
            for i in range(len(result)):
                self.listFile.itemconfig( i, fg="#000", bg='#fff')
        else:
            self.listFile.itemconfig( currentFile, fg="#000", bg='#ddd')

            if self.listFile.focus_get() is not self.listFile:
                self.listFile.see(currentFile)

        # for i in range( len( result) + 0):
        #     item = max( i -1, 1)
        #     if i <= currentFile:
        #         self.listFile.itemconfig( item, fg="#000", bg='#ddd')
        #     else:
        #         self.listFile.itemconfig( item, fg="#000", bg='#fff')

    def tagsCopy( self):
        self.textTag.grid( row=0, column=0, sticky='NWES', padx=5, columnspan=1)
        self.textEng.grid( row=0, column=1, sticky='NWES', padx=5)

    def tagsClear( self, event):
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
            if not self.focus_get(): # is not self.textLogs:
                mb.showinfo( "Work", 'Work complete!')
        return percentStr

    def progressUpdate( self, game):
        totalLine    = game.totalLines
        totalSize    = game.totalSize
        currentLine  = game.currentLine
        currentSize  = game.currentSize
        timeSTART    = game.timeSTART
        timeNOW      = datetime.today().timestamp()

        timeDelta    = timeNOW - timeSTART
        timeFinish   = ( totalLine * timeDelta) / currentLine
        timeEND      = timeSTART + timeFinish
        timeLaps     = timeFinish - timeDelta

        self.lbStart["text"] = datetime.fromtimestamp( timeEND).strftime( "%H:%M:%S")
        self.lbEnd["text"]   = datetime.utcfromtimestamp( timeLaps).strftime("%Mм %Sс")

        self.lbLine['text']  = '{:,} из {:,}'.format( currentLine, totalLine)
        self.lbLines['text'] = '{:,} из {:,}'.format( currentSize, totalSize)
        # percent         = str( round((( currentLine / totalLine) * 100), 2))
        self.pbSet(( currentLine / totalLine) * 100 , f'{game.currentFile}/{game.totalFiles}')

    def listFileUpdate( self, fileStat):
        i = 0
        totalSize = 0
        totalLine = 0
        self.listFile.delete(0, tk.END)
        self.listFile.insert( tk.END, "  №|{:^25}|{:^8}|{:^6}".format( 'File', 'Size', 'Lines'))

        for fileName in fileStat:
            i += 1

            if 'lines' in fileStat[fileName]:
                tLine = fileStat[fileName]['lines']
                totalLine += tLine
            else:
                tLine = 0

            if 'size' in fileStat[fileName]:
                tSize = fileStat[fileName]['size']
                totalSize += tSize
            else:
                tSize = 0

            self.listFile.insert( tk.END, "{:3}|{:<25.25}|{:>8,}|{:>6}".format( i, fileStat[fileName]['fileName'], tSize, tLine))

        self.lbLine['text']  = '{:,} из {:,}'.format( 0, totalLine)
        self.lbLines['text'] = '{:,} из {:,}'.format( 0, totalSize)

    def print( self, line, newLine=False, lastLine=False, tag=False):
        if newLine:
            self.textLogs.insert( tk.END, '[{}]\n'.format( time.strftime('%H:%M:%S')))

        self.textLogs.insert( tk.END, '[{}] {}\n'.format( time.strftime('%H:%M:%S'), str( line)), tag)
        logging.info( line)

        if lastLine:
            self.textLogs.insert( tk.END, '[{}]\n'.format( time.strftime('%H:%M:%S')))

        if self.textLogs.focus_get() is not self.textLogs:
            self.textLogs.see( tk.END)

    def updateUI( self):
        self.update()
        self.after(1000, self.updateUI)


def main():
    pass


if __name__ == "__main__":
    main()
