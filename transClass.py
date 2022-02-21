import os
import time
from datetime import datetime
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError
from settings import settings
from unrpa import UnRPA
from renTrans import RenTrans

rent = RenTrans()


class Translator:
    def __init__(self, app, game) -> None:
        self.app = app
        self.game = game

        self.currentSize    = 0
        self.currentLine    = 0
        self.currentFile    = 0
        self.totalFiles     = 0
        self.timeSTART      = 0
        self.threadSTOP     = {}

    def progressUpdate( self):
        timeDelta    = datetime.today().timestamp() - self.timeSTART
        timeFinish   = ( self.game.totalLines * timeDelta) / self.currentLine
        timeEND      = self.timeSTART + timeFinish
        timeLaps     = timeFinish - timeDelta

        self.app.lbStart["text"] = datetime.fromtimestamp( timeEND).strftime( "%H:%M:%S")
        self.app.lbEnd["text"]   = datetime.utcfromtimestamp( timeLaps).strftime("%Mм %Sс")
        self.app.lbLine['text']  = f'{self.currentLine:,} из {self.game.totalLines:,}'
        self.app.lbLines['text'] = f'{self.currentSize:,} из {self.game.totalSizes:,}'
        self.app.pbSet(( self.currentLine / self.game.totalLines) * 100 , f'{self.currentFile}/{self.totalFiles}')

    def printTransError( self, error, lineSize, lineCount, listName):
        self.app.print( f'-=> ERROR: {error} -=> line: [{lineCount}] ( {lineSize}b) at [{listName}]')
        self.threadSTOP['trans'].do_run = False

    def listTransPrepare(self, lenFileList):
        self.currentSize   = 0
        self.currentLine   = 0
        self.currentFile   = 0
        self.totalFiles    = lenFileList
        self.timeSTART     = datetime.today().timestamp()

    def lineTransate( self, oLine, lineCount=0, listName='noListName'):
        try:
            tLine = GoogleTranslator( source=self.app.optLang.get(), target=self.app.optTrans.get()).translate( oLine)  #+ '\n'

        except RequestError as error:
            self.printTransError( error, len( oLine), lineCount, listName)
            tLine = oLine

        except Exception as error:
            self.printTransError( error, len( oLine), lineCount, listName)
            tLine = oLine

        return tLine

    def listTranslate(self, oList: list, listName: str) -> tuple:
        tList       = []
        oLineTemp   = ''
        oListLines  = len(oList)
        testRun     = self.app.testRun.get()

        for ind, oLine in enumerate(oList, 1):
            if not getattr(self.threadSTOP['trans'], "do_run"):
                self.app.print('`red`translate break.`', True)
                return "Error", True
            lineCurSize = len(oLine)
            lineTempSize = len(oLineTemp)
            self.currentLine += 1
            self.currentSize += lineCurSize
            # print("dasdsa ", lineTempSize, lineCurSize, settings['TRLEN'], ind, oListLines, oLineTemp, oLine)
            if (lineTempSize + lineCurSize >= settings['TRLEN']) or (ind == oListLines):
                if testRun:
                    time.sleep(settings['testWait'])
                else:
                    oLineTemp = self.lineTransate(oLineTemp, ind, listName)

                percent = round((ind / oListLines) * 100, 1)
                self.app.print(f'`rain{ round( percent)}`-=> {percent:5}%` `bold`{self.currentFile:2}/{self.totalFiles}` ({lineTempSize:4}) [{listName:.48}]')
                tList.append(oLineTemp)
                oLineTemp = ""
                self.progressUpdate()
            oLineTemp += oLine + '\n'
        return tList, False


class RPAClass:
    def __init__(self, app, game) -> None:
        self.app        = app
        self.game       = game
        self.extension  = settings['extension']

    def rpaExtractFiles(self, fileList: dict, pathGame: str) -> None:
        for fileName in fileList:
            self.app.print(f'Extracting from [`bold`{fileName}`]...', True)
            try:
                UnRPA(fileName, path=pathGame).extract_files('.', fileList[fileName], self.app)
            except:
                self.app.print( f'`red`ERROR.` Can`t open file [`bold`{fileName}`]')

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
            except:
                self.app.print( f'`red`ERROR.` Can`t open file [`bold`{fileName}`]')

        return dicRPA

    def rpaGetFilesStats(self, fileList: dict) -> dict:
        dicRPA = {}
        for fileName in fileList:
            try:
                archNames   = UnRPA(fileName).list_files()
                rpycFiles   = 0
                fontsFiles  = 0

                for fileArchName in archNames:
                    extention = os.path.splitext(fileArchName)[1].lower()
                    if extention == '.rpyc':
                        rpycFiles += 1
                    elif extention in ('.ttf', '.otf'):
                        fontsFiles += 1

                dicRPA[fileList[fileName]['fileName']] = {
                    'size'      : os.path.getsize(fileName) / (1024 * 1024),
                    'count'     : len(archNames),
                    'rpycFiles' : rpycFiles,
                    'fontsFiles': fontsFiles,
                }
            except:
                self.app.print( f'`red`ERROR.` Can`t open file [{fileName}]')

        return dicRPA


def main():
    pass


if __name__ == '__main__':
    main()

    #
    # def listTranslate( self, oList: list, listName: str) -> tuple:
    #     tList       = []
    #     indList     = []
    #     oLineTemp   = ''
    #     oListLines  = len( oList)
    #
    #     for ind, sepLine in enumerate( oList, 1):
    #
    #         if not getattr( self.threadSTOP['trans'], "do_run"):
    #             self.app.print( '`red`Translate break. :(`', True)
    #             return "Error", True
    #
    #         # lineCurSize      = len( sepLine.encode("utf-8"))
    #         # lineTempSize     = len( oLineTemp.encode("utf-8"))
    #         lineCurSize      = len( sepLine)
    #         lineTempSize     = len( oLineTemp)
    #         self.currentLine += 1
    #         self.currentSize += lineCurSize
    #
    #         if ( lineTempSize + lineCurSize >= settings['TRLEN']) or ( ind == oListLines):
    #             if self.app.testRun.get():
    #                 time.sleep( settings['testWait'])
    #             else:
    #                 oLineTemp = self.lineTransate( oLineTemp, ind, listName)
    #
    #             percent = ( ind / oListLines) * 100
    #             rent.print( f'-=> `rain{ round(percent)}`{ round(percent, 1):5}%` `bold`{self.currentFile:2}/{self.totalFiles}` ({lineTempSize:4}) [{listName:.60}]')
    #
    #             olList = oLineTemp.split( '\n')
    #
    #             for i, iid in enumerate( indList):
    #                 tList.append( f'{iid}#{olList[i]}')
    #             oLineTemp = ""
    #             indList = []
    #             self.progressUpdate()
    #
    #         sepLine = sepLine.split('#', 1)
    #         if len( sepLine) == 2:
    #             indList.append(int(sepLine[0]))
    #             oLine = sepLine[1]
    #
    #             oLineTemp += oLine + '\n'
    #     return tList, False
