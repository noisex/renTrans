import os
import re
import time
import threading
import logging


import tkinter as tk
import tkinter.ttk as ttk

from datetime import datetime
from tkinter import messagebox as mb
# from tkinter.ttk import Progressbar, Style, Button

from toolTip import CreateToolTip
from deep_translator import GoogleTranslator
from deep_translator.exceptions import RequestError
########################################################################################################################

fileTRans   = []
fileStat    = {}
threadSTOP  = False
allStart    = False
TRLEN       = 4100 # 4700 for GoogleTranslate

folderTL    = './tl'
folderTEMP  = './temp'
folderRPY   = './transl'
extTEMP     = 'tmp'
extTRANS    = 'transl'

testRun     = False
engTRANS    = False
testWait    = 0.3

oprint = print

reFind      = '(\\[.+?\\])'
reProc      = '(\\%\\(.+?\\)s)'
# reTrans     = re.compile(r'"(.*[\w].*)"(  )?$'), 0, 0
reTrans     = re.compile(r'"(.*[\w].*)"'), 0, 0

# src_str  = re.compile("this", re.IGNORECASE)
# str_replaced  = src_str.sub("that", "This is a test sentence. this is a test sentence. THIS is a test sentence.")
# print(re.escape('https://www.python.org'))
# https://www\.python\.org

# redata = re.compile(re.escape('php'), re.IGNORECASE)
# new_text = redata.sub('php', 'PHP Exercises')

# reTrans     = re.compile(r'"(.*\w+.*)"( nointeract)?$'), 0, 0
reBrackets  = [
    '(\\[.+?\\])',          # квадратные скобки  - []
    '({.+?})',              # фигурные скобки    - {}
    '(\\%\\(.+?\\))'        # процент со скобкой - %()
]

logging.basicConfig(filename='example.log', format='%(asctime)s %(message)s', datefmt='%Y.%d.%m %H:%M:%S', encoding='utf-8', level=logging.ERROR)

fileSkip    = [ 'gui.rpy', "common.rpy", "options.rpy", "screens.rpy", 'xxx_transparent.rpy', 'xxx_toggle_menu.rpy' ]
# fileSkip    = []


def print( line, newLine=False, lastLine=False):
    if newLine:
        textLogs.insert( tk.END, '[{}]\n'.format( time.strftime('%H:%M:%S')))

    textLogs.insert( tk.END, '[{}] {}\n'.format( time.strftime('%H:%M:%S'), str( line)))

    if lastLine:
        textLogs.insert( tk.END, '[{}]\n'.format( time.strftime('%H:%M:%S')))

    textLogs.see( tk.END)


def update():
    root.update()
    root.after(1000, update)


def makeNewDirs():
    if not os.path.exists( folderRPY):                                   # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderRPY)
        print( f'Папка {folderRPY} - из нее забираем перевод')

    if not os.path.exists( folderTL):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderTL)
        print( f'Папка {folderTL} - в нее кладем файлы для перевода')

    if not os.path.exists( folderTEMP):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderTEMP)
        print( f'Папка {folderTEMP} - она просто нужна...')


def clearFolder( fileExt=extTRANS, dirName=folderTEMP):
    test = os.listdir(dirName)

    for item in test:
        if item.endswith( fileExt):
            os.remove(os.path.join(dirName, item))


def rescanFolders():
    makeNewDirs()
    print( f'[scan {folderTL} folder]')
    global fileTRans
    global fileStat
    fileTRans = listTransFiles()
    fileStat  = listFileStats( fileTRans)
    return fileTRans, fileStat


def listFileUpdate( fileStat):
    i = 0
    listFile.delete(0, tk.END)
    listFile.insert( tk.END,  "{:^34}|{:^10}|{:^7}".format( 'File', 'Size', 'Lines'))

    for fileName in fileStat['files']:
        i += 1
        fs = fileStat['files'][fileName]
        listFile.insert( tk.END,  "{:3}|{:<30.30}|{:>10,}|{:>7}".format( i, fileName, fs['tempFSize'], fs['tempFLine']))

    totalLine    = fileStat['setting']['totalLine']
    totalSize    = fileStat['setting']['totalSize']
    currentLine  = fileStat['setting']['currentLine']
    currentSize  = fileStat['setting']['currentSize']

    fileStat['setting']['dictTemp'] = {}

    lbLine['text']  = '{:,} из {:,}'.format( currentLine, totalLine)
    lbLines['text'] = '{:,} из {:,}'.format( currentSize, totalSize)
    print( f'-=> {i} files found')


def listTransFiles():
    filesAll = []
    for top, dirs, files in os.walk( f'./{folderTL}/'):                           # Находим файлы для перевода в дирректории
        for nm in files:
            if nm not in fileSkip:
                filesAll.append(os.path.join(top, nm))

    print( '[make listFiles]')
    return sorted( list(filter(lambda x: x.endswith('.rpy'), filesAll)))


def listFileStats( fileList):
    dicTemp  = {}
    filesCur = 0

    for filePath in fileList:                           # Находим файлы для перевода в дирректории

        fileName = os.path.basename( filePath)
        fileSize = os.path.getsize(  filePath)
        fileBase, fileExt  = os.path.splitext( fileName)
        filesMax = len( fileList)
        filesCur += 1

        # allFile = []
        with open( filePath, encoding='utf-8') as infile:
            allFile = infile.read()
            current_file_text = allFile.split('\n')
            # words = 0
            # characters = 0
            lines = 0
            linesLen = 0

            for line in current_file_text:
                lines += 1
                linesLen += len( line)
                # wordslist = line.split()
                # words += len(wordslist)
                # characters += sum(len(word) for word in wordslist)

        i = 0
        while fileName in dicTemp:                  # приписывает число к имени, если есть такой файл
            i += 1
            fileName = '{} ({:02}){}'.format( fileBase, i, fileExt)

        dicTemp[fileName] = {}

        fs = dicTemp[fileName]

        fs['name'] = fileBase + fileExt
        fs['size'] = fileSize
        fs["path"] = filePath
        fs['lines'] = lines
        fs["chars"] = linesLen
        fs['tempFLine'] = 0
        fs['tempFSize'] = 0
        fs['filesMax']  = filesMax
        # fs['filesCur']  = filesCur
        fs['nameTemp']  = f'{folderTEMP}/{fileName}.{extTEMP}'
        fs['nameTrans'] = f'{folderTEMP}/{fileName}.{extTRANS}'
        fs['nameRPY']   = f'{folderRPY}/{fileName}'

    fileStat   = { 'files': {}, 'setting': {}}
    listSorted = { key: dicTemp[key] for key in sorted( dicTemp)}

    for filesCur, key in enumerate( listSorted):
        fileStat['files'][key] = dicTemp[key]
        fileStat['files'][key]['filesCur']  = filesCur + 1

    fileStat['setting']['currentLine']  = 0
    fileStat['setting']['currentSize']  = 0
    fileStat['setting']['totalSize']    = 0
    fileStat['setting']['totalLine']    = 0
    fileStat['setting']['replCount']    = 0

    listFileUpdate( fileStat)
    # print( fileStat)
    return fileStat


def fileStatsUpdate( fileTRans):

    totalLine = 0
    totalSize = 0

    for fileName in fileStat['files']:

        with open( fileStat['files'][fileName]['nameTemp'], 'r', encoding='utf-8') as file :
            allFile = file.read()
            current_file_text = allFile.split('\n')
            lines = 0
            linesLen = 0

            for line in current_file_text:
                lines += 1
                linesLen += len( line)

            totalLine = totalLine + lines
            totalSize = totalSize + linesLen

            fileStat['files'][fileName]['tempFSize'] = linesLen
            fileStat['files'][fileName]['tempFLine'] = lines - 1

    fileStat['setting']['totalLine'] = totalLine
    fileStat['setting']['totalSize'] = totalSize



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

    fix = fix.replace( '"', '\'')

    fix = fix.replace( '\\ n', '\\n')
    fix = fix.replace( '\\ N', '\\n')

    fix = fix.replace( '% (', ' %(')
    fix = fix.replace( ') s', ')s')
    fix = fix.replace( '{я', '{i}')
    fix = fix.replace( '} ', '}')

    # if fix.find( 'Какие') >= 0:
    #     print( str( fix))

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

    return tLine


def findTempBrackets( fileTRans):
    print( '[change brackets]')
    dictTemp    = {}
    textLine01  = textTag.get(1.0, tk.END).split('\n')
    texLineEng  = textEng.get(1.0, tk.END)
    textLine02  = texLineEng.split('\n')

    if len( texLineEng) <= 1:
        print( ' -=> nothing to change, skiped...', False, True)
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
                print( ' !!! {} -=> Skipped'.format( line))
                pass

    for tempFile in fileStat['files']:
        fileNameTemp  = fileStat['files'][tempFile]['nameTemp']

        with open( fileNameTemp, 'r', encoding='utf-8') as file :
            filedata = file.read()

        for tempLine in dictTemp:
            if tempLine != dictTemp[tempLine]['data']:
                dictTemp[tempLine]['count'] += filedata.count( tempLine)
                filedata = filedata.replace( tempLine, dictTemp[tempLine]['data'] + '[123]')

        with open( fileNameTemp, 'w', encoding='utf-8') as file:
            file.write(filedata)

    for tempLine in dictTemp:
        print( ' -=> {:3} {} -=> {}'.format( dictTemp[tempLine]['count'], tempLine, dictTemp[tempLine]['data']))

    # fileTRans['setting']['dictTemp'] = dictTemp
    print( '')


def findZamena( oLine, dictZamena, dictZamenaPR):

    oResultSC = re.findall( reFind, oLine)
    oResultPR = re.findall( reProc, oLine)

    if oResultSC:
        for i in range( len( oResultSC)):
            dictZamena[oResultSC[i]] = oResultSC[i]              # выписываем в словарь тэги в квадратных скобках

    if oResultPR:
        for i in range( len( oResultPR)):
            dictZamenaPR[oResultPR[i]] = oResultPR[i]              # выписываем в словарь тэги в квадратных скобках


def tryToTranslate( oLine, currentFileLine, file):

    fileName     = fileStat['files'][file]['nameTrans'] #'temp\\{}.transl'.format( str( file))
    fileTempSize = fileStat['files'][file]['tempFLine']
    filesMax     = fileStat['files'][file]['filesMax']
    filesCur     = fileStat['files'][file]['filesCur']

    totalLine    = fileStat['setting']['totalLine']
    totalSize    = fileStat['setting']['totalSize']
    currentLine  = fileStat['setting']['currentLine']
    currentSize  = fileStat['setting']['currentSize']

    timeSTART    = fileStat['setting']['timeSTART']
    timeNOW      = datetime.today().timestamp()

    timeDelta    = timeNOW - timeSTART
    timeFinish   = ( totalLine * timeDelta) / currentLine
    timeEND      = timeSTART + timeFinish
    timeLaps     = timeFinish - timeDelta

    lbStart["text"] = datetime.fromtimestamp( timeEND).strftime( "%H:%M:%S")
    lbEnd["text"]   = datetime.utcfromtimestamp( timeLaps).strftime("%Hч %Mм %Sсек")

    lbLine['text']  = '{:,} из {:,}'.format( currentLine, totalLine)
    lbLines['text'] = '{:,} из {:,}'.format( currentSize, totalSize)
    percent         = str( round((( currentLine / totalLine) * 100), 2))
    pbTotal['value']= percent
    root.title( percent + '%')

    stPBar.configure("lbPBar", text= percent + "%      ")

    # tLine       = MyMemoryTranslator( source='en', target='ru').translate( oLine)
    if testRun:
        tLine = oLine
        time.sleep( testWait)
    else:
        try:
            tLine = GoogleTranslator( source='en', target='ru').translate( oLine)

        except RequestError as e:
            print( f'-=> ERROR: {e} -=> line: {currentFileLine} ( {len( oLine)}b) at [{file}]')
            logging.error( f'ERROR -=> line: {currentFileLine} ( {len(oLine)}b) at [{file}] ({e})' )

        except Exception as error:
            print( f'ERROR -=> line: {currentFileLine} ( {len(oLine)}b) at [{file}] ({error})' )
            logging.error( f'ERROR -=> line: {currentFileLine} ( {len(oLine)}b) at [{file}] ({error})' )
            # print( oLine)
            tLine = oLine

    if tLine:
        if fileTempSize != 0:
            fileReadProc = ( currentFileLine / fileTempSize) * 100
        else:
            fileReadProc = 0

        print( '-=> {:5}% {:2}/{} [{:.35}]'.format( round( fileReadProc, 1), filesCur, filesMax, file))

        f = open( fileName,'a', encoding='utf-8')
        f.write( tLine + '\n')
        f.close()


def makeTempFiles( fileStat):

    clearFolder( extTEMP)
    print( "[make temp files]")

    dictZamena = {}
    dictZamenaPR = {}
    totalSize  = 0
    totalLine  = 0
    textTag['state'] = tk.NORMAL
    textTag.delete( '1.0', tk.END)
    # textEng.delete( '1.0', tk.END)

    for fileName in fileStat['files']:

        allFile = []
        with open( fileStat['files'][fileName]['path'], encoding='utf-8') as f:
            skip01  = 0
            fileSize= 0
            lines   = 0
            allFile = f.read()
            fileText= allFile.split('\n')
            tmpFile = open( fileStat['files'][fileName]['nameTemp'], 'w', encoding='utf-8')

            for line in fileText:

                if line.find( r' "') >= 1 and skip01 == 0:
                    skip01 = 1

                    result = re.search( reTrans[0], line)
                    if result:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                        lines    += 1
                        oLine    = result.group(1)
                        fileSize = fileSize + len( oLine)

                        tmpFile.write( str( oLine) + '\n')

                        findZamena( oLine, dictZamena, dictZamenaPR)
                else:
                    skip01 = 0

            fileStat['files'][fileName]['tempFSize'] = fileSize
            fileStat['files'][fileName]['tempFLine'] = lines
            tmpFile.close()

            totalLine = totalLine + lines + 1
            totalSize = totalSize + fileSize

        fileStat['setting']['totalSize'] = totalSize
        fileStat['setting']['totalLine'] = totalLine
        sorted_income = {k: dictZamena[k] for k in sorted(dictZamena)}

    for zamane in sorted_income:
        # if len( zamane) > 1:
        textTag.insert( tk.END, zamane + '\n')

    for zamane in dictZamenaPR:
        # if len( zamane) > 1:
        textTag.insert( tk.END, zamane + '\n')

    textTag['state'] = tk.DISABLED
    listFileUpdate(fileStat)
    # print( "[temp files done]", True)


def makeTransFiles( fileStat):
    global allStart
    clearFolder( extTRANS)
    print( '[translating start]')
    currentSize = 0
    currentLine = 0
    fileStat['setting']['timeSTART'] = datetime.today().timestamp()

    if 'totalLine' not in fileStat['setting']:
        fileStatsUpdate( fileTRans)

    for fileName in fileStat['files']:

        lineCount       = -1
        with open( fileStat['files'][fileName]['nameTemp'], encoding='utf-8') as f:

            lineTemp    = ""
            allFile     = f.read()
            fileAllText = allFile.split('\n')

            for line in fileAllText:

                if not getattr( threadSTOP, "do_run"):
                    print( 'translate break.', True, True)
                    return

                lineCount    += 1
                currentLine  += 1
                lineTemp     = lineTemp + line + '\n'
                lineSize     = len( lineTemp)
                currentSize  = currentSize + len( line)
                fileStat['setting']['currentLine'] = currentLine
                fileStat['setting']['currentSize'] = currentSize

                if lineSize >= TRLEN:
                    tryToTranslate( lineTemp, lineCount, fileName)
                    lineTemp    = ""

            if len( lineTemp) > 1:
                tryToTranslate( lineTemp, lineCount, fileName)

    threadSTOP.do_run = False
    btnTranslate['text']    = '3 translate start'
    print( '[translating done!]', False, True)
    if allStart:
        makeRPYFiles()
    else:
        mb.showinfo( "trans", 'make TRANS files done!')


def makeRPYFiles():

    global allStart
    print( '[start compile renpy files]', True)
    clearFolder( 'rpy', folderRPY)

    for fileName in fileStat['files']:

        lineFoundCount  = 0
        fileNameTrans   = fileStat['files'][fileName]['nameTrans'] #'temp\\{}.transl'.format( str( fileName))
        fileNameDone    = fileStat['files'][fileName]['nameRPY'] #'transl\\{}'.format(str(fileName))
        fileNameOrig    = fileStat['files'][fileName]['path']
        allFile         = []

        try:
            fileTemp    = open( fileNameTrans, encoding='utf-8').read()
            linesTemp   = fileTemp.split('\n') # readlines()

            with open( fileNameOrig, encoding='utf-8') as f:
                skip01  = 0
                allFile = f.read()
                fileAllText = allFile.split('\n')

                for lineCount, line in enumerate( fileAllText):

                    if line.find( r' "') >= 1 and skip01 == 0:
                        skip01 = 1

                        result = re.search( reTrans[0], line)

                        if result:
                            oLine = result.group(1)
                            tLine = linesTemp[lineFoundCount]

                            tLine = findCorrect( tLine)
                            tLine = findSkobki( tLine, oLine)                                       # заменяем теги

                            if engTRANS:                                                           # если хочется иметь копию оригинальной строки внизу переведенной в игре
                                tLine = tLine + '\\n{i}{size=-10}{color=#999}' + oLine

                            rLine = str( line.replace( str( oLine), tLine))                           # формируем результирующую строку ( не помню почему так, а не собрать нормальную, видимо потому, что бывают еще старые переводы с другим форматом)
                            lineFoundCount = lineFoundCount + 1
                        else:
                            rLine = line

                        rLine = str( rLine.replace("    # ", "    "))
                        rLine = str( rLine.replace("    old ", "    new "))

                        fileAllText[lineCount + 1] = rLine                                             # записываем ее в массив как следующую строку
                    else:
                        skip01 = 0

                new_rpy_tr = open( fileNameDone, 'w', encoding='utf-8')

                for i in fileAllText:
                    new_rpy_tr.write(str(i) + '\n')

                # print( "make file [" + fileName + '] done')
                new_rpy_tr.close()

        except FileNotFoundError:
            print( f'Error. File [{fileNameTrans}] not found or can`t read.')
            logging.error( f'Error. File [{fileNameTrans}] not found or can`t read.' )
            # mb.showerror( 'error', f'trans file ( {fileNameTrans}) not found! make translate first.')
            # break


    print( 'можно копировать все это ( папка /transl/) обратно в игру ( папка /game/tl/rus/)')
    print( '[compile renpy files done!!!]', False, True)

    if allStart:
        allStart = False
        mb.showinfo( 'all done', 'make RPY files done')


def makeALLFiles():
    global allStart
    allStart = True

    rescanFolders()
    makeTempFiles( fileStat)
    findTempBrackets( fileStat)
    treatTranslate()


def treatTranslate():
    global threadSTOP

    if btnTranslate['text'] == '3 translate start':
        btnTranslate['text']    = '3 translate stop'

        threadSTOP = threading.Thread( name='trans', target=makeTransFiles, args=( fileStat,))
        threadSTOP.do_run = True
        threadSTOP.start()
    else:
        btnTranslate['text']    = '3 translate start'
        # t = getThreadByName('trans') #Get thread by name
        threadSTOP.do_run = False


def tagsCopy():
    textEng.delete( '1.0', tk.END)

    text01     = textTag.get(1.0, tk.END)
    textLine01 = text01.split('\n')

    for line in textLine01:
        textEng.insert( tk.END, line + '\n')


def tagsClear():
    textEng.delete( '1.0', tk.END)

#######################################################################################################

root= tk.Tk()
root.minsize( 1100, 300)
root.geometry("1100x450")

root.columnconfigure(0, weight=0, minsize=50)
root.columnconfigure(1, weight=0, minsize=50)
root.columnconfigure(2, weight=1, minsize=50)
root.rowconfigure(   0, weight=2, pad=5)
root.rowconfigure(   1, weight=0, pad=5)

#######################################################################################################
listFile        = tk.Listbox( root, selectmode=tk.NORMAL, height=4, width=53, font=("Consolas", 8))
listFile.grid( row=0, column=0, sticky="NWES", padx=5, pady=5)

group0          = tk.LabelFrame(root, padx=5, pady=10, text="        [game_tag]        -=>      'eng text'   ")
group0.grid( row=0, column=1, padx=5, pady=0, sticky='NWES')
group0.columnconfigure(0, weight=2, minsize=25)
group0.columnconfigure(1, weight=2, minsize=25)
group0.rowconfigure(   0, weight=2, pad=0)

textTag         = tk.Text( group0, font=("Consolas", 8), width=25)#, state=tk.DISABLED)
textEng         = tk.Text( group0, font=("Consolas", 8), width=25)

btnTagCopy      = ttk.Button( group0, text=">>>>",       width=25, command= tagsCopy)
btnTagClear     = ttk.Button( group0, text="xxxx",       width=25, command= tagsClear)

textTag.grid( row=0, column=0, sticky='NWES', padx=5)
textEng.grid( row=0, column=1, sticky='NWES', padx=5)

btnTagCopy.grid(  row=1, column=0, sticky='WES', padx=0)
btnTagClear.grid( row=1, column=1, sticky='WES', padx=0)

#######################################################################################################
group2          = tk.LabelFrame(root, padx=3, pady=3, text="Common")
group2.grid(row=0, column=2, padx=0, pady=0, sticky='NWES')
group2.columnconfigure(0, weight=0, minsize=5)
group2.columnconfigure(1, weight=1, minsize=25)
group2.columnconfigure(2, weight=0, minsize=5)
group2.columnconfigure(3, weight=1, minsize=5)
group2.rowconfigure(   3, weight=2, pad=0)

tk.Label(group2, text="Закончим:").grid(row=0, sticky=tk.E)
tk.Label(group2, text="Через:"   ).grid(row=1, sticky=tk.E)
tk.Label(group2, text="Строка:"  ).grid(row=0, sticky=tk.E, column=2)
tk.Label(group2, text="Размер:"  ).grid(row=1, sticky=tk.E, column=2)

stPBar          = ttk.Style( group2)
stPBar.layout(   "lbPBar", [('lbPBar.trough', {'children': [('lbPBar.pbar', {'side': 'left', 'sticky': 'ns'}), ("lbPBar.label",   {"sticky": ""})], 'sticky': 'nswe'})])
stPBar.configure("lbPBar", text="0 %      ")

pbTotal         = ttk.Progressbar( group2, mode="determinate", length = 200, style='lbPBar')
textLogs        = tk.Text( group2, height=4, width=53, font=("Consolas", 8))

lbStart         = tk.Label(group2, text="")
lbEnd           = tk.Label(group2, text="")
lbLine          = tk.Label(group2, text="")
lbLines         = tk.Label(group2, text="")

lbStart.grid(   row=0, sticky=tk.W, column=1)
lbEnd.grid(     row=1, sticky=tk.W, column=1)
lbLine.grid(    row=0, sticky=tk.W, column=3)
lbLines.grid(   row=1, sticky=tk.W, column=3)

pbTotal.grid(   row=2, column=0, columnspan=4, sticky="NSEW")
textLogs.grid(  row=3, column=0, columnspan=4, sticky="NWES", padx=5, pady=5)

#######################################################################################################
group1          = tk.LabelFrame(root, padx=3, pady=3, text="")
group1.grid(row=1, column=0, columnspan=3, padx=0, pady=0, sticky='NWES')
group1.columnconfigure(0, weight=1, minsize=15)
group1.columnconfigure(1, weight=1, minsize=15)
group1.columnconfigure(2, weight=1, minsize=15)
group1.columnconfigure(3, weight=1, minsize=15)
group1.columnconfigure(4, weight=1, minsize=15)
group1.columnconfigure(5, weight=1, minsize=15)
group1.columnconfigure(6, weight=1, minsize=15)
# group1.columnconfigure(7, weight=0, minsize=15)

btnTLScan       = ttk.Button( group1, text="0 rescan tl folder",   width=15, command= lambda: rescanFolders())
btnMakeTemp     = ttk.Button( group1, text="1 make temp files",    width=15, command= lambda: makeTempFiles( fileStat))
btnTempRepl     = ttk.Button( group1, text="2 tags replace",       width=15, command= lambda: findTempBrackets( fileStat))
btnTranslate    = ttk.Button( group1, text="3 translate start",    width=15, command= lambda: treatTranslate())
btnMakeRPY      = ttk.Button( group1, text="4 make Renpy files",   width=15, command= lambda: makeRPYFiles())
btnALL          = ttk.Button( group1, text="just Translate",       width=15, command= makeALLFiles)

btnTLScan.grid(   row=0, column=0, sticky='NWES')
btnMakeTemp.grid( row=0, column=1, sticky='NWES')
btnTempRepl.grid( row=0, column=2, sticky='NWES')
btnTranslate.grid(row=0, column=3, sticky='NWES')
btnMakeRPY.grid(  row=0, column=4, sticky='NWES')
btnALL.grid(      row=0, column=6, sticky='NWES')

button1_ttp = CreateToolTip(btnTLScan,      'Делается автоматически при старте программы.\n Можно тыкать, если поменялись файлы в папке tl или просто скучно...')
button2_ttp = CreateToolTip(btnMakeTemp,    'Делаем временные (temp) файлы в одноименной папке.\n Можно тыкать, если поменялись файлы в папке tl или накосячили с тэгами.'\
                                                ' Временные файлы создаются заново, считываясь из файлов в папке tl, ничего страшного.')
button3_ttp = CreateToolTip(btnTempRepl,    'Замена тэгов во временных (temp) файлах на разумный текст.\n' \
                                                'Заменяем теги в квадратных скобках на свой вариант на английском (!!!) языке, для более качественного перевода, '\
                                                'например "[sister]" -=> "sister" ( что на что менять ищем в коде игры или вангуем).' \
                                                'Если пошло что-то не так то обновляем временные файлы предыдущей кнопкой, меняем тэги и тыкаем заново.\n' \
                                                'Если не меняли, то нажимать это и не надо...\n\n' \
                                                '!u - tag uppercase ("[mom!u]" = "MOM"),\n' \
                                                '!l - tag lowercase ("[MOM!l]" = "mom"),\n' \
                                                '!c - only first character ("[mom!c]" = "Mom")')
button4_ttp = CreateToolTip(btnTranslate,   'Перевод временных файлов (temp) на русский язык (transl).')
button5_ttp = CreateToolTip(btnMakeRPY,     'Сборка переведенных файлов (transl) в Ренпайские файлы (rpy) в папке transl.')
button6_ttp = CreateToolTip(btnALL,         'Одна кнопка для всего. Нажимаем - получаем. Все просто и без затей.')

# sizeGrip    = ttk.Sizegrip(group1)
# sizeGrip.grid( row=0, column=6, sticky=tk.SE)

rescanFolders()
# oprint( root.winfo_toplevel())
root.after(1000, update)
root.mainloop()



# (.{2,5}?)([0-9]*) against this input: $50,000


# i = 5 if a > 7 else 0


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
# ...     print(k, '->', v)
# ...
# ('orange', '->', 3500.0)
# ('banana', '->', 5000.0)
# ('apple', '->', 5600.0)

# >>> for value in sorted(incomes.values()):
# ...     print(value)
# ...
# 3500.0
# 5000.0
# 5600.0




# def a():
#     t = threading.currentThread()
#     while getattr(t, "do_run", True):
#     print('Do something')
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

