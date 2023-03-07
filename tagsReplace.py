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


def tagListMake( game, oLine: str):
    for reZam in reZamena:
        oResult = re.findall( reZam, oLine)

        if oResult:
            for value in oResult:
                if value not in game.listTempTags:
                    game.listTempTags[value] = {'count': 0, 'item': value}  # выписываем в словарь тэги в квадратных скобках
                game.listTempTags[value]['count'] += 1


def tagsInTLFolder( app, game, fileList):
    game.listTempTags = {}
    for fileName in fileList:
        fileData, _error = files.readFileToList( fileName)
        for line in fileData:
            if ( '    #' in line) or ( '    old' in line):
                tagListMake( game, line)

    app.textTag['state'] = tk.NORMAL
    tagListInsertRead( game, app.textTag, longStr=True)
    app.textTag['state'] = tk.DISABLED


def tagsChange( app, game):
    dictTemp    = {}
    textLine01  = tagListInsertRead( game, keyList=True)
    texLineEng  = app.textEng.get(1.0, tk.END)
    textLine02  = texLineEng.split('\n')

    if len( texLineEng) <= 1:
        app.print( 'Nothing to change, skipped...', True)
        return

    for i, line in enumerate(textLine02):
        if len( line) >= 1:
            try:
                if line != textLine01[i]:
                    dictTemp[textLine01[i]] = { 'data': line, 'count': 0}
            except RuntimeError as e:
                app.print( f'-=> Skipped [{line}] -=> [{e}]')
            except IndexError:
                app.print( f'-=> Skipped [{line}] -=> видимо оно лишнее...')

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
        app.print('Change brackets tags in temp files...', True)
        for tempLine, tempValue in dictTemp.items():
            app.print( f'-=> `red`{tempValue["count"]:3}` `bold`{tempLine}` -=> `bold`{tempValue["data"]}`')
    else:
        app.print('No one tag changed, skipped...')


def tagsCopy( app, game):
    tagListInsertRead( game, app.textEng)
    app.tagsCopy()


def tagListInsertRead( game, textBox=None, longStr=None, retList=None, keyList=None):
    returnList = []
    sortedList = {k: game.listTempTags[k] for k in sorted(game.listTempTags)}

    if textBox:
        textBox.delete( '1.0', tk.END)
        if len( sortedList) >= 1:
            textBox['width'] = min( len( max( sortedList, key=len)) + 10, 70)
        else:
            textBox['width'] = 20

    for strTag in sortedList:
        if retList:
            returnList.append(game.listTempTags[strTag]["item"])
        elif keyList:
            returnList.append( strTag)
        else:
            if longStr:
                textBox.insert(tk.END, f'{game.listTempTags[strTag]["count"]:3}| {game.listTempTags[strTag]["item"][:65]}\n')
            else:
                textBox.insert(tk.END, f'{game.listTempTags[strTag]["item"][:65]}\n')
    return returnList


def tagsLoad( app, game):
    gameTag = files.loadDicFromFile( game.gameNameClear)

    if gameTag:
        for ind in gameTag.keys():
            if ( ind in game.listTempTags) and ( gameTag[ind] != game.listTempTags[ind]['item']):
                game.listTempTags[ind]["item"] = gameTag[ind]

        tagListInsertRead( game, app.textEng)


def tagsSave( app, game):
    textLine01  = tagListInsertRead( game, keyList=True)
    texLineEng  = app.textEng.get(1.0, tk.END)
    textLine02  = texLineEng.split('\n')

    for i, line in enumerate(textLine02):
        if len( line) >= 1:
            try:
                if line != textLine01[i]:

                    game.listTempTags[textLine01[i]]["item"] = line

                    # dictTemp[textLine01[i]] = { 'data': line, 'count': 0}
            except RuntimeError as e:
                app.print( f'-=> Skipped [{line}] -=> [{e}]')
            except IndexError:
                app.print( f'-=> Skipped [{line}] -=> видимо оно лишнее...')

    files.writeDicToFile( game.listTempTags, game.gameNameClear)


    def main():
        pass

    if __name__ == '__main__':
        main()

