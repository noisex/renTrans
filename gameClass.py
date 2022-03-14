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

    def listGameDClick( self):
        self.gameName       = self.app.listGames.selection_get()
        self.path           = self.gameFolder + self.gameName + '\\'
        self.gamePath       = self.gameFolder + self.gameName + '\\game\\'
        self.pathPython     = None
        pathPython          = self.path       + 'lib\\'

        try:
            # libFolder = list( filter( lambda x: x.startswith( 'windows'), os.listdir( pathPython)))
            libFolder = list( filter( lambda x: 'windows' in x, os.listdir( pathPython)))
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
        sortOrder   = self.app.gameSort.get()
        gameReverse = False
        listGames   = {}
        gameID      = 0
        self.app.gameNameLabelReset()

        with os.scandir( self.gameFolder) as fileList:
            for dirName in fileList:
                gamePath = f'{self.gameFolder}{dirName.name}'
                if dirName.is_dir() and os.path.exists( f'{gamePath}\\game\\') and os.path.exists( f'{gamePath}\\renpy\\'):

                    if sortOrder == 'by date':
                        gameSort    = os.path.getmtime( gamePath)
                        gameReverse = True
                    else:
                        gameSort    = gameID

                    listGames[gameID] = {
                        'dirName': dirName.name,
                        'gameSort': gameSort
                    }
                    gameID += 1

        _listSorted = sorted( listGames.items(), key=lambda x: x[1]['gameSort'], reverse=gameReverse)

        for gameData in _listSorted:
            self.app.listGames.insert( tk.END, gameData[1]['dirName'])

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
