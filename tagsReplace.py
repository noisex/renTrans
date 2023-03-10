# from settings import settings
import re
import tkinter as tk
import filesClass as files


reZamena = [
    # r'(\[.+?\])',
    # r'(\[[^\s]+?\])',
    r'(\[[\w.!-]+?\])',
    r'(\%\(\w+?\)s)',
]


class TagsClass:
    def __init__(self, game) -> None:
        self.game   = game
        self.app    = game.app
        self.print  = game.print

    def makeList( self, oLine: str):
        for reZam in reZamena:
            oResult = re.findall( reZam, oLine)

            if oResult:
                for value in oResult:
                    if value not in self.game.listTempTags:
                        self.game.listTempTags[value] = {'count': 0, 'item': value}  # выписываем в словарь тэги в квадратных скобках
                    self.game.listTempTags[value]['count'] += 1

    def load( self, fileList):
        self.game.listTempTags = {}
        for fileName in fileList:
            fileData, _error = files.readFileToList( fileName)
            for line in fileData:
                if ( '    #' in line) or ( '    old' in line):
                    self.makeList( line)

        self.app.textTag['state'] = tk.NORMAL
        self.loadToTextBox(self.app.textTag, longStr=True)
        self.app.textTag['state'] = tk.DISABLED

    def replace( self, _event):
        dictTemp    = {}
        textLine01  = self.loadToTextBox(keyList=True)
        texLineEng  = self.app.textEng.get(1.0, tk.END)
        textLine02  = texLineEng.split('\n')

        if len( texLineEng) <= 1:
            self.print( 'Nothing to change, skipped...', True)
            return

        for i, line in enumerate(textLine02):
            if len( line) >= 1:
                try:
                    if line != textLine01[i]:
                        dictTemp[textLine01[i]] = { 'data': line, 'count': 0}
                except RuntimeError as e:
                    self.print( f'-=> Skipped [{line}] -=> [{e}]')
                except IndexError:
                    self.print( f'-=> Skipped [{line}] -=> видимо оно лишнее...')

        fileList = files.getFolderList(files.folderTL, '.rpy', silent=True)
        for fileNameTemp in fileList:
            # ТУТ НЕ НАДО В ЛИСТ!!!
            with open(fileNameTemp, 'r', encoding='utf-8') as file:
                fileData = file.read()

            for tempLine, tempValue in dictTemp.items():
                if tempLine != tempValue['data']:
                    tempValue['count'] += fileData.count( tempLine)
                    fileData = fileData.replace( tempLine, str( tempValue['data']))  # + '[123]')
            # ТУТ ТОЖЕ НЕ НАДО
            with open( fileNameTemp, 'w', encoding='utf-8') as file:
                file.write(fileData)

        if len( dictTemp) >= 1:
            self.print('Change brackets tags in temp files...', True)
            for tempLine, tempValue in dictTemp.items():
                self.print( f'-=> `red`{tempValue["count"]:3}` `bold`{tempLine}` -=> `bold`{tempValue["data"]}`')
        else:
            self.print('No one tag changed, skipped...')

    def copyRight( self, _event):
        self.loadToTextBox(self.app.textEng)
        self.app.tagsCopy()

    def loadToTextBox(self, textBox=None, longStr=None, retList=None, keyList=None):
        returnList = []
        sortedList = {k: self.game.listTempTags[k] for k in sorted( self.game.listTempTags)}

        if textBox:
            textBox.delete( '1.0', tk.END)
            if len( sortedList) >= 1:
                textBox['width'] = min( len( max( sortedList, key=len)) + 10, 70)
            else:
                textBox['width'] = 20

        for strTag in sortedList:
            if retList:
                returnList.append( self.game.listTempTags[strTag]["item"])
            elif keyList:
                returnList.append( strTag)
            else:
                if longStr:
                    textBox.insert(tk.END, f'{ self.game.listTempTags[strTag]["count"]:3}| { self.game.listTempTags[strTag]["item"][:65]}\n')
                else:
                    textBox.insert(tk.END, f'{ self.game.listTempTags[strTag]["item"][:65]}\n')
        return returnList

    def loadFile( self, _event):
        gameTag = files.loadDicFromFile( self.game.gameNameClear)

        if gameTag:
            for ind in gameTag.keys():
                if ( ind in self.game.listTempTags) and ( gameTag[ind] != self.game.listTempTags[ind]['item']):
                    self.game.listTempTags[ind]["item"] = gameTag[ind]

            self.loadToTextBox(self.app.textEng)

    def saveFile( self, _event):
        textLine01  = self.loadToTextBox(keyList=True)
        texLineEng  = self.app.textEng.get(1.0, tk.END)
        textLine02  = texLineEng.split('\n')

        for i, line in enumerate(textLine02):
            if len( line) >= 1:
                try:
                    if line != textLine01[i]:

                        self.game.listTempTags[textLine01[i]]["item"] = line

                        # dictTemp[textLine01[i]] = { 'data': line, 'count': 0}
                except RuntimeError as e:
                    self.print( f'-=> Skipped [{line}] -=> [{e}]')
                except IndexError:
                    self.print( f'-=> Skipped [{line}] -=> видимо оно лишнее...')

        files.writeDicToFile( self.game.listTempTags, self.game.gameNameClear)
