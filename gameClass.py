import os
import tkinter as tk
from settings import settings
# from renTrans import RenTrans


class GameRenpy():
    def __init__(self, app):
        # tk.Tk.__init__(self, *args, **kwargs)
        self.app = app
        self.gameName = None
        self.path = None
        self.gamePath = None
        self.shortPath = None
        self.gameTLRUS = None
        self.pathPython = None
        self.totalLines = 0
        self.totalSizes = 0
        self.totalFiles = 0
        self.wordDicCount = 0
        self.listTempTags = {}
        self.itemDict = {}
        self.threadSTOP = {}

        self.backupFolderTemplate = 'Backup'
        self.gameFolder     = self.app.gameFolder.get()  #settings['gameFolder']  #'D:\\AdGames\\'
        self.backupFolder   = settings['backupFolder']  #Backup'

    def makeNewBackupFolder( self):
        self.backupFolder = self.backupFolderTemplate
        i = 0
        while os.path.exists( self.getPath() + self.backupFolder):                  # приписывает число к имени, если есть такой файл
            i += 1
            self.backupFolder = f'{self.backupFolderTemplate} ({i:02})'
        # self.app.print( f'backup folder = {self.backupFolder}')

    def getBackupFolder( self):
        return self.backupFolder

    # def rawincount(self, filename):
    #     f = open(filename, 'rb')
    #     bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    #     return sum( buf.count(b'\n') for buf in bufgen )

    @staticmethod
    def getFileSize( fileName: str) -> tuple:
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
        return fileSize, fileLine

    def getListFilesByExt( self, ext='.rpy', gamePath=None, withTL=True, withStat=False, onlyRoot=None, silent=False, lastScan=None) -> dict:
        if not gamePath:
            gamePath = self.getPathGame()
        gamePathTemp = 'TestDirs' + 'game\\tl' if withTL else 'game\\tl'

        if isinstance( ext, str):
            ext = ext.split( ', ')
        if withStat:
            self.totalLines = 0
            self.totalSizes  = 0
            self.totalFiles = 0

        filesAll = {}
        for top, _, files in os.walk( gamePath):                           # Находим файлы для перевода в дирректории
            for fileName in files:
                if gamePathTemp not in top \
                    and ( os.path.splitext( fileName)[1] in ext or '*' in ext) \
                        and fileName not in settings['fileSkip']:

                    if onlyRoot and top != gamePath:
                        break
                    # filePath = os.path.normpath( os.path.join( top, fileName))
                    filePath = os.path.join( top, fileName)
                    # fileTime = os.path.getmtime(filePath)
                    filesAll[filePath] = {
                        'fileShort': filePath.replace( gamePath, ''),
                        'fileName' : os.path.basename( filePath)
                    }
                    if withStat:
                        # print( fileName, fileTime, lastScan)
                        size, lines     = self.getFileSize( filePath)  #os.path.getsize(  filePath)
                        self.totalLines += lines
                        self.totalSizes += size
                        self.totalFiles += 1
                        filesAll[filePath]['lines'] = lines
                        filesAll[filePath]['size']  = size
        if not silent:
            self.app.print( f'[`bold`{len( filesAll)}`] {ext} files in [`bold`{gamePath}`]')
        return dict( sorted( filesAll.items()))

    def listGameDClick( self):
        self.gameName       = self.app.listGames.selection_get()
        self.path           = self.gameFolder + self.gameName + '\\'
        self.gamePath       = self.gameFolder + self.gameName + '\\game\\'
        self.pathPython     = None
        pathPython          = self.path       + 'lib\\'

        try:
            libFolder = list( filter( lambda x: x.startswith( 'windows'), os.listdir( pathPython)))
            for folder in libFolder:
                tryName = pathPython + folder + '\\python.exe'
                if os.path.exists( tryName):
                    self.pathPython = tryName

            if not self.pathPython:
                self.app.print( f'`navy`Warning:` not found python for Windows in folder [`bold`{pathPython}`]')

        except BaseException as e:
            self.app.print( f'`red`ERROR:` cant found python libs in game folder: [`bold`{pathPython}`]')
            self.app.print( f'{e}')

        tempLine = ''
        self.shortPath      = self.gameName + '\\'
        self.gameTLRUS      = self.gamePath + 'tl\\rus\\'

        if os.path.exists( self.gameTLRUS):
            tempLine += '[`green`RUS`] '
        if os.path.exists( self.gamePath + 'tl\\russian\\'):
            tempLine += '[`red`RUSSIAN`] '
        if os.path.exists( self.gamePath + 'tl\\en\\'):
            tempLine += '[`red`EN`] '
        if os.path.exists( self.gamePath + 'tl\\english\\'):
            tempLine += '[`red`ENGLISH`] '
        self.app.print(f'`big`{self.gameName}` {tempLine}', True)  # , tag='bold')

    # todo new game init
    def gameListScan( self, _event):
        self.gameFolder = self.app.gameFolder.get()
        self.app.gameNameLabelReset()

        with os.scandir( self.gameFolder) as fileList:
            for dirName in fileList:
                if dirName.is_dir() and os.path.exists( f'{self.gameFolder}{dirName.name}\\game\\') and os.path.exists( f'{self.gameFolder}{dirName.name}\\renpy\\'):
                    self.app.listGames.insert( tk.END, dirName.name)

    def checkSelectedGame( self):
        if not self.gameName:
            self.app.print( '`red`Error` with game folder. `navy`No game selected!`', True)

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
