import os
import  re
import tkinter as tk
from settings import settings
# from renTrans import RenTrans

# reMenu      = 'menu:'
# reSpace     = r'\s{4}'
reNonSpace  = r'\S+'
reFix       = re.compile(r'\b\w{3,14}\b')  # ищем слова 4+ для замены по словарю
reg         = re.compile(r'^([\w\s]+)-.*')

reBrackets  = [
    '(\\[.+?\\])',          # квадратные скобки  - []
    '({.+?})',              # фигурные скобки    - {}
    '(\\%\\(.+?\\))'        # процент со скобкой - %()
]


class GameRenpy:
    def __init__(self, app):
        # tk.Tk.__init__(self, *args, **kwargs)
        self.app        = app
        self.print      = app.print
        self.gameName   = None
        self.gameNameClear = None
        self.path       = None
        self.gamePath   = None
        self.shortPath  = None
        self.gameTLRUS  = None
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

        self.inFolderRPY = 0
        self.inFolderRPC = 0
        self.inFolderRPA = 0

        self.inArchiveRPC = 0
        self.inArchiveRPY = 0
        self.inArchiveTTF = 0

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

        ret = reg.search(self.gameName)
        if ret is not None:
            self.gameNameClear = ret.group(1)
        else:
            self.gameNameClear = self.gameName

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
                self.print( f'`navy`Warning:` not found python for Windows in folder [`bold`{pathPython}`]')

        except BaseException as e:
            self.print( f'`red`ERROR:` cant found python libs in game folder: [`bold`{pathPython}`]')
            self.print( f'{e}')

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
            self.print( '`red`Error` with game folder. `navy`No game selected!`', True)

    def getPathGame( self):
        self.checkSelectedGame( )
        return self.gamePath

    def getPath( self):
        self.checkSelectedGame()
        return self.path

    def setGameNameBlock(self):
        self.app.gameNameBlock['text'] = self.gameName

        self.app.gmb11['text'] = self.inFolderRPY
        self.app.gmb12['text'] = self.inFolderRPC
        self.app.gmb13['text'] = self.inFolderRPA

        self.app.gmb21['text'] = self.inArchiveRPY
        self.app.gmb22['text'] = self.inArchiveRPC
        self.app.gmb23['text'] = self.inArchiveTTF

    def stringLevel( self, oLine: str):
        """back indent level of current line in spaces/4"""
        return int( re.search( reNonSpace, oLine).start()) / 4
        # return len( re.findall( reSpace, oLine))

    def stringLevel4( self, oLine: str) -> int:
        """back indent level of current line in spaces"""
        return re.search(reNonSpace, oLine).start()

    def correctWordDic( self,fix: str) -> str:
        fixRE   = re.findall( reFix, fix)
        wordDic = settings['wordDic']

        for item in fixRE:
            itemLow = item.lower()

            if itemLow in wordDic:
                self.wordDicCount += 1

                if item.islower():
                    itemRET = wordDic[itemLow]
                elif item.isupper():
                    itemRET = wordDic[itemLow].upper()
                elif item.istitle():
                    itemRET = wordDic[itemLow].capitalize()
                else:
                    itemRET = wordDic[itemLow]

                fix = re.sub( fr'\b{item}\b', itemRET, fix)
                # app.log.error(f' wordDic: [{fileName}] = [{ fix.strip()}]')
        return fix

    def correctOpenBrackets( self, tLine: str, oLine: str) -> str:
        """
        поиск и замена нечетных квадратных скобок
        """
        ref = re.findall( r'[\[\]]', tLine)
        if len( ref) % 2 != 0:
            self.print( '`red`WARNING`:')
            self.print( f'`bold`Open brackets` in (`bold`{tLine}`).')
            self.print( f'Original string: (`bold`{oLine}`)')

            ref = re.findall( r'\S*', tLine)
            for rel in ref:
                if '[' in rel and ']' not in rel:
                    tLine = tLine.replace( rel, rel + ']')
                elif ']' in rel and '[' not in rel:
                    tLine = tLine.replace(rel, '[' + rel)

            self.print( f'I try to fix it: (`bold`{tLine}`)')
        return tLine

    def correctTranslate( self, fix):                                           # корректировка всяких косяков первода, надо перписать...
        """
        корректировка всяких косяков перевода, надо переписать...
        """
        # %(РС - %(p_name)s
        fix = re.sub( r'([-~])$', r'.', fix)                                    # -" => ."
        fix = re.sub( '^да', 'Да', fix)
        fix = re.sub( r'(\s+)([.!?,])', r'\2', fix)                             # убираем парные+ пробелы и пробелы перед знаком препинания

        fix = re.sub( r'К[аА][кК][иИоОаА].+([-.!?])', r'Что\1', fix)            # Какие -> Что
        fix = re.sub( r'Большой([.!?])', r'Отлично\1', fix)
        fix = re.sub( r'Прохладный([.!?])', r'Здорово\1', fix)

        fix = re.sub( r'([A-ZА-Я])-([а-яА-Я])(\w+)', r'\2-\2\3', fix)           # T-Спасибо -=> С-Спасибо
        fix = re.sub( r'(\d+)\W*%', r'\1\%', fix)                               # 123% => 123\%

        fix = fix.replace( r'\"', r"'")
        fix = fix.replace( r'"', r"'")

        fix = fix.replace( '% (', ' %(')
        # fix = fix.replace( '} ', '}')
        # fix = fix.replace( ' {/', '{/')
        fix = re.sub( r'\\$', '', fix)

        fix = re.sub( r'\)\s*[ысs]', r'\)s', fix, flags=re.I)
        fix = re.sub( r'\\ n', r'\\n', fix, flags=re.I)
        fix = re.sub( '{я[ }]', '{i} ', fix, flags=re.I)
        # if fix.find( 'Какие') >= 0:
        #     app.print( str( fix))
        return fix

    def correctTagsBrackets( self, tLine: str, oLine: str):
        """
        замена кривых, т.е. всех, переведенных тегов на оригинальные
        """
        for re_find in reBrackets:
            tResultSC = re.findall(re_find, tLine)                              # ищем теги в скобках в оригинальной строке

            if tResultSC:
                oResultSC = re.findall(re_find, oLine)                          # ищем теги в скобках в переведенной строке
                for i, value in enumerate( oResultSC):

                    try:
                        # if tResultSC[i] != '[123]':
                        tLine = tLine.replace( tResultSC[i], value)              # заменяем переведенные кривые теги оригинальными по порядку
                    except IndexError:
                        self.print( f'`red`IndexError` with tag replace [{tResultSC}] in line [{tLine}]')

        return tLine   #.replace( '[123]', '')


def main():
    pass


if __name__ == "__main__":
    main()
