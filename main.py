# "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$",
# https://www.sublimetext.com/docs/build_systems.html#exec_options
import os
import re
import threading
import shutil
import pickle
from datetime import datetime

import subprocess
import tkinter as tk
from shutil import ignore_patterns  # copytree, rmtree
from fontTools.ttLib import TTFont

from gameClass import GameRenpy
from guiClass import YoFrame
from renTrans import RenTrans
from settings import settings
from transClass import Translator, RPAClass
import filesClass as files
########################################################################################################################

rent    = RenTrans()
app     = YoFrame()
game    = GameRenpy( app)
rpaArch = RPAClass(  app, game)
trans   = Translator(app)

rent.print = app.print

reZamena = [
    '(\\[\\w+?\\])',
    '(\\%\\(\\w+?\\)s)',
]
reBrackets  = [
    '(\\[.+?\\])',          # квадратные скобки  - []
    '({.+?})',              # фигурные скобки    - {}
    '(\\%\\(.+?\\))'        # процент со скобкой - %()
]
reFix       = re.compile(r'\b\w{3,14}\b')  # ищем слова 4+ для замены по словарю

# reTrans     = re.compile(r'(["])')
# reTrans     = re.compile(r'"(.*[a-zA-Z].*")(?:( \(.*\))?)')
# reTrans     = re.compile(r'"(.*[\w].*?)"')
# reTrans     = re.compile( r'"(.*?[A-Za-z].*?)"')
reTrans     = re.compile( r'"(.+?)"')

reMenu      = '\\s{4,}menu:'
reSpace     = '\\s{4}'
########################################################################################################################


def stringLevel( oLine: str) -> int:
    """back indent level of current line"""
    return len( re.findall( reSpace, oLine))


def clearItem( line: str) -> str:
    line = line.replace( '$', '')
    line = line.replace( '"', '')

    tComm = line.find( '#')
    if tComm > 1:
        line = line[0:tComm]

    line = line.strip()
    line = line[0: 30]
    return line


def clearMenuList( menuList: dict, level: int) -> dict:
    retList = {}
    # обновляем менюлист пуктами, которые еще не закрыты
    for menuLevel in menuList:
        if menuLevel < level:
            retList[menuLevel] = menuList[menuLevel]
    return retList


# todo где-то тут надо влепить ПОП вместо пересборки списка менюшек
def checkMenuList( level: int, lines: int, line: str, menuList: dict, menuDict: dict):
    menuList = clearMenuList( menuList, level)

    for menuLevel, menuValue in menuList.items():
        menuID = menuValue
        filePath = menuDict[menuID]['filePath']
        # ближе чем меню - закрываем меню
        # if level <= menu:
        #     menuDict[menuID]['end'] = lines

        # следующий уровень - пишем пункт меню
        if level == menuLevel + 1 and '  "' in line:
            # menuDict[menuID]['items'].append( line)
            menuDict[menuID]['itemsID'].append( lines)

        # текст тела меню - ищем переменные и пишем
        if ( level == menuLevel + 2) and ( '  $' in line) and ( '=' in line) and ( 'renpy' not in line):
            line = clearItem( line)
            itemsStrID = menuDict[menuID]['itemsID'][-1]

            # если нет еще итемов на данный пункт - создать пустой
            if itemsStrID not in game.itemDict[filePath]:
                game.itemDict[filePath][itemsStrID] = settings['itemSize']

            game.itemDict[filePath][itemsStrID] += f' ({line})'
            # menuDict[menuID]['vars'].append( line)
            # menuDict[menuID]['items'][-1] = tList.replace( '\":', f' [{line}]\":')
            # itemsID = list( game.itemDict.keys())[-1]
            # game.itemDict[itemsStrID] = menuDict[menuID]['items'][-1]
            # print( f'{spacePrint(level)}{line} {tList} {menuID} {itemsID}')


def menuFileRead( filePath: str, fileText: list):
    menuDict = {}
    menuList = {}
    menuID = 0

    for lineID, line in enumerate( fileText, 1):
        oResultSC = re.findall( reMenu, line)
        spaceLevel = stringLevel( line)

        if oResultSC:
            menuID += 1
            menuList[spaceLevel] = menuID
            menuDict[menuID] = { 'id': menuID, 'itemsID': [], 'filePath': filePath}  # , 'level': spaceLevel, 'start': lineID, 'items': [], 'vars': []}

        # если еще есть незакрытые менюхи и есть данные - анализ этой строки
        elif len( menuList) > 0 and len( line) > 0:
            checkMenuList( spaceLevel, lineID, line, menuList, menuDict)


# Партишн строки на 3 части # x = txt.partition("eat")
# If the specified value is not found, the rpartition() method returns a tuple containing: 1 - an empty string, 2 - an empty string, 3 - the whole string:
# не катит, так как я не знаю конец добавленной строки, только если регуляркой вырезаьть
def itemClearFromOld( line: str, strReplace: str) -> str:
    """очищаем строку от добавленных ранее подсказок"""
    itemStart = line.find( settings['itemSize'])
    if itemStart > 0:
        itemEnd = line.find( strReplace)
        strFull = line[0:itemStart] + line[itemEnd:]
    else:
        strFull = line
    return strFull


def menuFileWrite(fileName: str, fileText: list, fileShort: str) -> None:
    lenItemsList = len( game.itemDict[fileName])
    if lenItemsList < 1:
        return

    app.print( f'-=> [`red`{lenItemsList:3}`] in [{fileShort}]')
    copyMenuToBackUp( fileName)

    for lineID, lineValue in game.itemDict[fileName].items():
        oLine = fileText[lineID - 1]
        if '":' in oLine:   # если вконце меню есть ИФ или еще что-то
            strReplace = '":'
        else:
            strReplace = '" '

        lineValue = re.sub( r'[\[\]]', '.', lineValue)
        oLine     = itemClearFromOld( oLine, strReplace)
        oLine     = oLine.replace( strReplace, lineValue[0:100] + strReplace)
        app.log.error( f'[{lineID}] = [{oLine.strip()}]')
        fileText[lineID - 1] = oLine

    files.writeListToFile( fileName, fileText)


# reTest = re.compile( r'\s{4}"(.+?)".*:\s*$')

#  todo check items before wtite and print result
def btnMenuFindVars(_event):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    fileList = files.getFolderList(pathGame, '.rpy', withTL=False, silent=True)
    game.makeNewBackupFolder()
    app.print( f'Find menu with variables ( backUp in [`bold`{game.backupFolder}`])...', True)
    for fileName, fileValue in fileList.items():
        fileText, error = files.readFileToList( fileName)

        if not error:
            game.itemDict[fileName] = {}
            menuFileRead( fileName, fileText)

            # for ind, testLine in enumerate( fileText):
            #     reFind = re.search( reTest, testLine)
            #     if reFind:
            #         oLine = reFind.group(1)
            #         print( ind, testLine, oLine)
            # for reT in reFind:
            #     print( reT)
            menuFileWrite( fileName, fileText, fileValue['fileShort'])
        else:
            return
########################################################################################################################


def copyMenuToBackUp(filePath, fileBackPath=None):
    fileNewName = filePath.replace( f'{game.getPathGame()}', '')

    if fileBackPath is None:
        fileBackPath = f'{game.getPath()}\\{game.getBackupFolder()}\\game\\{os.path.dirname( fileNewName)}\\'
    else:
        fileBackPath = f'{game.getPath()}\\{fileBackPath}\\{os.path.dirname( fileNewName)}\\'

    fileBackFile = fileBackPath + os.path.basename( filePath)
    os.makedirs( fileBackPath, exist_ok=True)
    shutil.copy2( filePath, fileBackFile)  # complete target filename given


def copyTLStuff( event, old=None, new=None, updateList=True):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    if not old:
        old = f'{pathGame}tl\\rus\\'
    if not new:
        new = files.folderTL

    if os.path.exists( old) and os.path.exists( new):
        files.clearFolder( new, '*')
        shutil.copytree( old, new, dirs_exist_ok=True, ignore=ignore_patterns('*.rpyc', 'xxx_*', 'common.rpy', 'options.rpy', 'screens.rpy'))
        app.print( f'From [`bold`{old}`] copied to [`bold`{new}`].')
        if updateList:
            listFileStats( event)
    else:
        app.print( f'`red`ERROR:` folder [`bold`{old}`] not found. {os.path.exists( new)}')


def btnCopyFontsStuff(_event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    char = 1060
    # app.print( 'Start search non-rus fonts and replace them...', True)
    try:
        shutil.copytree( settings['folderGAME'], pathGame, dirs_exist_ok=True)
        app.print(f'Your game stuff from [`bold`{settings["folderGAME"]}`] copied.', True)
    except FileNotFoundError:
        app.print( f'`red`Error.` Folder [`bold`{settings["folderGAME"]}`] not found.', True)

    fileList = files.getFolderList(pathGame, '.ttf, .otf')

    for fileName, fileValue in fileList.items():
        font = TTFont( fileName)
        for cmap in font['cmap'].tables:
            if cmap.isUnicode():
                if char in cmap.cmap:
                    app.print( f"`green`Good RUS` font: [`bold`{fileValue['fileShort']}`]")
                else:
                    app.print( f"`navy`Badz ENG` font: [`bold`{fileValue['fileShort']}`]")
                    try:
                        copyMenuToBackUp( fileName, 'backupFonts')
                        shutil.copy2( pathGame + 'webfont.ttf', fileName)  # complete target filename given
                    except FileNotFoundError as error:
                        app.print( f'`red`Error.` `bold`{error}`')
                break


def getListFilesRPA():
    filesRPY    = 0
    filesRPYC   = 0
    filesFonts  = 0
    pathGame    = game.getPathGame()

    if pathGame:
        fileList = files.getFolderList(pathGame, '.rpa', onlyRoot=True, silent=True)
        archFileList = rpaArch.rpaGetFilesStats( fileList)

        for archFile, archValues in archFileList.items():
            app.print( f'-=> [`bold`{archValues["size"]:7,.1f}` mb] [`bold`{archValues["count"]:6,}` files] in [`bold`{archFile}`]')
            filesRPY   += archValues["rpyFiles"]
            filesRPYC  += archValues["rpycFiles"]
            filesFonts += archValues["fontsFiles"]

        if filesRPY >= 1:
            app.print( f'[`red`{filesRPY}`] `navy`RPY` files in achieves.')
        if filesRPYC >= 1:
            app.print( f'[`red`{filesRPYC}`] `navy`RPYC` files in achieves.')
        if filesFonts >= 1:
            app.print( f'[`red`{filesFonts}`] `bold`Fonts` files in archives.')


def findTagsInTLFolder( fileList):
    game.listTempTags = {}
    for fileName in fileList:
        fileData, _error = files.readFileToList( fileName)
        for line in fileData:
            if ( '    #' in line) or ( '    old' in line):
                makeTempTagList( line)

    app.textTag['state'] = tk.NORMAL
    tagListInsertRead( app.textTag, longStr=True)
    app.textTag['state'] = tk.DISABLED


def listFileStats( _event, path=False, withTL=True, withStat=False, ext='.rpy'):
    if not path:
        path = files.folderTL
    fileList = files.getFolderList(path, ext=ext, withTL=withTL, withStat=withStat)
    app.listFileUpdate( fileList)
    if path == files.folderTL:
        findTagsInTLFolder( fileList)


def correctWordDic(fix: str) -> str:
    fixRE   = re.findall( reFix, fix)
    wordDic = settings['wordDic']

    for item in fixRE:
        itemLow = item.lower()

        if itemLow in wordDic:
            game.wordDicCount += 1

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


def correctOpenBrackets( tLine: str, oLine: str) -> str:
    ref = re.findall( r'[\[\]]', tLine)
    if len( ref) % 2 != 0:
        app.print( '`red`WARNING`:')
        app.print( f'`bold`Open brackets` in (`bold`{tLine}`).')
        app.print( f'Original string: (`bold`{oLine}`)')

        ref = re.findall( r'\S*', tLine)
        for rel in ref:
            if '[' in rel and ']' not in rel:
                tLine = tLine.replace( rel, rel + ']')
            elif ']' in rel and '[' not in rel:
                tLine = tLine.replace(rel, '[' + rel)

        app.print( f'I try to fix it: (`bold`{tLine}`)')
    return tLine


def correctTranslate(fix):                                                 # корректировка всяких косяков первода, надо перписать...
    # %(РС - %(p_name)s
    fix = re.sub( r'([-~])$', r'.', fix)                                           # -" => ."
    fix = re.sub( '^да', 'Да', fix)
    fix = re.sub( r'(\s+)([.!?,])', r'\2', fix)                               # убираем парные+ пробелы и пробелы перед знаком препинания

    fix = re.sub( r'К[аА][кК][иИоО]\w([-.!?])', r'Что\1', fix)         # Какие -> Что
    fix = re.sub( r'Большой([.!?])', r'Отлично\1', fix)
    fix = re.sub( r'Прохладный([.!?])', r'Здорово\1', fix)

    fix = re.sub( r'([A-ZА-Я])-([а-яА-Я])(\w+)', r'\2-\2\3', fix)                     # T-Спасибо -=> С-Спасибо
    fix = re.sub( r'(\d+)\W*%', r'\1\%', fix)                                   # 123% => 123\%

    fix = fix.replace( r'\"', r"'")
    fix = fix.replace( r'"', r"'")

    fix = fix.replace( '% (', ' %(')
    fix = fix.replace( '} ', '}')
    # fix = fix.replace( ' {/', '{/')
    fix = re.sub( r'\\$', '', fix)

    fix = re.sub( r'\)\s*[ысs]', r'\)s', fix, flags=re.I)
    fix = re.sub( r'\\ n', r'\\n', fix, flags=re.I)
    fix = re.sub( '{я[ }]', '{i}', fix, flags=re.I)
    # if fix.find( 'Какие') >= 0:
    #     app.print( str( fix))
    return fix


def correctTagsBrackets(tLine: str, oLine: str):                                      # замена кривых, т.е. всех, переведенных тегов на оригинальные
    for re_find in reBrackets:
        tResultSC = re.findall(re_find, tLine)                              # ищем теги в скобках в оригинальной строке

        if tResultSC:
            oResultSC = re.findall(re_find, oLine)                          # ищем теги в скобках в переведенной строке
            for i, value in enumerate( oResultSC):

                try:
                    # if tResultSC[i] != '[123]':
                    tLine = tLine.replace( tResultSC[i], value)              # заменяем переведенные кривые теги оригинальными по порядку
                except IndexError:
                    app.print( f'`red`Error` with tag replace [{tResultSC}] in line [{tLine}]')
                    pass

    return tLine   #.replace( '[123]', '')


def tagListInsertRead(textBox=None, longStr=None, retList=None):
    returnList = []
    sortedList = {k: game.listTempTags[k] for k in sorted(game.listTempTags)}

    if textBox:
        textBox.delete( '1.0', tk.END)
        if len( sortedList) >= 1:
            textBox['width'] = max( len( max( sortedList, key=len)) + 5, 15)
        else:
            textBox['width'] = 15

    for strTag in sortedList:
        if retList:
            returnList.append(game.listTempTags[strTag]["item"])
        else:
            if longStr:
                textBox.insert(tk.END, f'{game.listTempTags[strTag]["count"]:3}| {game.listTempTags[strTag]["item"]}\n')
            else:
                textBox.insert(tk.END, f'{game.listTempTags[strTag]["item"]}\n')
    return returnList


def btnTagsChange(_event):
    dictTemp    = {}
    textLine01  = tagListInsertRead(retList=True)
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


def makeTempTagList(oLine: str):
    for reZam in reZamena:
        oResult = re.findall( reZam, oLine)

        if oResult:
            for value in oResult:
                if value not in game.listTempTags:
                    game.listTempTags[value] = {'count': 0, 'item': value}  # выписываем в словарь тэги в квадратных скобках
                game.listTempTags[value]['count'] += 1


def btnMakeTempFiles(event):
    files.clearFolder( files.folderTEMP, '*')
    files.clearFolder( files.folderIND, '*')
    fileList = files.getFolderList(files.folderTL, '.rpy')

    for fileName in fileList:
        fileText, _error = files.readFileToList( fileName)
        tempFileName    = files.folderTEMP + fileList[fileName]['fileShort']
        indFileName     = files.folderIND + fileList[fileName]['fileShort']

        oList = []
        iList = []
        skipLLines = 0
        for ind, line in enumerate( fileText):
            if ( skipLLines <= 0) and ( r' "' in line):
                line = line.replace( r'\"', r"'")
                skipLLines = 3
                result = reTrans.search( line)
                if result is not None:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                    oList.append( result.group(1))
                    iList.append( str(ind))
            else:
                skipLLines -= 1
        files.writeListToFile( tempFileName, oList)
        files.writeListToFile( indFileName, iList)

    app.pbTotal.pbReset()
    fileList = files.getFolderList( files.folderTEMP, ext='.rpy', withTL=True, withStat=True)
    totalLines, totalSizes, _, _, _ = getDicLastData( fileList)
    app.listFileUpdate(fileList)
    app.labelsSet(totalLines, totalSizes)
    # listFileStats( event, path=files.folderTEMP, withTL=True, withStat=True)


def getDicLastData( fileList: dict) -> tuple:
    lastKey    = list(fileList.keys())[-1]
    totalLines = fileList[lastKey]['linesTotal']
    totalSizes = fileList[lastKey]['sizeTotal']
    totalRPY   = fileList[lastKey]['totalRPY']
    totalRPYC  = fileList[lastKey]['totalRPYC']
    totalRPA   = fileList[lastKey]['totalRPA']
    return totalLines, totalSizes, totalRPY, totalRPYC, totalRPA


def btnMakeTransFilesThread():
    files.clearFolder( files.folderTRANS, '*')
    app.print( f'Translating from [`green`{app.lang.get()}`] to [`green`{app.trans.get()}`] language start...', True)

    fileList    = files.getFolderList(files.folderTEMP, '*', withStat=True, silent=True)
    totalLines,  totalSizes, _, _, _  = getDicLastData( fileList)
    totalFiles  = len( fileList)
    currentFile = currentLine = currentSize = 0

    app.listFileUpdate( fileList)
    app.labelsSet( totalLines, totalSizes)
    trans.listTransPrepare()

    for fileName, fileValue in fileList.items():
        app.listTLupdate( currentFile)
        currentFile += 1

        fileAllText, error = files.readFileToList( fileName)

        if not error:
            # print( totalLines, totalSizes, totalFiles, currentFile, fileValue['lines'], fileValue['size'], fileName)
            tList, error = trans.listTranslate( fileAllText, fileValue['fileShort'], tl=totalLines, ts=totalSizes, tf=totalFiles, cl=currentLine, cs=currentSize, cf=currentFile)
            currentLine += fileValue['lines']
            currentSize += fileValue['size']

            if not error:
                files.writeListToFile( files.folderTRANS + fileValue['fileShort'], tList)
            else:
                app.print( 'Error. Something going wrong...')
                return
    # reset button state text
    btnMakeTransFiles( False)
    app.listTLupdate( -1)


def btnMakeTransFiles(_event):
    # if app.btnTranslate['text'] == 'translate start':
    if ( 'trans' not in trans.threadSTOP) or ( not getattr( trans.threadSTOP['trans'], "do_run")):
        app.btnTranslate['text'] = 'translate stop'
        trans.threadSTOP['trans'] = threading.Thread(name='trans', target=btnMakeTransFilesThread, args=( ))
        trans.threadSTOP['trans'].do_run = True
        trans.threadSTOP['trans'].start()
    else:
        app.btnTranslate['text'] = 'translate start'
        # t = getThreadByName('trans') #Get thread by name
        trans.threadSTOP['trans'].do_run = False


def btnMakeRPYFiles(_event):
    app.print( 'compile renpy RPY files...', True)
    files.clearFolder( files.folderRPY, '*', )
    game.wordDicCount = 0
    fileList = files.getFolderList(files.folderTRANS, '.rpy', silent=True)
    for fileName in fileList:

        fileNameTrans   = files.folderTRANS + fileList[fileName]['fileShort']
        fileNameDone    = files.folderRPY   + fileList[fileName]['fileShort']
        fileNameInd     = files.folderIND   + fileList[fileName]['fileShort']
        fileNameOrig    = files.folderTL    + fileList[fileName]['fileShort']

        linesTranslated, _error = files.readFileToList( fileNameTrans)
        linesOriginal, _error   = files.readFileToList( fileNameOrig)
        linesIND, _error        = files.readFileToList( fileNameInd)
        for tIND, originalIND in enumerate( linesIND):
            if originalIND:
                originalIND = int( originalIND)
                oLine = linesOriginal[originalIND]
                # print(originalIND, tIND, oLine)
                tLine = linesTranslated[tIND]

                tLine = correctOpenBrackets( tLine, oLine)
                tLine = correctTranslate( tLine)
                tLine = correctWordDic( tLine)
                tLine = correctTagsBrackets( tLine, oLine)                                       # заменяем теги
                # if settings['engTRANS']:                                                 # если хочется иметь копию оригинальной строки внизу переведенной в игре
                #     tLine += settings['engLine'] + oLine

                linesOriginal[originalIND+1] = linesOriginal[originalIND + 1].replace('""', f'"{tLine}"')
        files.writeListToFile(fileNameDone, linesOriginal)
    app.print( f"wordDic replaced [`green`{game.wordDicCount}`] times.")


def runExternalCmd( path):
    app.print( '')
    if path and os.path.exists( path) and path.endswith( 'exe'):
        app.print( f'Start [`bold`{path}`]...')
        subprocess.call( f'"{path}"')
    else:
        app.print( f'Path not found: [{path}]')


def runThreadCmd( path):
    if path and os.path.exists( path):
        game.threadSTOP['run'] = threading.Thread( name='run', target=runExternalCmd, args=( path,))
        game.threadSTOP['run'].do_run = True
        game.threadSTOP['run'].start()


def btnTagsCopy( _event):
    tagListInsertRead(app.textEng)
    app.tagsCopy()


def btnRunGameClick( _event):
    pathGame = game.getPath()
    if not pathGame:
        return
    # arr_txt = [x for x in os.listdir() if x.endswith(".txt")]
    exeName = os.listdir( pathGame)
    exeName = sorted( list( filter(lambda fileName: fileName.endswith('.exe'), exeName)))[-1]

    if exeName and len( exeName) > 1:
        runThreadCmd( f'{pathGame}{exeName}')


def btnRunSDKClick( _event):
    if game.getPathGame():
        if os.path.exists( game.gameTLRUS):
            app.askClearFolder(game.gameTLRUS, f"Clear folder before run SDK? [{game.gameTLRUS}]")
    runThreadCmd( f'{files.folderSDK}renpy.exe')


def btnRPAExtractThread(pathGame):
    fileList = files.getFolderList(pathGame, '.rpa', onlyRoot=True)
    dicRPA = rpaArch.rpaGetListFilesExt( fileList)
    rpaArch.rpaExtractFiles( dicRPA, pathGame)


def btnRPAExtract(_event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    app.pbTotal.pbReset()
    game.threadSTOP['run'] = threading.Thread(name='run', target=btnRPAExtractThread, args=(pathGame,))
    game.threadSTOP['run'].do_run = True
    game.threadSTOP['run'].start()


# todo херня со четчиком гуд/бэд/еррор
def btnDecompileThread():
    if not game.pathPython:
        app.print( 'Python 2.7 in current folder not found!')
        return

    pathGame = game.getPathGame()
    if not pathGame:
        return

    app.pbTotal.pbSet()
    app.print( 'Start decompiling rpyc files..', True)

    good = 0
    bad = 0
    filesRPY = files.getFolderList(pathGame, '.rpyc')
    filesTotal = len( filesRPY)

    for fileCurrent, fileName in enumerate( filesRPY, 1):
        cmd = f'"{game.pathPython}" -O "unrpyc.py" -c --init-offset "{fileName}"'  # -l "rus" -T "{fileName}.trans"'
        # print( cmd)
        p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  #, cwd= f'{game.gameFolder}!renpy-7.3.5-sdk\\')
        out, err = p.communicate()
        out = out.decode('UTF-8')
        # print( out, err)
        result = out.split('\n')
        for line in result:
            if line == '1\r':
                good += 1
            elif line == '0\r':
                bad += 1
            elif len( line) > 3:
                percent = ( fileCurrent / filesTotal) * 100
                app.print( f'`rain{ round( percent)}`{line}`')
        app.pbTotal.pbSet( percent, f'{fileCurrent}/{filesTotal}')
    app.print( f'Decompiling complete. [{good}] files done with [{bad}] errors.', False)


def btnDecompile( _event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    game.threadSTOP['rpy'] = threading.Thread(name='rpy', target=btnDecompileThread)  #, args=( filesRPY))
    game.threadSTOP['rpy'].start()


def btnCopyRPYBack( event):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    copyTLStuff(event, old=files.folderRPY, new=f'{pathGame}tl\\rus\\', updateList=False)


def btnWordDicClick( _event=None):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    app.print( "")
    fileList = files.getFolderList(pathGame, ['.txt', '.rpy'])  # + 'tl\\rus\\')
    game.wordDicCount = 0
    # print( fileList)
    for fileName in fileList:
        tempList = []
        wordCountLocal = game.wordDicCount
        fileLines, error = files.readFileToList( fileName)
        for line in fileLines:
            line = correctWordDic(line)  # , fileList[fileName]['fileShort'])
            tempList.append( line)
        if game.wordDicCount != wordCountLocal:
            files.writeListToFile( fileName, tempList)
    app.print( f"wordDic replaced [`green`{game.wordDicCount}`] times.")


def listGamesDClick( _event):
    game.listGameDClick()
    app.gameNameLabelSet()
    getListFilesRPA()


# todo активировать 0й таб при копировании файлов в ТЛ
def tabOnChange( event):
    tabID = event.widget.index("current")
    if tabID == 0:
        return

    tabName     = event.widget.tab( tabID, "text")
    child       = app.tabList[tabName]['lb']
    folderName  = 'workFolder\\' + tabName

    if child.lastScan < files.getFolderTime( folderName):
        fileList = files.getFolderList(folderName, '*', withStat=True, silent=True)
        app.listFileUpdate(fileList, lb=child)
        child.lastScan = datetime.today().timestamp()

#######################################################################################################


def main():
    files.makeNewDirs()
    game.gameListScan( app)

    fileList = files.getFolderList(files.folderTL, ext='.rpy', withTL=True, withStat=True)
    totalLines, totalSizes, _, _, _ = getDicLastData(fileList)
    app.listFileUpdate(fileList)
    app.labelsSet(totalLines, totalSizes)
    findTagsInTLFolder(fileList)

    # listFileStats( app, files.folderTL)

    app.listGames.bind(     '<Double-1>',           listGamesDClick, add=True)
    app.btnGameRescan.bind( '<ButtonRelease-1>',    game.gameListScan)
    app.cbGameFolder.bind(  "<<ComboboxSelected>>", game.gameListScan)
    app.cbGamesSort.bind(   "<<ComboboxSelected>>", game.gameListScan)

    app.btnExtract.bind(    '<ButtonRelease-1>', btnRPAExtract)
    app.btnDecompile.bind(  '<ButtonRelease-1>', btnDecompile)
    app.btnRunRenpy.bind(   '<ButtonRelease-1>', btnRunSDKClick)
    app.btnFontsCopy.bind(  '<ButtonRelease-1>', btnCopyFontsStuff)
    app.btnMenuFinder.bind( '<ButtonRelease-1>', btnMenuFindVars)
    app.btnCopyTL.bind(     '<ButtonRelease-1>', copyTLStuff)
    # app.btnWordDic.bind(    '<ButtonRelease-1>', btnWordDicClick)

    app.btnTLScan.bind(     '<ButtonRelease-1>', listFileStats)
    app.btnMakeTemp.bind(   '<ButtonRelease-1>', btnMakeTempFiles)
    app.btnTranslate.bind(  '<ButtonRelease-1>', btnMakeTransFiles)
    app.btnMakeRPY.bind(    '<ButtonRelease-1>', btnMakeRPYFiles)
    app.btnCopyRPY.bind(    '<ButtonRelease-1>', btnCopyRPYBack)
    app.btnRunGame.bind(    '<ButtonRelease-1>', btnRunGameClick)

    app.btnTagCopy.bind(    '<ButtonRelease-1>', btnTagsCopy)
    app.btnTagClear.bind(   '<ButtonRelease-1>', app.tagsClear)
    app.btnTempRepl.bind(   '<ButtonRelease-1>', btnTagsChange)

    app.chAllEcxt['command'] = getListFilesRPA

    app.filemenu.insert_command( 1, label="Find & Replace")
    app.filemenu.insert_command( 2, label="WordDIC replacer", command=btnWordDicClick)

    app.tabControl.bind("<<NotebookTabChanged>>", tabOnChange)
    # app.after( 1000, app.updateUI())

    app.mainloop()


if __name__ == "__main__":
    main()


# def tabOnChange( event):
#     tabID = event.widget.index("current")
#     # print( event.widget.index( event.widget.select()))
#     selected_tab = event.widget.select()
#     tabName = selected_tab.split('.')[3]
#     tab_text = event.widget.tab(selected_tab, "text")
#     # print( selected_tab, tab_text, tabID, tabName)
#     objCurrentTab = event.widget.children[tabName]
#     self.tabList
#     if objCurrentTab.winfo_children() and tabID > 0:
#         listTabChilds = objCurrentTab.winfo_children()
#         for child in listTabChilds:
#             if isinstance(child, tk.Listbox):
#                 fileList = game.getListFilesByExt( '*', 'workFolder\\' + tab_text)
#                 fileTimeCheck = 0
#                 for _, fileData in fileList.items():
#                     if child.lastScan < fileData['fileTime']:
#                         fileTimeCheck += 1
#                         break
#                     # print(fileName, fileData['fileTime'])
#
#                 if fileTimeCheck > 0:
#                     fileList = game.getListFilesByExt('*', 'workFolder\\' + tab_text, withStat=True)
#                     app.listFileUpdate( fileList, lb=child)
#
#                 child.lastScan = datetime.today().timestamp()
#
#
# def btnMakeTempDicFiles(event):
#     game.listTempTags = {}
#     files.clearFolder( files.folderTEMP, '*')
#     app.textTag['state'] = tk.NORMAL
#     fileList = files.getFolderList(files.folderTL, '.rpy')
#
#     for fileName in fileList:
#         fileText, _error = files.readFileToList( fileName)
#         tempFileName = files.folderTEMP + fileList[fileName]['fileShort']
#
#         # oList = []
#         oDict = {}
#         skipLLines = 0
#         for ind, line in enumerate( fileText):
#             if ( skipLLines <= 0) and ( r' "' in line):
#                 line = line.replace( r'\"', r"'")
#                 skipLLines = 3
#                 result = reTrans.search( line)
#                 if result is not None:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
#                     oLine    = result.group(1)
#                     makeTempTagList(oLine)
#                     # oList.append( oLine)
#                     oDict[ind] = oLine
#             else:
#                 skipLLines -= 1
#         # writeListToFile( tempFileName, oList)
#         files.smartDirs(tempFileName)
#         with open( tempFileName, 'wb') as f:
#             pickle.dump( oDict, f)
#
#     tagListInsertRead(app.textTag, longStr=True)
#     app.textTag['state'] = tk.DISABLED
#     app.pbReset()
#     listFileStats( event, path=files.folderTEMP, withTL=True, withStat=True)


# def btnMakeRPYFiles(_event):
#     app.print( 'compile renpy RPY files...', True)
#     game.clearFolder( '*', files.folderRPY)
#     game.wordDicCount = 0
#     fileList = game.getListFilesByExt( '.rpy', files.folderTL)
#     for fileNameOrig in fileList:
#         lineFoundCount  = 0
#         fileNameTrans   = files.folderTRANS + fileList[fileNameOrig]['fileShort']
#         fileNameDone    = files.folderRPY   + fileList[fileNameOrig]['fileShort']
#
#         try:
#             skipLines = 0
#             linesTranslated, _error = readFileToList( fileNameTrans)
#             linesOriginal, _error   = readFileToList( fileNameOrig)
#
#             for lineCount, line in enumerate( linesOriginal):
#                 if ( skipLines <= 0) and ( r' "' in line):
#                     skipLines = 3
#                     # result = re.search( reTrans[0], line)
#                     line = line.replace(r'\"', r"'")
#                     result = reTrans.search(line)
#                     if result is not None:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
#                         oLine = result.group(1)
#                         tLine = linesTranslated[lineFoundCount]
#                         tLine = correctOpenBrackets( tLine, oLine)
#                         tLine = correctTranslate( tLine)
#                         tLine = correctWordDic( tLine, fileList[fileNameOrig]['fileShort'])
#                         tLine = correctTagsBrackets( tLine, oLine)                                       # заменяем теги
#
#                         if settings['engTRANS']:                                                 # если хочется иметь копию оригинальной строки внизу переведенной в игре
#                             tLine += settings['engLine'] + oLine
#
#                         # tLine = str( line.replace( str( oLine), tLine))                           # формируем результирующую строку ( не помню почему так, а не собрать нормальную
#                         lineFoundCount += 1
#                         linesOriginal[lineCount + 1] = linesOriginal[lineCount + 1].replace('""', f'"{tLine}"')  # записываем ее в массив как следующую строку
#                     else:
#                         tLine = line
#                         tLine = str( tLine.replace("    # ", "    "))
#                         tLine = str( tLine.replace("    old ", "    new "))
#                         linesOriginal[lineCount + 1] = tLine      # записываем ее в массив как следующую строку
#
#                 else:
#                     skipLines -= 1
#             writeListToFile( fileNameDone, linesOriginal)
#
#         except FileNotFoundError:
#             app.print( f'`red`Error.` File [{fileNameTrans}] not found or can`t read.')
#             # logging.error( f'Error. File [{fileNameTrans}] not found or can`t read.' )
#             # mb.showerror( 'error', f'trans file ( {fileNameTrans}) not found! make translate first.')
#             # break
#     app.print( f"wordDic replaced [`green`{game.wordDicCount}`] times.")
# return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
# findWholeWord('seek')('those who seek shall find')    # -> <match object>
# findWholeWord('word')('swordsmith')                   # -> None

# (.{2,5}?)([0-9]*) against this input: $50,000


# i = 5 if a > 7 else 0

# i = 5 | a > 7 | or | 0 |

# i = dic[c] or 1

# if c in dic.keys():
#     i = dic[c]
# else:
#     i = 1

# >>> a_dict = {'color': 'blue', 'fruit': 'apple', 'pet': 'dog'}
# >>> 'pet' in a_dict.keys()
# True
# >>> 'apple' in a_dict.values()
# True
# >>> 'onion' in a_dict.values()
# False

# >>> # Python 3.6, and beyond
# >>> incomes = {'apple': 5600.00, 'orange': 3500.00, 'banana': 5000.00}
# >>> sorted_income = {k: incomes[k] for k in sorted(incomes)}
# >>> sorted_income
# {'apple': 5600.0, 'banana': 5000.0, 'orange': 3500.0}

# >>> incomes = {'apple': 5600.00, 'orange': 3500.00, 'banana': 5000.00}
# >>> def by_value(item):
# ...     return item[1]
# ...
# >>> for k, v in sorted(incomes.items(), key=by_value):
# ...     app.print(k, '->', v)
# ...
# ('orange', '->', 3500.0)
# ('banana', '->', 5000.0)
# ('apple', '->', 5600.0)

# >>> for value in sorted(incomes.values()):
# ...     app.print(value)
# ...
# 3500.0
# 5000.0
# 5600.0


# def a():
#     t = threading.currentThread()
#     while getattr(t, "do_run", True):
#     app.print('Do something')
#     time.sleep(1)

# def getThreadByName(name):
#     threads = threading.enumerate() #Threads list
#     for thread in threads:
#         if thread.name == name:
#             return thread

# threading.Thread(target=a, name='228').start() #Init thread
# t = getThreadByName('228') #Get thread by name
# time.sleep(5)
# t.do_run = False #Signal to stop thread
# t.join()

# src_str  = re.compile("this", re.IGNORECASE)
# str_replaced  = src_str.sub("that", "This is a test sentence. this is a test sentence. THIS is a test sentence.")
# print(re.escape('https://www.python.org'))
# https://www\.python\.org

# redata = re.compile(re.escape('php'), re.IGNORECASE)
# new_text = redata.sub('php', 'PHP Exercises')
