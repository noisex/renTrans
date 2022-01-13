import os
import shutil
import tkinter as tk
# import tkinter.ttk as ttk
from settings import settings
# from itertools import (takewhile,repeat)
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError

class gameRenpy():
    def __init__(self, app, *args, **kwargs):
        # tk.Tk.__init__(self, *args, **kwargs)
        self.backupFolderTemplate = 'Backup'
        self.gameFolder     = settings['gameFolder'] #'D:\\AdGames\\'
        self.backupFolder   = settings['backupFolder'] #Backup'
        self.folderTL       = settings['folderTL'] #'workFolder\\tl\\'
        self.folderTEMP     = settings['folderTEMP'] #'workFolder\\temp\\'
        self.folderTRANS    = settings['folderTRANS'] #'workFolder\\trans\\'
        self.folderRPY      = settings['folderRPY'] #'workFolder\\tl_done\\'
        self.rootPath       = os.path.abspath(os.getcwd()) + '\\'  # C:\GitHub\renTrans\
        self.sdkFolder      = self.rootPath + settings['sdkFolder']
        self.fileSkip       = settings['fileSkip']

        self.app            = app
        self.gameName       = False
        self.path           = False
        self.gamePath       = False
        self.shortPath      = False
        # self.fullGamePath   = False
        self.totalLines     = 0
        self.totalSize      = 0
        self.totalFiles     = 0
        self.currentLine    = 0
        self.currentSize    = 0
        self.currentFile    = 0
        self.timeSTART      = 0
        self.wordDicCount   = 0

        self.makeNewDirs()

    def lineTransate( self, oLine, currentFileLine='noNum', file='noFile'):
        tLine = False
        try:
            tLine = GoogleTranslator( source=self.app.lang.get(), target='ru').translate( oLine) + '\n'

        except RequestError as e:
            self.app.print( f'-=> ERROR: {e} -=> line: {currentFileLine} ( {len( oLine)}b) at [{file}]')
            # print( oLine)
            threadSTOP.do_run = False
            tLine = oLine

        except Exception as error:
            self.app.print( f'ERROR -=> line: {currentFileLine} ( {len(oLine)}b) at [{file}] ({error})' )
            tLine = oLine
            # print(oLine)
            threadSTOP.do_run = False
        return tLine


    def makeNewDirs( self):
        if not os.path.exists( self.folderRPY):                                   # создаем дирректорию для файлов с переводом (если нужно)
            os.mkdir( self.folderRPY)
            self.app.print( f'Папка {self.folderRPY} - из нее забираем перевод')
        if not os.path.exists( self.folderTL):                                       # создаем дирректорию для файлов с переводом (если нужно)
            os.mkdir( self.folderTL)
            self.app.print( f'Папка {self.folderTL} - в нее кладем файлы для перевода')
        if not os.path.exists( self.folderTEMP):                                       # создаем дирректорию для файлов с переводом (если нужно)
            os.mkdir( self.folderTEMP)
            self.app.print( f'Папка {self.folderTEMP} - она просто нужна...')
        if not os.path.exists( self.folderTRANS):                                       # создаем дирректорию для файлов с переводом (если нужно)
            os.mkdir( self.folderTRANS)
            self.app.print( f'Папка {self.folderTRANS} - она просто нужна...')


    def makeNewBackupFolder( self):
        self.backupFolder = self.backupFolderTemplate
        i = 0
        while os.path.exists( self.getPath() + self.backupFolder):                  # приписывает число к имени, если есть такой файл
            i += 1
            self.backupFolder = '{} ({:02})'.format( self.backupFolderTemplate, i)
        # self.app.print( f'backup folder = {self.backupFolder}')

    def getBackupFolder( self):
        return self.backupFolder



    # def rawincount(self, filename):
    #     f = open(filename, 'rb')
    #     bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    #     return sum( buf.count(b'\n') for buf in bufgen )

    def getFileSize( self, fileName):
        fileSize = 0
        fileLine = 0
        for encode in settings['encList']:
            try:
                with open( fileName, encoding=encode) as f:
                    for line in f.read().split('\n'):
                        fileLine += 1
                        fileSize += len( line)
                    # print(encode, fileSize, fileLine)
                    return fileSize, fileLine
            except:
                pass
                # print( f' encode [{encode}] not good...')
                # enc_list.remove(encode)

        # with open( fileName, encoding='utf-8') as f:
        #     for line in f.read().split('\n'):
        #         fileLine += 1
        #         fileSize += len( line)
        # return fileSize, fileLine

    def getListFilesByExt( self, ext='.rpy', gamePath=None, withTL=True, withStat=False) -> dict:
        """"""
        if not gamePath:
            gamePath = self.getPathGame()

        gamePathTemp = 'TestDirs' + 'game\\tl' if withTL else 'game\\tl'

        if type( ext) == str:
            ext = ext.split( ', ')

        if withStat:
            self.totalLines = 0
            self.totalSize  = 0
            self.totalFiles = 0

        filesAll = {}

        for top, dirs, files in os.walk( gamePath):                           # Находим файлы для перевода в дирректории
            for fileName in files:
                if gamePathTemp not in top \
                    and os.path.splitext( fileName)[1] in ext \
                    and fileName not in self.fileSkip:

                    filePath = os.path.normpath( os.path.join( top, fileName))

                    filesAll[filePath] = {
                        'fileShort': filePath.replace( gamePath, ''),
                        'fileName':  os.path.basename( filePath)
                        }

                    if withStat:
                        # lines   = self.rawincount( filePath)
                        size, lines     = self.getFileSize( filePath) #os.path.getsize(  filePath)
                        self.totalLines += lines
                        self.totalSize  += size
                        self.totalFiles += 1
                        filesAll[filePath]['lines']= lines
                        filesAll[filePath]['size'] = size
        # print( dict(sorted(filesAll.items())))
        # print( filesAll)
        return dict( sorted( filesAll.items()))


    def listGameDClick( self):
        self.gameName       = self.app.listGames.selection_get()
        self.path           = self.gameFolder + self.gameName + '\\'
        self.gamePath       = self.gameFolder + self.gameName + '\\game\\'
        # self.shortPath      = self.path
        self.shortPath      = self.gameName + '\\'
        self.app.print( f'Game: {self.gameName}', True, tag='bold')
        if os.path.exists( self.gamePath + '\\tl\\rus\\'):
            self.app.print( '-=> with [RUS] tl folder')
        if os.path.exists( self.gamePath + '\\tl\\russian\\'):
            self.app.print( '-=> with [RUSSIAN] tl folder')
        if os.path.exists( self.gamePath + '\\tl\\en\\'):
            self.app.print( '-=> with [EN] tl folder')
        if os.path.exists( self.gamePath + '\\tl\\english\\'):
            self.app.print( '-=> with [ENGLISH] tl folder')


    def gameListScan( self, event):
        self.app.listGames.delete(0, tk.END)
        self.app.lbGameSelected['fg'] ='#f00'
        self.app.lbGameSelected['text'] = 'None'

        with os.scandir( self.gameFolder) as list:
            for dirName in list:
                if dirName.is_dir() and os.path.exists( f'{self.gameFolder}{dirName.name}\\game\\') and os.path.exists( f'{self.gameFolder}{dirName.name}\\renpy\\'):
                    self.app.listGames.insert( tk.END, dirName.name)


    # TODO rewrite listwalk vs listdir
    @staticmethod
    def clearFolder(fileExt='.rpy', dirName= str):
        if fileExt == '*':
            shutil.rmtree( dirName)
        else:
            test = os.listdir(dirName)
            for item in test:
                if item.endswith( fileExt):
                    os.remove(os.path.join(dirName, item))

    def checkSelectedGame( self):
        if not self.gameName:
            self.app.print( 'Error with game dir. No game selected!', True)

    def getPathGame( self):
        self.checkSelectedGame( )
        return self.gamePath
    def getPath( self):
        self.checkSelectedGame()
        return self.path


def main():
    pass

if __name__ == "__main__":
    main()