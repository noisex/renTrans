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
    def __init__(self, app) -> None:
        self.app = app
        self.timeSTART      = 0
        self.threadSTOP     = {}

    def progressUpdate( self, tl: int, ts: int, tf: int, cl: int, cs: int, cf: int):
        timeDelta   = datetime.today().timestamp() - self.timeSTART
        timeFinish  = ( tl * timeDelta) / cl
        timeEND     = self.timeSTART + timeFinish
        timeLaps    = timeFinish - timeDelta
        st          = datetime.fromtimestamp( timeEND).strftime( "%H:%M:%S")
        et          = datetime.utcfromtimestamp( timeLaps).strftime("%Mм %Sс")
        self.app.labelsSet( tl, ts, cl, cs, st, et)
        self.app.pbTotal.pbSet(( cl / tl) * 100 , f'{cf}/{tf}')

    def printTransError( self, error, lineSize, lineCount, listName):
        self.app.print( f'-=> ERROR: {error} -=> line: [{lineCount}] ( {lineSize}b) at [{listName}]')
        self.threadSTOP['trans'].do_run = False

    def listTransPrepare(self):
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

    def listTranslate(self, oList: list, listName: str, tl: int, ts: int, tf: int, cl=0, cs=0, cf=0, ) -> tuple:
        tList       = []
        lineCum     = ''
        tLine       = ''
        oListLines  = len(oList)
        testRun     = self.app.testRun.get()

        for ind, oLine in enumerate(oList, 1):
            if not getattr(self.threadSTOP['trans'], "do_run"):
                self.app.print('`red`translate break.`', True)
                return "Error", True
            lineCurSize = len(oLine)
            lineTempSize = len(lineCum)
            cl += 1
            cs += lineCurSize
            # print("dasdsa ", lineTempSize, lineCurSize, settings['TRLEN'], ind, oListLines, oLineTemp, oLine)
            if (lineTempSize + lineCurSize >= settings['TRLEN']) or (ind == oListLines):

                lineNCount = lineCum.count( '\n')

                if testRun:
                    time.sleep(settings['testWait'])
                    tLine = lineCum[0:-1]
                else:
                    tLine = self.lineTransate(lineCum, ind, listName)
                    if tLine is None:
                        tLine = lineCum

                lineONCount = tLine.count('\n') + 1

                if lineNCount > lineONCount:
                    tLine += '\n' * ( lineNCount - lineONCount)

                percent = round((ind / oListLines) * 100, 1)
                self.app.print(f'`rain{ round( percent)}`-=> {percent:5}%` `bold`{cf:2}/{tf}` ({lineTempSize:4}) [{listName:.68}]')
                tList.append( tLine)
                lineCum = ''
                tLine = ''
                self.progressUpdate( tl, ts, tf, cl, cs, cf)
            lineCum += oLine + '\n'
        return tList, False


class RPAClass:
    def __init__(self, app, game) -> None:
        self.app        = app
        self.game       = game
        self.extension  = settings['extension']
        self.extracts   = settings['extracts']

    def rpaExtractFiles(self, fileList: dict, pathGame: str) -> None:
        for fileName in fileList:
            self.app.print(f'Extracting from [`bold`{fileName}`]...', True)
            try:
                UnRPA(fileName, path=pathGame).extract_files('.', fileList[fileName], self.app)
            except BaseException as error:
                self.app.print( f'`red`ERROR.` [`bold`{fileName}`]: {error}')

    def rpaGetListFilesExt(self, fileList: dict) -> dict:
        dicRPA      = {}
        extractes   = self.app.extract.get()

        for fileName in fileList:
            try:
                archNames   = UnRPA(fileName).list_files()
                for fileArchName in archNames:
                    if ( self.app.allExctract.get()) or ( os.path.splitext( fileArchName)[1].lower() in self.extracts[extractes]):
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
                rpyFiles    = 0
                fontsFiles  = 0

                for fileArchName in archNames:
                    extention = os.path.splitext(fileArchName)[1].lower()
                    if extention == '.rpyc':
                        rpycFiles += 1
                    elif extention == '.rpy':
                        rpyFiles += 1
                    elif extention in ('.ttf', '.otf'):
                        fontsFiles += 1

                dicRPA[fileList[fileName]['fileName']] = {
                    'size'      : os.path.getsize(fileName) / (1024 * 1024),
                    'count'     : len(archNames),
                    'rpycFiles' : rpycFiles,
                    'rpyFiles'  : rpyFiles,
                    'fontsFiles': fontsFiles,
                }
            except:
                self.app.print( f'`red`ERROR.` Can`t open file [{fileName}]')

        return dicRPA


def main():
    pass


if __name__ == '__main__':
    main()

