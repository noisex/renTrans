import os
import re
import time
import threading
import logging
import sys
import shutil
from shutil import copytree, ignore_patterns, rmtree

import subprocess

from unrpa import UnRPA

import tkinter as tk
import tkinter.ttk as ttk

from datetime import datetime
from tkinter import messagebox as mb

from guiClass import yoFrame
from gameClass import gameRenpy
from transClass import translator

from fontTools.ttLib import TTFont
########################################################################################################################

fileStat    = {}
dictZamena  = {}
threadSTOP  = False
allStart    = False
TRLEN       = 4990 # 4700 for GoogleTranslate

extTEMP     = 'tmp'
extTRANS    = 'transl'

testRun     = False
# testRun     = True
engTRANS    = False
testWait    = 0.1

dicRPA      = {}
itemDict    = {}

wordDic = {
    'вереск':   'Хизер',
    'мед':      'милый',
    'медовый':  'милый',
    'членом':   'хуем',
    'члена':    'хуя',
    'члены':    'хуи',
    'члене':    'хуе',
    'член':     'хуй',
    'петух':    'хуй',
    'петуху':   'хую',
    'члену':    'хую',
    'киска':    'пизда',
    'киску':    'пизду',
    'киски':    'пизды',
    'киске':    'пизде',
    'киску':    'пизду',
    'киской':   'пиздой',
    'трахать':  'ебать',
    'трахаю':   'ебу',
    'трахнул':  'выебал',
    'трахал':   'ебал',
    'трахнуть': 'выебать',
    'трахни':   'выеби',
    'трахаешь': 'ебешь',
    'трахают':  'ебут',
    'трахнули': 'выебали',
    'трахаться':'ебаться',
    'олухи':    'сиськи',
    'щенки':    'сиськи',
    'задницу':  'жопу',
    'диплом':   'кончить',
    'перебирать':   'дрочить',
    'мастурбировать':   'дрочить',
    'мастурбирую':      'дрочу',
}

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

extensions  = set([ '.ttf', '.otf'])
itemSize    = '{size=-5}{color=#777}'

reMenu      = '\\s{4,}menu:'
reSpace     = '\\s{4}'

logging.basicConfig(filename='example.log', format='%(asctime)s %(message)s', datefmt='%Y.%m.%d %H:%M:%S', encoding='utf-8', level=logging.ERROR)
############################################################################################################################

def smartDirs( path):
    try:
        os.makedirs( os.path.dirname( path))
    except:
        pass

def fileCopy( filePath=str):
    fileNewName = filePath.replace( f'{game.getPathGame()}', '')
    fileBackPath = f'{game.getPath()}\\{game.getBackupFolder()}\\game\\{os.path.dirname( fileNewName)}\\'
    fileBackFile = fileBackPath + os.path.basename( filePath)

    os.makedirs( fileBackPath, exist_ok=True)
    shutil.copy2( filePath, fileBackFile) # complete target filename given


def stringLevel( oLine=str) -> str:
    spaceResult = re.findall( reSpace, oLine)
    return len(spaceResult)


def spacePrint( spaces=int):
    ret = ''
    for i in range( spaces * 4):
        ret =  ret + ' '
    return ret


def clearItem( line: str) -> str:
    line = line.replace( '$', '')
    line = line.replace( '"', '')

    tComm = line.find( '#')
    if tComm > 1:
        line = line[0:tComm]

    line = line.strip()
    line = line[0: 30]
    return line


def clearMenuList( menuList=list, level=int):
    retList = {}
    ### обновляем менюлист пуктами, которые еще не закрыты
    for menuLevel in menuList:
        if menuLevel < level:
            retList[menuLevel] = menuList[menuLevel]

    return retList


def checkMenuList( level=int, lines=int, line=str, menuList=dict, menuDict=list):
    global itemDict

    menuList = clearMenuList( menuList, level)

    for menuLevel in menuList:

        menuID = menuList[menuLevel]
        filePath = menuDict[menuID]['filePath']

        ### ближе чем меню - закрываем меню
        # if level <= menu:
        #     menuDict[menuID]['end'] = lines

        ### следующий уровень - пишем пункт меню
        if level == menuLevel + 1 and line.find( '  "') > 1 :
            # menuDict[menuID]['items'].append( line)
            menuDict[menuID]['itemsID'].append( lines)

        ### текст тела меню - ищем переменные и пишем
        if level == menuLevel + 2                \
            and line.find( '  $') > 1       \
            and line.find( '=') > 1         \
            and line.find( 'renpy') < 1:

            line = clearItem( line)
            itemsStrID = menuDict[menuID]['itemsID'][-1]

            ### если нет еще итемов на данный пункт - создать пустой
            if itemsStrID not in itemDict[filePath]:
                itemDict[filePath][itemsStrID] = itemSize

            itemDict[filePath][itemsStrID] += f' ({line})'
            # menuDict[menuID]['vars'].append( line)
            # menuDict[menuID]['items'][-1] = tList.replace( '\":', f' [{line}]\":')
            # itemsID = list( itemDict.keys())[-1]
            # itemDict[itemsStrID] = menuDict[menuID]['items'][-1]
            # print( f'{spacePrint(level)}{line} {tList} {menuID} {itemsID}')


def menuFileRead( filePath=str, fileText=list):
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
            menuDict[menuID] = { 'id': menuID, 'itemsID': [], 'filePath': filePath} #, 'level': spaceLevel, 'start': lineID, 'items': [], 'vars': []}

        ### если еще есть незакрытые менюхи и есть данные - анализ этой строки
        elif len( menuList) > 0 and len( line) > 0:
            checkMenuList( spaceLevel, lineID, line, menuList, menuDict)


def itemClearFromOld( line=str, strReplace=str) -> str:
    itemStart = line.find( itemSize)
    if itemStart > 0:
        itemEnd = line.find( strReplace)
        strFull = line[0:itemStart] + line[itemEnd:]
    else:
        strFull = line

    return strFull


def menuFileWrite( filePath=str, fileText=list, fileShort=str):
    if len( itemDict[filePath]) < 2:
        return

    lineID = 0
    fileCopy( filePath)
    # oprint( itemDict)

    tmpFile = open( f'{filePath}', 'w', encoding='utf-8')
    logging.error( f'[{filePath}]')
    app.print( f'menu finded in [{fileShort}]')

    for line in fileText:
        lineID += 1

        if lineID in itemDict[filePath]:

            if line.find( '":') > 10:   # если вконце меню есть ИФ или еще что-то
                strReplace = '":'
            else:
                strReplace = '" '

            line = itemClearFromOld( line, strReplace)
            line = line.replace( strReplace, itemDict[filePath][lineID] + strReplace)
            logging.error( f'-=> [{lineID}] = [{line.strip()}]')

        tmpFile.write( line + '\n')
    tmpFile.close()


def findMenuStart( event):
    fileList = game.getListFilesByExt( '.rpy', False, False)
    game.makeNewBackupFolder()
    app.print( 'finding menu with variablles...', True)
    for filePath in fileList:
        with open( filePath, encoding='utf-8') as infile:
            fileText = infile.read().split('\n')

        itemDict[filePath] = {}
        menuFileRead( filePath, fileText)
        menuFileWrite( filePath, fileText, fileList[filePath]['fileShort'])

#####################################################################################################################################

def copyTLStuffBack():
    pathGame = game.getPathGame()
    if not pathGame:
        return

    old = game.folderRPY
    new = f'{pathGame}tl\\rus\\'

    clearFolder( '*', new)

    shutil.copytree( old, new, dirs_exist_ok=True)
    app.print( f'Files from [{old}] copied back to [{new}].')

def copyTLStuff( event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    old = f'{pathGame}tl\\rus\\'
    new = game.folderTL
    clearFolder( '*', new)
    shutil.copytree( old, new, dirs_exist_ok=True, ignore=ignore_patterns('*.rpyc', 'xxx_*', 'common.rpy', 'options.rpy', 'screens.rpy'))
    app.print( f'Files from [{old}] copied to [{new}].')
    listFileStats( event)


def scanInputFolder( event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    char =  1060
    myFonts = ['cormac.ttf', 'qFont.ttf', 'webfont.ttf',]

    app.print( 'Start search non-rus fonts and replace them...', True)
    shutil.copytree( f'{game.gameFolder}game\\', pathGame, dirs_exist_ok=True)

    fileList = game.getListFilesByExt( '.ttf, .otf')

    for fileName in fileList:
        font = TTFont( fileName)
        for cmap in font['cmap'].tables:
            if cmap.isUnicode():
                if char in cmap.cmap:
                    app.print( f"Good font: [{fileList[fileName]['fileShort']}]")
                    break
                else:
                    app.print( f"Badz font: [{fileList[fileName]['fileShort']}]")
                    shutil.copy2( pathGame + 'webfont.ttf', fileName) # complete target filename given
                    break


def read_rpyc_data( ):

    if not os.path.exists( f'{game.getPath()}\\lib\\windows-i686\\python.exe'):
        app.print( 'Python 2.7 in current follder not found!')
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
        cmd = f'"{game.getPath()}lib\\windows-i686\\python.exe" -O "unrpyc.py" -c --init-offset "{fileName}"'
        print( cmd)
        percent = str( round((( fileCurrent / filesTotal) * 100), 2))
        app.pbSet( percent, f'{fileCurrent}/{filesTotal}')

        p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)#, cwd= f'{game.gameFolder}!renpy-7.3.5-sdk\\')
        out, err = p.communicate()
        out = out.decode('UTF-8')
        # print( out, err)
        result = out.split('\n')
        for line in result:
            if line == '1\r':
                good +=1
            elif line == '0\r':
                bad +=1
            elif len( line) > 3:
                app.print(line)

    app.print( f'Decompiling compete. {good} files done with {bad} errors.', False)


def gameScanRPA():
    global dicRPA

    pathGame = game.getPathGame()
    filesRPY = 0
    filesFonts = 0
    dicRPA = {}

    if os.path.exists( pathGame):
        app.print( f'Game: {game.gameName}', True)

        fileList = game.getListFilesByExt( '.rpa')
        foundRPA = len( fileList)

        for fileName in fileList:
            fileSize = os.path.getsize( fileName) / ( 1024 *1024)

            extractor = UnRPA( fileName)
            archNames = extractor.list_files()
            archNamesCount = len( archNames)

            app.print( f" [{fileList[fileName]['fileShort']}] [{fileSize:,.1f} mb] [{archNamesCount:,} files]")

            for fileArchName in archNames:
                # if fileName.endswith( '.rpy'):
                    # print( f'{i} - {fileName}')
                    # filesRPY.append( fileName)
                    # if dirName.name not in dicRPA:
                        # dicRPA[dirName.name] = []
                    # dicRPA[dirName.name].append(fileName)
                if fileArchName.endswith( '.rpyc'):
                    filesRPY += 1
                    if fileName not in dicRPA:
                        dicRPA[fileName] = []
                    dicRPA[fileName].append( fileArchName)

                elif os.path.splitext( fileArchName)[1] in extensions:
                    filesFonts += 1
                    if fileName not in dicRPA:
                        dicRPA[fileName] = []
                    dicRPA[fileName].append( fileArchName)

        if os.path.exists( pathGame + '/tl/rus/'):
            app.print( '-=> with RUS tl folder')

        if os.path.exists( pathGame + '/tl/russian/'):
            app.print( '-=> with RUSSIAN tl folder')

        if foundRPA > 0:
            app.print( f'Found {foundRPA} RPA files.')

        if filesRPY >= 1:
            app.print( f' {filesRPY} RPYC files in achives.')
        if filesFonts >= 1:
            app.print( f' {filesFonts} Fonts files in archives.')


def buttonDecompile( event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    threadRPY = threading.Thread( name='rpy', target=read_rpyc_data) #, args=( filesRPY))
    threadRPY.start()


def buttonExtract( event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    if len( dicRPA) >= 1:
        app.print( 'Start extracting rpyc and fonts files from rpa...', True)
        for fileName in dicRPA:
            extractor = UnRPA( fileName, path=pathGame)
            app.print( f'Extracting from {fileName}...')

            for files in dicRPA[fileName]:
                app.print( f'-=> {files}')

            extractor.extract_files( '.', dicRPA[fileName])


def listGamesDClick( event):
    game.listGameDCllick()
    gameScanRPA()


def clearFolder( fileExt=extTRANS, dirName=str):

    if fileExt == '*':
        shutil.rmtree( dirName)
    else:
        test = os.listdir(dirName)
        for item in test:
            if item.endswith( fileExt):
                os.remove(os.path.join(dirName, item))


def listFileStats( event, path=False, withTL=True, withStat=False):
    if not path:
        path = game.folderTL

    fileList = game.getListFilesByExt( ext='.rpy', gamePath=path, withTL=withTL, withStat=withStat)

    app.print( f'found [{len(fileList)}] filles in [{path}]. ')
    app.listFileUpdate( fileList)


def dicReplacer( fix:str) -> str:
    fixRE =  re.findall( reFix, fix)

    for item in fixRE:
        itemLow = item.lower()

        if itemLow in wordDic.keys():
            game.wordDicCount += 1

            if item == itemLow:
                itemRET = wordDic[itemLow]
            elif item == item.upper():
                itemRET = wordDic[itemLow].upper()
            elif item == item.capitalize():
                itemRET = wordDic[itemLow].capitalize()
            else:
                itemRET = wordDic[itemLow]

            fix = re.sub( r'(\b{}\b)'.format( item), itemRET, fix)

    return fix

# TODO процент с цыфрой без экрана
def findCorrect( fix):                                                 # корректировка всяких косяков первода, надо перписать...
    # %(РС - %(p_name)s

    fix = re.sub( r'(-)$', r'.', fix)                                           # -" => ."
    fix = re.sub( '^да', 'Да', fix)
    fix = re.sub( r'(\s+)([\.\!\?])', r'\2', fix)                               # убираем парные+ пробелы и пробелы перед знаком препинания

    fix = re.sub( r'К[аА][кК][иИоО]\w{1}([-\.\!\?]{1})', r'Что\1', fix)         # Какие -> Что
    fix = re.sub( r'Большой([\.\!\?]{1})', r'Отлично\1', fix)
    fix = re.sub( r'Прохладный([\.\!\?]{1})', r'Здорово\1', fix)

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
            for i in range( len( oResultSC)):

                try:
                    if tResultSC[i] != '[123]':
                        tLine = tLine.replace( tResultSC[i], oResultSC[i])              # заменяем переведенные кривые теги оригинальными по порядку
                    else:
                        tLine = tLine.replace( '[123]', '')
                except:
                    pass

    tLine = tLine.replace( '[123]', '')

    return tLine


def insertZamenaInText( textBox=False, longStr=False, retList=False):
    if textBox:
        textBox.delete( '1.0', tk.END)
    returnList = []

    sorted_income = {k: dictZamena[k] for k in sorted(dictZamena)}
    for zamane in sorted_income:
        if retList == True:
            returnList.append( dictZamena[zamane]["item"])
        else:
            if longStr == True:
                textBox.insert( tk.END, f'{dictZamena[zamane]["count"]:3}| {dictZamena[zamane]["item"]}\n')
            else:
                textBox.insert( tk.END, f'{dictZamena[zamane]["item"]}\n')

    return returnList


def findTempBrackets( event):
    app.print( 'change brackets in temp files...', True)
    dictTemp    = {}
    textLine01  = insertZamenaInText( retList=True)
    texLineEng  = app.textEng.get(1.0, tk.END)
    textLine02  = texLineEng.split('\n')

    if len( texLineEng) <= 1:
        app.print( ' -=> nothing to change, skiped...', False, True)
        return

    for i, line in enumerate(textLine02):
        if len( line) >= 1:
            try:
                if line != textLine01[i] and len(textLine01[i]) > 1:
                    dictTemp[textLine01[i]] = {}
                    dictTemp[textLine01[i]]['data'] = line
                    dictTemp[textLine01[i]]['count'] = 0
                    # print( f' -=> {line} -=> {textLine01[i]}')
            except:
                app.print( ' !!! {} -=> Skipped'.format( line))
                pass

    fileList = game.getListFilesByExt( '.rpy', game.folderTEMP)
    for fileNameTemp in fileList:
        # fileNameTemp  = fileStat['files'][tempFile]['nameTemp']

        with open( fileNameTemp, 'r', encoding='utf-8') as file :
            filedata = file.read()

        for tempLine in dictTemp:
            if tempLine != dictTemp[tempLine]['data']:
                dictTemp[tempLine]['count'] += filedata.count( tempLine)
                filedata = filedata.replace( tempLine, dictTemp[tempLine]['data'] + '[123]')

        with open( fileNameTemp, 'w', encoding='utf-8') as file:
            file.write(filedata)

    for tempLine in dictTemp:
        app.print( ' -=> {:3} {} -=> {}'.format( dictTemp[tempLine]['count'], tempLine, dictTemp[tempLine]['data']))

    # fileTRans['setting']['dictTemp'] = dictTemp


def findZamena( oLine, dictZamena):

    for reZam in reZamena:
        oResult = re.findall( reZam, oLine)

        if oResult:
            for i in range( len( oResult)):
                if oResult[i] not in dictZamena:
                    dictZamena[oResult[i]] = { 'count': 0, 'item': ''}

                dictZamena[oResult[i]]['item'] = oResult[i]              # выписываем в словарь тэги в квадратных скобках
                dictZamena[oResult[i]]['count'] = dictZamena[oResult[i]]['count'] +1


def tryToTranslate( oLine, currentFileLine, file, currentFile, totalFiles, tempFilleLines, fileTransName):

    app.progressUpdate( game)

    if testRun:
        tLine = oLine
        time.sleep( testWait)
    else:
        tLine = game.lineTransate( oLine, currentFileLine, file)

    if tLine:
        if tempFilleLines != 0:
            fileReadProc = ( currentFileLine / tempFilleLines) * 100
        else:
            fileReadProc = 0

        app.print( '-=> {:5}% {:2}/{} ({:4}) [{:.35}]'.format( round( fileReadProc, 1), currentFile, totalFiles, len( oLine), file))

        f = open( fileTransName,'a', encoding='utf-8')
        f.write( tLine)
        f.close()
    else:
        threadSTOP.do_run = False


def makeTempFiles( event):

    clearFolder( '*', game.folderTEMP)

    global dictZamena
    dictZamena = {}
    app.textTag['state'] = tk.NORMAL

    fileList = game.getListFilesByExt( '.rpy', game.folderTL)

    for fileName in fileList:

        allFile = []
        with open( fileName, encoding='utf-8') as f:
            skip01  = 0
            allFile = f.read()
            fileText= allFile.split('\n')
            tempFileName = game.folderTEMP + fileList[fileName]['fileShort']

            smartDirs( tempFileName)
            tmpFile = open( tempFileName, 'w', encoding='utf-8')

            for line in fileText:

                if line.find( r' "') >= 1 and skip01 == 0:
                    # skip01 = 0
                    skip01 = 1

                    result = re.search( reTrans[0], line)
                    if result:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                        oLine    = result.group(1)
                        oLine    = oLine.replace( '"', "'")
                        tmpFile.write( str( oLine) + '\n')
                        findZamena( oLine, dictZamena)
                else:
                    skip01 = 0

            tmpFile.close()

    insertZamenaInText( app.textTag, True)
    app.textTag['state'] = tk.DISABLED
    app.pbReset()
    listFileStats( event, path=game.folderTEMP, withTL=True, withStat=True)

def makeTransFiles( fileStat):
    clearFolder( '*', game.folderTRANS)
    app.print( 'translating start...', True)

    fileList    = game.getListFilesByExt( '.rpy', game.folderTEMP, withStat=True)
    currentSize = 0
    currentLine = 0
    currentFile = 0
    totalFiles  = len( fileList)
    game.timeSTART = datetime.today().timestamp()

    for fileName in fileList:

        lineCount       = 0
        currentFile     += 1
        tempFilleLines  = fileList[fileName]['lines']
        fileTransName   = game.folderTRANS + fileList[fileName]['fileShort']
        smartDirs( fileTransName)

        with open( fileName, encoding='utf-8') as f:

            lineTemp    = ""
            allFile     = f.read()
            fileAllText = allFile.split('\n')

            for line in fileAllText:

                if not getattr( threadSTOP, "do_run"):
                    app.print( 'translate break.', True, True)
                    return

                lineCount    += 1
                currentLine  += 1
                lineSize     = len( lineTemp)
                lineCurSize  = len( line)
                currentSize  = currentSize + lineCurSize
                # print( lineCount, currentSize, line)

                if lineSize + lineCurSize >= TRLEN:
                    tryToTranslate( lineTemp, lineCount, fileList[fileName]['fileShort'], currentFile, totalFiles, tempFilleLines, fileTransName)
                    lineTemp    = ""

                lineTemp     = lineTemp + line + '\n'

                game.currentLine = currentLine
                game.currentSize = currentSize

            if len( lineTemp) > 1:
                tryToTranslate( lineTemp, lineCount, fileList[fileName]['fileShort'], currentFile, totalFiles, tempFilleLines, fileTransName)

    threadSTOP.do_run = False
    app.btnTranslate['text']    = 'translate start'
    app.print( 'translating done!')
    if allStart:
        makeRPYFiles()
    else:
        mb.showinfo( "trans", 'make TRANS files done!')


def makeRPYFiles( event):

    global allStart
    app.print( 'start compile renpy files', True)
    clearFolder( 'rpy', game.folderRPY)

    game.wordDicCount = 0
    fileList = game.getListFilesByExt( '.rpy', game.folderTL)
    # smartDirs( fileTransName)
    for fileName in fileList:

        lineFoundCount  = 0

        fileNameTrans   = game.folderTRANS + fileList[fileName]['fileShort']  #fileStat['files'][fileName]['nameTrans'] #'temp\\{}.transl'.format( str( fileName))
        fileNameDone    = game.folderRPY   + fileList[fileName]['fileShort'] #fileStat['files'][fileName]['nameRPY'] #'transl\\{}'.format(str(fileName))
        fileNameOrig    = fileName# fileStat['files'][fileName]['path']
        allFile         = []
        smartDirs( fileNameDone)

        try:
            fileTemp    = open( fileNameTrans, encoding='utf-8').read()
            linesTemp   = fileTemp.split('\n') # readlines()

            with open( fileNameOrig, encoding='utf-8') as f:
                skip01  = 0
                allFile = f.read()
                fileAllText = allFile.split('\n')

                for lineCount, line in enumerate( fileAllText):

                    if line.find( r' "') >= 1 and skip01 == 0:
                        # skip01 = 0
                        skip01 = 1

                        result = re.search( reTrans[0], line)

                        if result:
                            oLine = result.group(1)
                            tLine = linesTemp[lineFoundCount]

                            tLine = findCorrect( tLine)
                            tLine = dicReplacer( tLine)
                            tLine = findSkobki( tLine, oLine)                                       # заменяем теги

                            if engTRANS:                                                           # если хочется иметь копию оригинальной строки внизу переведенной в игре
                                tLine = tLine + '\\n{i}{size=-10}{color=#999}' + oLine

                            rLine = str( line.replace( str( oLine), tLine))                           # формируем результирующую строку ( не помню почему так, а не собрать нормальную, видимо потому, что бывают еще старые переводы с другим форматом)
                            lineFoundCount = lineFoundCount + 1
                        else:
                            rLine = line

                        rLine = str( rLine.replace("    # ", "    "))
                        rLine = str( rLine.replace("    old ", "    new "))

                        # fileAllText[lineCount + 0] = rLine                                             # записываем ее в массив как следующую строку
                        fileAllText[lineCount + 1] = rLine                                             # записываем ее в массив как следующую строку
                    else:
                        skip01 = 0

                new_rpy_tr = open( fileNameDone, 'w', encoding='utf-8')

                for i in fileAllText:
                    new_rpy_tr.write(str(i) + '\n')

                # print( "make file [" + fileName + '] done')
                new_rpy_tr.close()

        except FileNotFoundError:
            app.print( f'Error. File [{fileNameTrans}] not found or can`t read.')
            logging.error( f'Error. File [{fileNameTrans}] not found or can`t read.' )
            # mb.showerror( 'error', f'trans file ( {fileNameTrans}) not found! make translate first.')
            # break

    app.print( f"wordDic replaced {game.wordDicCount} times.")
    # app.print( 'compile renpy files done!!!', False, True)
    copyTLStuffBack()

    if allStart:
        allStart = False
        mb.showinfo( 'all done', 'make RPY files done')


def makeALLFiles( event):
    global allStart
    allStart = True

    listFileStats()
    makeTempFiles( fileStat)
    findTempBrackets( fileStat)
    treatTranslate()


def treatTranslate( event):
    global threadSTOP

    if app.btnTranslate['text'] == 'translate start':
        app.btnTranslate['text']    = 'translate stop'

        threadSTOP = threading.Thread( name='trans', target=makeTransFiles, args=( fileStat,))
        threadSTOP.do_run = True
        threadSTOP.start()
    else:
        app.btnTranslate['text']    = 'translate start'
        # t = getThreadByName('trans') #Get thread by name
        threadSTOP.do_run = False


def tagsCopy( event):
    insertZamenaInText( app.textEng)


def tagsClear( event):
    app.textEng.delete( '1.0', tk.END)


def runExternalCmd( path):
    if path and os.path.exists( path) and path.endswith( 'exe'):
        app.print( f'running [{path}]...', True)
        # os.system( f'"{path}"')
        subprocess.call( f'"{path}"')
    else:
        app.print( f'path not found: [{path}]')


def runThreadCmd( path):
    if path and os.path.exists( path):
        # print( f'running [{path}]...', True)
        threadRun = threading.Thread( name='run', target=runExternalCmd, args=( path,))
        threadRun.do_run = True
        threadRun.start()


def btnRunGameCllick( event):
    pathGame = game.getPath()
    if not pathGame:
        return
    # arr_txt = [x for x in os.listdir() if x.endswith(".txt")]
    exeName = os.listdir( pathGame)
    exeName = sorted( list( filter(lambda fileName: fileName.endswith('.exe'), exeName)))[-1]

    if exeName and len( exeName) > 1:
        runThreadCmd( f'{pathGame}\\{exeName}')


def btnRunSDKClick( event):
    runThreadCmd( f'{game.sdkFollder}renpy.exe')


# def mainBtnClickCTR( self, btn):
#     oprint( 'fromm GUI ', self, btn)

#######################################################################################################

def main():
    global app
    global game

    app = yoFrame()
    game = gameRenpy( app)
    game.gameListScan()
    listFileStats( app, game.folderTL)

    trans = translator( app, game)

    app.listGames.bind('<Double-1>', listGamesDClick)

    app.btnGameRescan.bind( '<Button-1>', game.gameListScan)
    app.btnExtract.bind('<Button-1>', buttonExtract)
    app.btnDecompile.bind('<Button-1>', buttonDecompile)
    app.btnRunRenpy.bind('<Button-1>', btnRunSDKClick)
    app.btnFontsCopy.bind('<Button-1>', scanInputFolder)
    app.btnMenuFinder.bind('<Button-1>', findMenuStart)
    app.btnCopyTL.bind('<Button-1>', copyTLStuff)

    app.btnTLScan.bind('<Button-1>', listFileStats)
    app.btnMakeTemp.bind('<Button-1>', makeTempFiles)
    app.btnTranslate.bind('<Button-1>', treatTranslate)
    app.btnMakeRPY.bind('<Button-1>', makeRPYFiles)
    # app.btnALL.bind('<Button-1>', makeALLFiles)
    app.btnRunGame.bind('<Button-1>', btnRunGameCllick)

    app.btnTagCopy.bind('<Button-1>', tagsCopy)
    app.btnTagClear.bind('<Button-1>', tagsClear)
    app.btnTempRepl.bind('<Button-1>', findTempBrackets)

    app.after(1000, app.updateUI)
    app.mainloop()


if __name__ == "__main__":
    main()




# root= tk.Tk()
# root.minsize( 1300, 400)
# root.geometry("1500x600")

# root.columnconfigure(0, weight=0, minsize=50)
# root.columnconfigure(1, weight=0, minsize=50)
# root.columnconfigure(2, weight=0, minsize=50)
# root.columnconfigure(3, weight=1, minsize=50)
# root.rowconfigure(   0, weight=2, pad=5)
# root.rowconfigure(   1, weight=0, pad=5)

# #######################################################################################################
# groupGames       = tk.LabelFrame(root, padx=3, pady=3, text="Game select")
# groupGames.grid(row=0, column=0, padx=3, pady=3, sticky='NWES')
# groupGames.columnconfigure(0, weight=2, minsize=25)
# groupGames.rowconfigure( 0, weight=0, pad=0)
# groupGames.rowconfigure( 1, weight=2, pad=0)
# groupGames.rowconfigure( 2, weight=0, pad=0)
# groupGames.rowconfigure( 3, weight=0, pad=0)
# groupGames.rowconfigure( 4, weight=0, pad=0)
# groupGames.rowconfigure( 5, weight=0, pad=0)
# groupGames.rowconfigure( 6, weight=0, pad=0)
# groupGames.rowconfigure( 7, weight=0, pad=0)
# groupGames.rowconfigure( 8, weight=0, pad=0)
# groupGames.rowconfigure( 9, weight=0, pad=0)

# lbGameSelected  = tk.Label(groupGames, text="None", font=10)
# listGames       = tk.Listbox( groupGames, selectmode=tk.NORMAL, height=4, width=40, font=("Consolas", 8))
# listGames.bind('<Double-1>', listGamesDClick)
# btnGameRescan   = ttk.Button( groupGames, text="rescan game list",      width=15, command= gamesScan)
# btnExtract      = ttk.Button( groupGames, text="extract rpyc/fonts",    width=15, command= buttonExtract)
# btnDecompile    = ttk.Button( groupGames, text="decompile rpyc->rpy",   width=15, command= buttonDecompile)
# btnRunRenpy     = ttk.Button( groupGames, text="run SDK to translate",  width=15, command= btnRunSDKClick)
# btnFontsCopy    = ttk.Button( groupGames, text="non rus fonts + myStuff", width=15, command= scanInputFolder)
# btnMenuFinder   = ttk.Button( groupGames, text="make menu finder",      width=15, command= findMenuStart)
# btnCopyTL       = ttk.Button( groupGames, text="copy TL files to translate",width=15, command= copyTLStuff)
# btnRunGame      = ttk.Button( groupGames, text="run selected game ",    width=15, command= btnRunGameCllick)

# lbGameSelected.grid(row=0, column=0, sticky="N", padx=3, pady=3)
# listGames.grid(     row=1, column=0, sticky="NWES", padx=3, pady=3, columnspan=1)

# btnGameRescan.grid( row=2, column=0, sticky='NWES')
# btnExtract.grid(    row=3, column=0, sticky='NWES')
# btnDecompile.grid(  row=4, column=0, sticky='NWES')
# btnFontsCopy.grid(  row=5, column=0, sticky='NWES')
# btnMenuFinder.grid( row=6, column=0, sticky='NWES')
# btnRunRenpy.grid(   row=7, column=0, sticky='NWES')
# btnCopyTL.grid(     row=8, column=0, sticky='NWES')
# btnRunGame.grid(    row=9, column=0, sticky='NWES')

# #######################################################################################################
# groupFiles       = tk.LabelFrame(root, padx=3, pady=3, text="File List")
# groupFiles.grid(row=0, column=1, padx=3, pady=3, sticky='NWES')
# groupFiles.columnconfigure(0, weight=2, minsize=25)
# groupFiles.rowconfigure( 0, weight=2, pad=0)
# groupFiles.rowconfigure( 1, weight=0, pad=0)
# groupFiles.rowconfigure( 2, weight=0, pad=0)

# listFile        = tk.Listbox( groupFiles, selectmode=tk.NORMAL, height=4, width=53, font=("Consolas", 8))
# btnTLScan       = ttk.Button( groupFiles, text="rescan tl folder",   width=15, command= lambda: rescanFolders())
# btnMakeTemp     = ttk.Button( groupFiles, text="make temp files",    width=15, command= lambda: makeTempFiles( fileStat))

# listFile.grid(      row=0, column=0, sticky="NWES", padx=5, pady=5)
# btnTLScan.grid(     row=1, column=0, sticky='NWES')
# btnMakeTemp.grid(   row=2, column=0, sticky='NWES')

# #######################################################################################################
# groupTags          = tk.LabelFrame(root, padx=3, pady=3, text="Tags list")
# groupTags.grid( row=0, column=2, padx=3, pady=3, sticky='NWES')

# groupTags.columnconfigure(0, weight=2, minsize=30)
# groupTags.columnconfigure(1, weight=2, minsize=30)
# # groupTags.columnconfigure(2, weight=2, minsize=25)

# groupTags.rowconfigure(   0, weight=2, pad=0)
# groupTags.rowconfigure(   1, weight=0, pad=0)

# textTag         = tk.Text( groupTags, font=("Consolas", 8), width=31)#, state=tk.DISABLED)
# textEng         = tk.Text( groupTags, font=("Consolas", 8), width=31)

# btnTagCopy      = ttk.Button( groupTags, text=">>>>",       width=20, command= tagsCopy)
# btnTagClear     = ttk.Button( groupTags, text="xxxx",       width=20, command= tagsClear)
# btnTempRepl     = ttk.Button( groupTags, text="tags replace", width=20, command= lambda: findTempBrackets( fileStat))

# textTag.grid( row=0, column=0, sticky='NWES', padx=5)
# textEng.grid( row=0, column=1, sticky='NWES', padx=5, columnspan=2)

# btnTagCopy.grid(  row=1, column=0, sticky='NW', padx=0, columnspan=2)
# btnTagClear.grid( row=1, column=0, sticky='N', padx=0, columnspan=2)
# btnTempRepl.grid( row=1, column=0, sticky='NE', columnspan=2)
# #######################################################################################################

# groupComm       = tk.LabelFrame(root, padx=3, pady=3, text="Common")
# groupComm.grid(row=0, column=3, padx=3, pady=3, sticky='NWES')
# groupComm.columnconfigure(0, weight=0, minsize=5)
# groupComm.columnconfigure(1, weight=1, minsize=25)
# groupComm.columnconfigure(2, weight=0, minsize=5)
# groupComm.columnconfigure(3, weight=1, minsize=5)
# groupComm.rowconfigure(   3, weight=2, pad=0)
# groupComm.rowconfigure(   4, weight=0, pad=0)

# tk.Label(groupComm, text="Закончим:").grid(row=0, sticky=tk.E)
# tk.Label(groupComm, text="Через:"   ).grid(row=1, sticky=tk.E)
# tk.Label(groupComm, text="Строка:"  ).grid(row=0, sticky=tk.E, column=2)
# tk.Label(groupComm, text="Размер:"  ).grid(row=1, sticky=tk.E, column=2)

# stPBar          = ttk.Style( groupComm)
# stPBar.layout(   "lbPBar", [('lbPBar.trough', {'children': [('lbPBar.pbar', {'side': 'left', 'sticky': 'ns'}), ("lbPBar.label",   {"sticky": ""})], 'sticky': 'nswe'})])
# stPBar.configure("lbPBar", text="0 %      ")

# pbTotal         = ttk.Progressbar( groupComm, mode="determinate", length = 200, style='lbPBar')
# textLogs        = tk.Text( groupComm, height=4, width=53, font=("Consolas", 8))

# lbStart         = tk.Label(groupComm, text="")
# lbEnd           = tk.Label(groupComm, text="")
# lbLine          = tk.Label(groupComm, text="")
# lbLines         = tk.Label(groupComm, text="")

# lbStart.grid(   row=0, sticky=tk.W, column=1)
# lbEnd.grid(     row=1, sticky=tk.W, column=1)
# lbLine.grid(    row=0, sticky=tk.W, column=3)
# lbLines.grid(   row=1, sticky=tk.W, column=3)

# pbTotal.grid(   row=2, column=0, columnspan=4, sticky="NSEW")
# textLogs.grid(  row=3, column=0, columnspan=4, sticky="NWES", padx=5, pady=5)

# btnPanel = tk.Frame(groupComm, background="#99fb99")
# btnPanel.grid( row=4, column=0, columnspan=4, sticky='NWES')
# btnPanel.columnconfigure(0, weight=1, minsize=20)
# btnPanel.columnconfigure(1, weight=1, minsize=20)
# btnPanel.columnconfigure(2, weight=1, minsize=20)

# btnTranslate    = ttk.Button( btnPanel, text="translate start",    width=25, command= lambda: treatTranslate())
# btnMakeRPY      = ttk.Button( btnPanel, text="make Renpy files",   width=25, command= lambda: makeRPYFiles())
# btnALL          = ttk.Button( btnPanel, text="just Translate",     width=25, command= makeALLFiles)

# btnTranslate.grid(row=0, column=0, sticky='NWES')
# btnMakeRPY.grid(  row=0, column=1, sticky='NWES')
# btnALL.grid(      row=0, column=2, sticky='NWES')

# #######################################################################################################
# button1_ttp = CreateToolTip(btnTLScan,      'Делается автоматически при старте программы.\n Можно тыкать, если поменялись файлы в папке tl или просто скучно...')
# button2_ttp = CreateToolTip(btnMakeTemp,    'Делаем временные (temp) файлы в одноименной папке.\n Можно тыкать, если поменялись файлы в папке tl или накосячили с тэгами.'\
#                                                 ' Временные файлы создаются заново, считываясь из файлов в папке tl, ничего страшного.')
# button3_ttp = CreateToolTip(btnTempRepl,    'Замена тэгов во временных (temp) файлах на разумный текст.\n' \
#                                                 'Заменяем теги в квадратных скобках на свой вариант на английском (!!!) языке, для более качественного перевода, '\
#                                                 'например "[sister]" -=> "sister" ( что на что менять ищем в коде игры или вангуем).' \
#                                                 'Если пошло что-то не так то обновляем временные файлы предыдущей кнопкой, меняем тэги и тыкаем заново.\n' \
#                                                 'Если не меняли, то нажимать это и не надо...\n\n' \
#                                                 '!u - tag uppercase ("[mom!u]" = "MOM"),\n' \
#                                                 '!l - tag lowercase ("[MOM!l]" = "mom"),\n' \
#                                                 '!c - only first character ("[mom!c]" = "Mom")')
# button4_ttp = CreateToolTip(btnTranslate,   'Перевод временных файлов (temp) на русский язык (transl).')
# button5_ttp = CreateToolTip(btnMakeRPY,     'Сборка переведенных файлов (transl) в Ренпайские файлы (rpy) в папке transl.')
# button6_ttp = CreateToolTip(btnALL,         'Одна кнопка для всего. Нажимаем - получаем. Все просто и без затей.')

# sizeGrip    = ttk.Sizegrip(groupBot)
# sizeGrip.grid( row=0, column=6, sticky=tk.SE)


# root.after(1000, update)
# root.mainloop()


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

# reTrans     = re.compile(r'"(.*\w+.*)"( nointeract)?$'), 0, 0

        # try:
        #     tLine = GoogleTranslator( source='auto', target='ru').translate( oLine)

        # except RequestError as e:
        #     app.print( f'-=> ERROR: {e} -=> line: {currentFileLine} ( {len( oLine)}b) at [{file}]')
        #     logging.error( f'ERROR -=> line: {currentFileLine} ( {len(oLine)}b) at [{file}] ({e})' )
        #     threadSTOP.do_run = False
        #     tLine = oLine

        # except Exception as error:
        #     app.print( f'ERROR -=> line: {currentFileLine} ( {len(oLine)}b) at [{file}] ({error})' )
        #     logging.error( f'ERROR -=> line: {currentFileLine} ( {len(oLine)}b) at [{file}] ({error})' )
        #     # print( oLine)
        #     tLine = oLine


    # global fileStat
    # fileStat  = {}
    # dicTemp  = {}
    # filesCur = 0
    # fileList = game.listTLFiles()

    # for filePath in fileList:                           # Находим файлы для перевода в дирректории

    #     fileName = os.path.basename( filePath)
    #     fileSize = os.path.getsize(  filePath)
    #     fileBase, fileExt  = os.path.splitext( fileName)
    #     filesMax = len( fileList)
    #     filesCur += 1

    #     with open( filePath, encoding='utf-8') as infile:
    #         allFile = infile.read()
    #         current_file_text = allFile.split('\n')
    #         # words = 0
    #         # characters = 0
    #         lines = 0
    #         linesLen = 0

    #         for line in current_file_text:
    #             lines += 1
    #             linesLen += len( line)
    #             # wordslist = line.split()
    #             # words += len(wordslist)
    #             # characters += sum(len(word) for word in wordslist)

    #     i = 0
    #     while fileName in dicTemp:                  # приписывает число к имени, если есть такой файл
    #         i += 1
    #         fileName = '{} ({:02}){}'.format( fileBase, i, fileExt)

    #     dicTemp[fileName] = {}

    #     fs = dicTemp[fileName]

    #     fs['name'] = fileBase + fileExt
    #     fs['size'] = fileSize
    #     fs["path"] = filePath
    #     fs['lines'] = lines
    #     fs["chars"] = linesLen
    #     fs['tempFLine'] = 0
    #     fs['tempFSize'] = 0
    #     fs['filesMax']  = filesMax
    #     fs['nameTemp']  = f'{game.folderTEMP}/{fileName}.{extTEMP}'
    #     fs['nameTrans'] = f'{game.folderTEMP}/{fileName}.{extTRANS}'
    #     fs['nameRPY']   = f'{game.folderRPY}/{fileName}'

    # fileStat   = { 'files': {}, 'setting': {}}
    # listSorted = { key: dicTemp[key] for key in sorted( dicTemp)}

    # for filesCur, key in enumerate( listSorted):
    #     fileStat['files'][key] = dicTemp[key]
    #     fileStat['files'][key]['filesCur']  = filesCur + 1

    # fileStat['setting']['currentLine']  = 0
    # fileStat['setting']['currentSize']  = 0
    # fileStat['setting']['totalSize']    = 0
    # fileStat['setting']['totalLine']    = 0
    # fileStat['setting']['replCount']    = 0


# def fileStatsUpdate():

#     totalLine = 0
#     totalSize = 0

#     for fileName in fileStat['files']:

#         with open( fileStat['files'][fileName]['nameTemp'], 'r', encoding='utf-8') as file :
#             allFile = file.read()
#             current_file_text = allFile.split('\n')
#             lines = 0
#             linesLen = 0

#             for line in current_file_text:
#                 lines += 1
#                 linesLen += len( line)

#             totalLine = totalLine + lines
#             totalSize = totalSize + linesLen

#             fileStat['files'][fileName]['tempFSize'] = linesLen
#             fileStat['files'][fileName]['tempFLine'] = lines - 1

#     fileStat['setting']['totalLine'] = totalLine
#     fileStat['setting']['totalSize'] = totalSize