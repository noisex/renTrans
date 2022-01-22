# "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$",
# https://www.sublimetext.com/docs/build_systems.html#exec_options

import os
import re
import threading
import shutil

import subprocess
import tkinter as tk
# import tkinter.ttk as ttk
# from datetime import datetime
from shutil import ignore_patterns  # copytree, rmtree
# from tkinter import messagebox as mb

from fontTools.ttLib import TTFont

from settings import settings
from guiClass import YoFrame
from gameClass import GameRenpy
from transClass import Translator, RPAClass
########################################################################################################################
color = "#222222"
colors = "#2b2b2b"

# app         = None
# game        = None
# rpaArch     = None
# trans       = None

reZamena = [
    '(\\[\\w+?\\])',
    '(\\%\\(\\w+?\\)s)',
]

reBrackets  = [
    '(\\[.+?\\])',          # квадратные скобки  - []
    '({.+?})',              # фигурные скобки    - {}
    '(\\%\\(.+?\\))'        # процент со скобкой - %()
]

reFix       = re.compile(r'\b\w{3,15}\b')  # ищем слова 4+ для замены по словарю
reTrans     = re.compile(r'"(.*[\w].*)"'), 0, 0

extensions  = {'.ttf', '.otf'}
itemSize    = '{size=-5}{color=#777}'

reMenu      = '\\s{4,}menu:'
reSpace     = '\\s{4}'
########################################################################################################################


def smartDirs( path):
    try:
        os.makedirs( os.path.dirname( path))
    except FileExistsError:
        pass


def fileCopy( filePath):
    fileNewName = filePath.replace( f'{game.getPathGame()}', '')
    fileBackPath = f'{game.getPath()}\\{game.getBackupFolder()}\\game\\{os.path.dirname( fileNewName)}\\'
    fileBackFile = fileBackPath + os.path.basename( filePath)

    os.makedirs( fileBackPath, exist_ok=True)
    shutil.copy2( filePath, fileBackFile)  # complete target filename given


def stringLevel( oLine: str) -> int:
    """back indent level of current line"""
    spaceResult = re.findall( reSpace, oLine)
    return len(spaceResult)


# def spacePrint( spaces: int) -> str:
#     """ back 4x-time spaces"""
#     ret = ''
#     for i in range( spaces * 4):
#         ret =  ret + ' '
#     return ret


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
                game.itemDict[filePath][itemsStrID] = itemSize

            game.itemDict[filePath][itemsStrID] += f' ({line})'
            # menuDict[menuID]['vars'].append( line)
            # menuDict[menuID]['items'][-1] = tList.replace( '\":', f' [{line}]\":')
            # itemsID = list( game.itemDict.keys())[-1]
            # game.itemDict[itemsStrID] = menuDict[menuID]['items'][-1]
            # print( f'{spacePrint(level)}{line} {tList} {menuID} {itemsID}')


def menuFileRead( filePath: str, fileText: list):
    menuDict = {}
    menuList = {}
    lineID = 0
    menuID = 0

    for line in fileText:
        lineID += 1

        oResultSC = re.findall( reMenu, line)
        spaceLevel = stringLevel( line)

        if oResultSC:
            menuID += 1
            menuList[spaceLevel] = menuID
            menuDict[menuID] = { 'id': menuID, 'itemsID': [], 'filePath': filePath}
            # , 'level': spaceLevel, 'start': lineID, 'items': [], 'vars': []}

        # если еще есть незакрытые менюхи и есть данные - анализ этой строки
        elif len( menuList) > 0 and len( line) > 0:
            checkMenuList( spaceLevel, lineID, line, menuList, menuDict)


def itemClearFromOld( line: str, strReplace: str) -> str:
    """очищаем строку от добавленных ранее подсказок"""
    itemStart = line.find( itemSize)
    if itemStart > 0:
        itemEnd = line.find( strReplace)
        strFull = line[0:itemStart] + line[itemEnd:]
    else:
        strFull = line

    return strFull


def menuFileWrite( filePath: str, fileText: list, fileShort: str) -> None:
    if len( game.itemDict[filePath]) < 2:
        return

    lineID = 0
    fileCopy( filePath)

    with open( f'{filePath}', 'w', encoding='utf-8') as f:
        app.print( f'-=> [{fileShort}]')

        for line in fileText:
            lineID += 1

            if lineID in game.itemDict[filePath]:

                if '":' in line:   # если вконце меню есть ИФ или еще что-то
                    strReplace = '":'
                else:
                    strReplace = '" '

                line = itemClearFromOld( line, strReplace)
                line = line.replace( strReplace, game.itemDict[filePath][lineID] + strReplace)
                app.log.error( f'[{lineID}] = [{line.strip()}]')

            f.write( line + '\n')


def findMenuStart( _event):
    fileList = game.getListFilesByExt( '.rpy', False, False)
    game.makeNewBackupFolder()
    app.print( f'finding menu with variables ( backUp in [{game.backupFolder}])...', True)
    for filePath in fileList:
        with open( filePath, encoding='utf-8') as infile:
            fileText = infile.read().split('\n')

        game.itemDict[filePath] = {}
        menuFileRead( filePath, fileText)
        menuFileWrite( filePath, fileText, fileList[filePath]['fileShort'])

########################################################################################################################


def copyTLStuff( event, old=None, new=None, updateList=True):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    if not old:
        old = f'{pathGame}tl\\rus\\'
    if not new:
        new = game.folderTL

    if os.path.exists( old) and os.path.exists( new):
        game.clearFolder( '*', new)
        shutil.copytree( old, new, dirs_exist_ok=True, ignore=ignore_patterns('*.rpyc', 'xxx_*', 'common.rpy', 'options.rpy', 'screens.rpy'))
        app.print( f'Files from [{old}] copied to [{new}].', True)
        if updateList:
            listFileStats( event)
    else:
        app.print( f'ERROR: folder [{old}] not found. {os.path.exists( new)}', True)


def scanInputFolder( _event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    char = 1060
    # myFonts = ['cormac.ttf', 'qFont.ttf', 'webfont.ttf',]

    app.print( 'Start search non-rus fonts and replace them...', True)
    shutil.copytree( f'{game.gameFolder}game\\', pathGame, dirs_exist_ok=True)

    fileList = game.getListFilesByExt( '.ttf, .otf')

    for fileName, fileValue in fileList.items():
        font = TTFont( fileName)
        for cmap in font['cmap'].tables:
            if cmap.isUnicode():
                if char in cmap.cmap:
                    app.print( f"Good font: [{fileValue['fileShort']}]")
                    # break
                else:
                    app.print( f"Badz font: [{fileValue['fileShort']}]", tag='bold')
                    shutil.copy2( pathGame + 'webfont.ttf', fileName)  # complete target filename given
                break


def decompileRPYCFiles():

    if not os.path.exists( game.pathPython):
        app.print( 'Python 2.7 in current folder not found!')
        return

    app.pbReset()
    app.print( 'Start decompiling rpyc files..', True)

    good = 0
    bad = 0
    filesRPY = game.getListFilesByExt( '.rpyc')
    filesTotal = len( filesRPY)
    fileCurrent = 0

    for fileName in filesRPY:
        fileCurrent += 1
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
                app.print(line)

        app.pbSet(( fileCurrent / filesTotal) * 100, f'{fileCurrent}/{filesTotal}')

    app.print( f'Decompiling compete. [{good}] files done with [{bad}] errors.', False)


def getListFilesRPA():
    filesRPY = 0
    filesFonts = 0

    if game.getPathGame():
        fileList = game.getListFilesByExt( '.rpa')
        archFileList = rpaArch.rpaGetFilesStats( fileList)
        app.print( '')

        for archFile, archValues in archFileList.items():
            app.print( f'-=> [{archFile}] [{archValues["size"]:,.1f} mb] [{archValues["count"]:,} files]')
            filesRPY   += archValues["rpycFiles"]
            filesFonts += archValues["fontsFiles"]

        if filesRPY >= 1:
            app.print( f'with [{filesRPY}] RPYC files in achieves.')
        if filesFonts >= 1:
            app.print( f'with [{filesFonts}] Fonts files in archives.')


def listFileStats( _event, path=False, withTL=True, withStat=False, ext='.rpy'):
    if not path:
        path = game.folderTL

    fileList = game.getListFilesByExt( ext=ext, gamePath=path, withTL=withTL, withStat=withStat)

    # app.print( f'found [{len(fileList)}] files in [{path}]. ')
    app.listFileUpdate( fileList)


def findDicReplacer( fix: str) -> str:
    fixRE   = re.findall( reFix, fix)
    wordDic = settings['wordDic']

    for item in fixRE:
        itemLow = item.lower()

        if itemLow in wordDic:
            game.wordDicCount += 1

            if item == itemLow:
                itemRET = wordDic[itemLow]
            elif item == item.upper():
                itemRET = wordDic[itemLow].upper()
            elif item == item.capitalize():
                itemRET = wordDic[itemLow].capitalize()
            else:
                itemRET = wordDic[itemLow]

            fix = re.sub( f'\b{item}\b', itemRET, fix)
    return fix


# TODO процент с цыфрой без экрана
def findCorrect( fix):                                                 # корректировка всяких косяков первода, надо перписать...
    # %(РС - %(p_name)s
    fix = re.sub( r'([-~])$', r'.', fix)                                           # -" => ."
    fix = re.sub( '^да', 'Да', fix)
    fix = re.sub( r'(\s+)([.!?,])', r'\2', fix)                               # убираем парные+ пробелы и пробелы перед знаком препинания

    fix = re.sub( r'К[аА][кК][иИоО]\w([-.!?])', r'Что\1', fix)         # Какие -> Что
    fix = re.sub( r'Большой([.!?])', r'Отлично\1', fix)
    fix = re.sub( r'Прохладный([.!?])', r'Здорово\1', fix)

    fix = re.sub( r'([A-ZА-Я])-([а-яА-Я])(\w+)', r'\2-\2\3', fix)                     # T-Спасибо -=> С-Спасибо
    fix = re.sub( r'(\d+)\W*%', r'\1\%', fix)                                   # 123% => 123\%

    fix = fix.replace( '\\"', '\'')
    fix = fix.replace( '"', '\'')
    fix = fix.replace( '% (', ' %(')
    fix = fix.replace( '} ', '}')
    # fix = fix.replace( ' {/', '{/')
    fix = re.sub( r'\\$', '', fix)

    fix = re.sub( '\\) [ысs]', '\\)s', fix, flags=re.I)
    fix = re.sub( r'\\ n', r'\\n', fix, flags=re.I)
    fix = re.sub( '{я[ }]', '{i}', fix, flags=re.I)
    # if fix.find( 'Какие') >= 0:
    #     app.print( str( fix))
    return fix


def findSkobki( tLine: str, oLine: str):                                      # замена кривых, т.е. всех, переведенных тегов на оригинальные
    for re_find in reBrackets:
        tResultSC = re.findall(re_find, tLine)                              # ищем теги в скобках в оригинальной строке

        if tResultSC:
            oResultSC = re.findall(re_find, oLine)                          # ищем теги в скобках в переведенной строке
            for i, value in enumerate( oResultSC):

                try:
                    if tResultSC[i] != '[123]':
                        tLine = tLine.replace( tResultSC[i], value)              # заменяем переведенные кривые теги оригинальными по порядку
                    # else:
                    #     tLine = tLine.replace( '[123]', '')
                except RuntimeError:
                    pass

    return tLine.replace( '[123]', '')


def insertZamenaInText( textBox=None, longStr=None, retList=None):
    if textBox:
        textBox.delete( '1.0', tk.END)
    returnList = []

    sorted_income = {k: game.dictZamena[k] for k in sorted(game.dictZamena)}
    for zamane in sorted_income:
        if retList:
            returnList.append( game.dictZamena[zamane]["item"])
        else:
            if longStr:
                textBox.insert( tk.END, f'{game.dictZamena[zamane]["count"]:3}| {game.dictZamena[zamane]["item"]}\n')
            else:
                textBox.insert( tk.END, f'{game.dictZamena[zamane]["item"]}\n')

    return returnList


def findTempBrackets( _event):
    app.print( 'change brackets in temp files...', True)
    dictTemp    = {}
    textLine01  = insertZamenaInText( retList=True)
    texLineEng  = app.textEng.get(1.0, tk.END)
    textLine02  = texLineEng.split('\n')

    if len( texLineEng) <= 1:
        app.print( ' -=> nothing to change, skipped...', False, True)
        return

    for i, line in enumerate(textLine02):
        if len( line) >= 1:
            try:
                if line != textLine01[i] and len(textLine01[i]) > 1:
                    dictTemp[textLine01[i]] = { 'data': line, 'count': 0}
            except RuntimeError as e:
                app.print( f'!!! {line} -=> Skipped [{e}]')

    fileList = game.getListFilesByExt( '.rpy', game.folderTEMP)
    fileCurrent = 0
    fileTotal = len( fileList)

    for fileNameTemp in fileList:
        fileCurrent += 1
        app.pbSet( ( fileCurrent / fileTotal) * 100)
        app.listTLupdate( fileCurrent)

        with open( fileNameTemp, 'r', encoding='utf-8') as file:
            fileData = file.read()

        for tempLine, tempValue in dictTemp.items():
            if tempLine != tempValue['data']:
                tempValue['count'] += fileData.count( tempLine)
                fileData = fileData.replace( tempLine, str( tempValue['data']) + '[123]')

        with open( fileNameTemp, 'w', encoding='utf-8') as file:
            file.write(fileData)

    for tempLine, tempValue in dictTemp.items():
        app.print( f' -=> {tempValue["count"]:3} {tempLine} -=> {tempValue["data"]}')

    app.listTLupdate()
    # fileTRans['setting']['dictTemp'] = dictTemp


def findZamena( oLine: str):
    for reZam in reZamena:
        oResult = re.findall( reZam, oLine)

        if oResult:
            for value in oResult:
                if value not in game.dictZamena:
                    game.dictZamena[value] = { 'count': 0, 'item': value}  # выписываем в словарь тэги в квадратных скобках
                game.dictZamena[value]['count'] += 1


def makeTempFiles( event):
    game.dictZamena = {}
    game.clearFolder( '*', game.folderTEMP)
    app.textTag['state'] = tk.NORMAL
    fileList = game.getListFilesByExt( '.rpy', game.folderTL)

    for fileName in fileList:
        with open( fileName, encoding='utf-8') as f:
            skip01  = 0
            fileText = f.read().split('\n')
            tempFileName = game.folderTEMP + fileList[fileName]['fileShort']
            # print( tempFileName, game.folderTEMP, fileList[fileName]['fileShort'])
            smartDirs( tempFileName)

            with open( tempFileName, 'w', encoding='utf-8') as fw:
                for line in fileText:
                    if r' "' in line and skip01 == 0:
                        # skip01 = 0
                        skip01 = 1

                        result = re.search( reTrans[0], line)
                        if result:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                            oLine    = result.group(1)
                            oLine    = oLine.replace( '"', "'")
                            fw.write( str( oLine) + '\n')
                            findZamena( oLine)
                    else:
                        skip01 = 0

    insertZamenaInText( app.textTag, longStr=True)
    app.textTag['state'] = tk.DISABLED
    app.pbReset()
    listFileStats( event, path=game.folderTEMP, withTL=True, withStat=True)


def treatTranslate( _event):
    # if app.btnTranslate['text'] == 'translate start':
    if ( 'trans' not in trans.threadSTOP) or ( not getattr( trans.threadSTOP['trans'], "do_run")):
        app.btnTranslate['text'] = 'translate stop'

        trans.threadSTOP['trans'] = threading.Thread( name='trans', target=makeTransFilesList, args=( ))
        trans.threadSTOP['trans'].do_run = True
        trans.threadSTOP['trans'].start()
    else:
        app.btnTranslate['text'] = 'translate start'
        # t = getThreadByName('trans') #Get thread by name
        trans.threadSTOP['trans'].do_run = False


def makeTransFilesList():
    game.clearFolder( '*', game.folderTRANS)
    app.print( f'translating from [{app.lang.get()}] to [{app.trans.get()}] language start...', True)

    currentFile = 0
    fileList    = game.getListFilesByExt( '*', game.folderTEMP, withStat=True)
    app.listFileUpdate( fileList)
    trans.listTransPrepate( len( fileList))

    for fileName, fileValue in fileList.items():
        app.listTLupdate( currentFile)
        currentFile   += 1
        fileTransName = game.folderTRANS + fileValue['fileShort']
        smartDirs( fileTransName)

        for encode in settings['encList']:
            try:
                with open( fileName, encoding=encode) as f:
                    fileAllText = f.read().split('\n')

                tList = trans.listTranslate( fileAllText, fileValue['fileShort'])

                if tList:
                    with open( fileTransName, 'a', encoding='utf-8') as f:
                        for line in tList:
                            f.write( line)
                else:
                    app.print( 'Error. Something going wrong...', True)
                    return
            except RuntimeError:
                pass

    # reset button state text
    treatTranslate( None)
    app.listTLupdate( -1)


def makeRPYFiles( event):
    app.print( 'start compile renpy files', True)
    game.clearFolder( '*', game.folderRPY)

    game.wordDicCount = 0
    fileList = game.getListFilesByExt( '.rpy', game.folderTL)
    for fileNameOrig in fileList:

        lineFoundCount  = 0
        fileNameTrans   = game.folderTRANS + fileList[fileNameOrig]['fileShort']
        fileNameDone    = game.folderRPY   + fileList[fileNameOrig]['fileShort']
        smartDirs( fileNameDone)

        try:
            with open( fileNameTrans, encoding='utf-8') as f:
                linesTemp = f.read().split('\n')

            with open( fileNameOrig, encoding='utf-8') as f:
                skip01 = 0
                fileAllText = f.read().split('\n')

                for lineCount, line in enumerate( fileAllText):
                    if r' "' in line and skip01 == 0:
                        # skip01 = 0
                        skip01 = 1
                        result = re.search( reTrans[0], line)

                        if result:
                            oLine = result.group(1)
                            tLine = linesTemp[lineFoundCount]

                            tLine = findCorrect( tLine)
                            tLine = findDicReplacer( tLine)
                            tLine = findSkobki( tLine, oLine)                                       # заменяем теги

                            if settings['engTRANS']:                                                 # если хочется иметь копию оригинальной строки внизу переведенной в игре
                                tLine += settings['engLine'] + oLine

                            tLine = str( line.replace( str( oLine), tLine))                           # формируем результирующую строку ( не помню почему так, а не собрать нормальную
                            lineFoundCount += 1
                        else:
                            tLine = line

                        tLine = str( tLine.replace("    # ", "    "))
                        tLine = str( tLine.replace("    old ", "    new "))
                        fileAllText[lineCount + 1] = tLine                                             # записываем ее в массив как следующую строку
                    else:
                        skip01 = 0

                with open( fileNameDone, 'w', encoding='utf-8') as fw:
                    for i in fileAllText:
                        fw.write(str(i) + '\n')

        except FileNotFoundError:
            app.print( f'Error. File [{fileNameTrans}] not found or can`t read.')
            # logging.error( f'Error. File [{fileNameTrans}] not found or can`t read.' )
            # mb.showerror( 'error', f'trans file ( {fileNameTrans}) not found! make translate first.')
            # break

    app.print( f"wordDic replaced [{game.wordDicCount}] times.", tag='bold')

    pathGame = game.getPathGame()
    if not pathGame:
        return
    copyTLStuff( event, old=game.folderRPY, new=f'{pathGame}tl\\rus\\', updateList=False)


def runExternalCmd( path):
    if path and os.path.exists( path) and path.endswith( 'exe'):
        app.print( f'running [{path}]...', True)
        subprocess.call( f'"{path}"')
    else:
        app.print( f'path not found: [{path}]')


def runThreadCmd( path):
    if path and os.path.exists( path):
        game.threadSTOP['run'] = threading.Thread( name='run', target=runExternalCmd, args=( path,))
        game.threadSTOP['run'].do_run = True
        game.threadSTOP['run'].start()


def btnTagsCopy( _event):
    insertZamenaInText( app.textEng)
    app.tagsCopy()


def btnRunGameClick( _event):
    pathGame = game.getPath()
    if not pathGame:
        return
    # arr_txt = [x for x in os.listdir() if x.endswith(".txt")]
    exeName = os.listdir( pathGame)
    exeName = sorted( list( filter(lambda fileName: fileName.endswith('.exe'), exeName)))[-1]

    if exeName and len( exeName) > 1:
        runThreadCmd( f'{pathGame}\\{exeName}')


def btnRunSDKClick( _event):
    runThreadCmd( f'{game.folderSDK}renpy.exe')


def btnExtractThread( pathGame):
    fileList = game.getListFilesByExt( '.rpa')
    dicRPA = rpaArch.rpaGetListFilesExt( fileList)
    rpaArch.rpaExtractFiles( dicRPA, pathGame)


def btnExtract( _event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    app.pbReset()
    game.threadSTOP['run'] = threading.Thread( name='run', target=btnExtractThread, args=( pathGame,))
    game.threadSTOP['run'].do_run = True
    game.threadSTOP['run'].start()


def btnDecompile( _event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    game.threadSTOP['rpy'] = threading.Thread(name='rpy', target=decompileRPYCFiles)  #, args=( filesRPY))
    game.threadSTOP['rpy'].start()


def listGamesDClick( _event):
    game.listGameDClick()
    app.gameListSet()
    getListFilesRPA()

#######################################################################################################


def main():
    global app
    global game
    global rpaArch
    global trans

    app     = YoFrame()
    game    = GameRenpy(app)        
    rpaArch = RPAClass(app, game)
    trans   = Translator(app, game)
    game.gameListScan( app)
    listFileStats( app, game.folderTL)

    app.listGames.bind('<Double-1>', listGamesDClick)

    app.btnGameRescan.bind( '<ButtonRelease-1>', game.gameListScan)
    app.btnExtract.bind('<ButtonRelease-1>', btnExtract)
    app.btnDecompile.bind('<ButtonRelease-1>', btnDecompile)
    app.btnRunRenpy.bind('<ButtonRelease-1>', btnRunSDKClick)
    app.btnFontsCopy.bind('<ButtonRelease-1>', scanInputFolder)
    app.btnMenuFinder.bind('<ButtonRelease-1>', findMenuStart)
    app.btnCopyTL.bind('<ButtonRelease-1>', copyTLStuff)

    app.btnTLScan.bind('<ButtonRelease-1>', listFileStats)
    app.btnMakeTemp.bind('<ButtonRelease-1>', makeTempFiles)
    app.btnTranslate.bind('<ButtonRelease-1>', treatTranslate)
    app.btnMakeRPY.bind('<ButtonRelease-1>', makeRPYFiles)
    # app.btnALL.bind('<ButtonRelease-1>', makeALLFiles)
    app.btnRunGame.bind('<ButtonRelease-1>', btnRunGameClick)

    app.btnTagCopy.bind('<ButtonRelease-1>', btnTagsCopy)
    app.btnTagClear.bind('<ButtonRelease-1>', app.tagsClear)
    app.btnTempRepl.bind('<ButtonRelease-1>', findTempBrackets)

    app.chAllEcxt['command'] = getListFilesRPA

    app.after(1000, app.updateUI)
    app.mainloop()


if __name__ == "__main__":
    main()


# sizeGrip    = ttk.Sizegrip(groupBot)
# sizeGrip.grid( row=0, column=6, sticky=tk.SE)


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
