# from guiClass import yoFrame
import os
# from itertools import (takewhile,repeat)
import tkinter as tk
import tkinter.ttk as ttk
from itertools import takewhile, repeat

from unrpa import UnRPA
from settings import settings


class Translator:
    def __init__(self, app, game) -> None:
        # print( '-=> Make new game', app, game)
        self.app = app
        self.game = game

        lbPanel = tk.Frame( self.app.groupFiles)  #, background="#99fb99")
        lbPanel.grid(row=1, column=0, sticky='NWES', columnspan=2)
        lbPanel.columnconfigure(0, weight=2, minsize=10)

        self.app.btnTLScan       = ttk.Button( lbPanel, text="rescan tl folder")  #, command= lambda: rescanFolders())
        self.app.btnMakeTemp     = ttk.Button( lbPanel, text="make temp files")  #, command= lambda: makeTempFiles( fileStat))
        self.app.btnTranslate    = ttk.Button( lbPanel, text="translate start")  #, command= lambda: treatTranslate())
        self.app.btnMakeRPY      = ttk.Button( lbPanel, text="make Renpy files")  #, command= lambda: makeRPYFiles())
        self.app.btnRunGame      = ttk.Button( lbPanel, text="run selected game ")  #, command= btnRunGameClick)

        self.app.btnTLScan.grid(    row=0, column=0, sticky='NWES')
        self.app.btnMakeTemp.grid(  row=1, column=0, sticky='NWES')
        self.app.btnTranslate.grid( row=2, column=0, sticky='NWES')
        self.app.btnMakeRPY.grid(   row=3, column=0, sticky='NWES')
        self.app.btnRunGame.grid(   row=4, column=0, sticky='NWES')

        # self.app.btnTranslate.bind( '<Button-1>', self.treatTranslate)
        # self.app.btnMakeRPY.bind(   '<Button-1>', self.makeRPYFiles)
        # self.app.btnALL.bind(       '<Button-1>', self.makeALLFiles)

    @staticmethod
    def rawincount(filename):
        f = open(filename, 'rb')
        bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
        return sum( buf.count(b'\n') for buf in bufgen)

    def treatTranslate( self, event):
        path    = self.game.folderTEMP
        tlist   = self.game.getListFilesByExt( '.tmp', path)
        fs = {
            'files': {},
            "stats": {
                'files': 0,
                'lines': 0,
                'size': 0,
            }
        }

        for filename in tlist:
            file     = filename.replace( path + '\\', '')
            basename = os.path.splitext( file)[0]
            lines    = self.rawincount(filename)
            size     = os.path.getsize(  filename)
            # print( filename, basename, file + '.tranl', lines, size)
            fs['files'][filename] = {
                'filename': filename,
                'file': file,
                'basename': basename,
            }

            fs['stats']['files'] += 1
            fs['stats']['lines'] += lines
            fs['stats']['size']  += size

        # print( fs)
        # for item in fs:
        #     print( item, len( fs[item]), fs[item])

        # for item in fs['files']:
        #     print( item, fs['files'][item])
        # print( f'\nfiles={files} - lines={line} - size={sizes}')

    def makeRPYFiles( self, event):
        pass

    def makeALLFiles( self, event):
        pass


class RPAClass:
    def __init__(self, app, game) -> None:
        # print( '-=> Make new game', app, game)
        self.app = app
        self.game = game
        self.extension = settings['extension']

    # def setNewFileInRPA(self, fileList, fileName, size, count):
    #     fileList[fileName] = {
    #         'size'  : size,
    #         'count' : count,
    #         'files' : []
    #     }
    #     return  fileList

    def rpaExtractFiles(self, fileList: dict, pathGame: str) -> None:
        for fileName in fileList:
            self.app.print(f'Extracting from {fileName}...', True)
            try:
                UnRPA(fileName, path=pathGame).extract_files('.', fileList[fileName], self.app)
            except (Exception,):
                self.app.print( f'ERROR. Can`t open file [{fileName}]')

    def rpaGetListFilesExt(self, fileList: dict) -> dict:
        dicRPA = {}
        for fileName in fileList:
            try:
                archNames   = UnRPA(fileName).list_files()

                for fileArchName in archNames:
                    if ( self.app.allExctract.get()) or ( os.path.splitext( fileArchName)[1].lower() in self.extension):
                        if fileName not in dicRPA:
                            dicRPA[fileName] = []
                        dicRPA[fileName].append( fileArchName)
            except (Exception,):
                self.app.print( f'ERROR. Can`t open file [{fileName}]')

        return dicRPA

    def rpaGetFilesStats(self, fileList: dict) -> dict:
        dicRPA = {}
        for fileName in fileList:
            # shorFileName = os.path.basename( fileName)
            try:
                archNames   = UnRPA(fileName).list_files()
                rpycFiles   = 0
                fontsFiles  = 0

                for fileArchName in archNames:
                    extention = os.path.splitext(fileArchName)[1].lower()
                    if extention == '.rpyc':
                        rpycFiles += 1
                    elif extention in '.ttf, .otf':
                        fontsFiles += 1

                dicRPA[fileList[fileName]['fileName']] = {
                    'size'      : os.path.getsize(fileName) / (1024 * 1024),
                    'count'     : len(archNames),
                    'rpycFiles' : rpycFiles,
                    'fontsFiles': fontsFiles,
                }
            except (Exception,):
                self.app.print( f'ERROR. Can`t open file [{fileName}]')

        return dicRPA


def main():
    pass


if __name__ == '__main__':
    main()
