# from guiClass import yoFrame
import os
# from itertools import (takewhile,repeat)
# import tkinter as tk
import tkinter.ttk as ttk
from itertools import takewhile, repeat

from unrpa import UnRPA
from settings import settings

class translator:
    def __init__(self, app, game) -> None:
        # print( '-=> Make new game', app, game)
        self.app = app
        self.game = game

        self.app.groupFiles.rowconfigure( 1, weight=0, pad=0)
        self.app.groupFiles.rowconfigure( 2, weight=0, pad=0)
        self.app.groupFiles.rowconfigure( 3, weight=0, pad=0)
        self.app.groupFiles.rowconfigure( 4, weight=0, pad=0)
        self.app.groupFiles.rowconfigure( 5, weight=0, pad=0)

        self.app.btnTLScan       = ttk.Button( self.app.groupFiles, text="rescan tl folder",   width=15)#, command= lambda: rescanFolders())
        self.app.btnMakeTemp     = ttk.Button( self.app.groupFiles, text="make temp files",    width=15)#, command= lambda: makeTempFiles( fileStat))
        self.app.btnTranslate    = ttk.Button( self.app.groupFiles, text="translate start",    width=25)#, command= lambda: treatTranslate())
        self.app.btnMakeRPY      = ttk.Button( self.app.groupFiles, text="make Renpy files",   width=25)#, command= lambda: makeRPYFiles())
        # self.app.btnALL          = ttk.Button( self.app.btnPanel, text="just Translate",     width=25)#, command= makeALLFiles)
        self.app.btnRunGame      = ttk.Button( self.app.groupFiles, text="run selected game ",    width=15)#, command= btnRunGameClick)

        self.app.btnTLScan.grid(    row=1, column=0, sticky='NWES')
        self.app.btnMakeTemp.grid(  row=2, column=0, sticky='NWES')
        self.app.btnTranslate.grid( row=3, column=0, sticky='NWES')
        self.app.btnMakeRPY.grid(   row=4, column=0, sticky='NWES')
        # self.app.btnALL.grid(      row=0, column=2, sticky='NWES')
        self.app.btnRunGame.grid(   row=5, column=0, sticky='NWES')

        self.app.btnTranslate.bind( '<Button-1>', self.treatTranslate)
        self.app.btnMakeRPY.bind(   '<Button-1>', self.makeRPYFiles)
        # self.app.btnALL.bind(       '<Button-1>', self.makeALLFiles)




    def rawincount(self, filename):
        f = open(filename, 'rb')
        bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
        return sum( buf.count(b'\n') for buf in bufgen )

    def treatTranslate( self, event):
        path    = self.game.folderTEMP
        tlist   = self.game.getListFilesByExt( '.tmp', path)
        fs = {
            'files':{},
            "stats": {
                'files': 0,
                'lines': 0,
                'size': 0,
            }
        }

        for filename in tlist:
            file    = filename.replace( path + '\\', '')
            basename= os.path.splitext( file)[0]
            lines   = self.rawincount(filename)
            size    = os.path.getsize(  filename)
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


class rpaClass:
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


    def rpaExtractFiles(self, fileList: dict, pathGame: str ) -> None:
        for fileName in fileList:
            self.app.print(f'Extracting from {fileName}...', True)
            UnRPA(fileName, path=pathGame).extract_files('.', fileList[fileName], self.app)


    def rpaGetListFilesExt(self, fileList:dict) -> dict:
        dicRPA = {}
        for fileName in fileList:
            archNames   = UnRPA(fileName).list_files()

            for fileArchName in archNames:
                if ( self.app.allExctract.get()) or ( os.path.splitext( fileArchName)[1].lower() in self.extension):
                    if fileName not in dicRPA:
                        dicRPA[fileName] = []
                    dicRPA[fileName].append( fileArchName)
        return dicRPA


    def rpaGetFilesStats(self, fileList:dict) -> dict:
        dicRPA = {}
        for fileName in fileList:
            # shorFileName = os.path.basename( fileName)
            archNames   = UnRPA(fileName).list_files()
            rpycFiles   = 0
            fontsFiles  = 0

            for fileArchName in archNames:
                extention = os.path.splitext(fileArchName)[1].lower()
                if  extention == '.rpyc':
                    rpycFiles += 1
                elif extention in '.ttf, .otf':
                    fontsFiles += 1

            dicRPA[fileList[fileName]['fileName']] = {
                'size'      : os.path.getsize(fileName) / (1024 * 1024),
                'count'     : len(archNames),
                'rpycFiles' : rpycFiles,
                'fontsFiles': fontsFiles,
            }
        return dicRPA

def main():
    pass

if __name__ == '__main__':
    main()