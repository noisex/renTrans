import os
import re
import time
import threading

import tkinter as tk
import tkinter.ttk as ttk

from deep_translator import GoogleTranslator

###############################################################################################################################

# dictZamena  = {}
fileTRans   = []
fileStat    = {}
threadSTOP  = False
allStart    = False

reFind      = '(\\[.+?\\])'
reTrans     = re.compile(r'"(.*\w+.*)"( nointeract)?$'), 0, 0
reBrackets  = [
    '(\\[.+?\\])',          # квадратные скобки  - []
    '({.+?})',              # фигурные скобки    - {}
    '(\\%\\(.+?\\))'        # процент со скобкой - %()
]

#################################################################################################################
class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 300   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
#############################################################################################

def print( line):
    textLogs.insert( tk.END, '[{}] {}\n'.format( time.strftime('%H:%M:%S'), str( line)))
    textLogs.see( tk.END)

def update():
    root.update()
    root.after(1000, update)


def makeNewDirs():
    if not os.path.exists( 'transl'):                                   # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir('transl')
        print( 'Папка transl - из нее забираем перевод')

    if not os.path.exists( 'tl'):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir('tl')
        print( 'Папка tl - в нее кладем файлы для перевода')

    if not os.path.exists( 'temp'):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir('temp')
        print( 'Папка temp - она просто нужна...')


def clearFolder( fileExt='transl', dirName='temp'):
    test = os.listdir(dirName)

    for item in test:
        if item.endswith( fileExt):
            os.remove(os.path.join(dirName, item))


def rescanFolders():
    makeNewDirs()
    print( 'scan tl folder')
    global fileTRans
    global fileStat
    fileTRans = listTransFiles()
    fileStat  = listFileStats( fileTRans)
    return fileTRans, fileStat


def listFileUpdate( fileStat):
    i = 0
    listFile.delete(0, tk.END)
    listFile.insert( tk.END,  "{:^33}|{:^10}|{:^7}".format( 'File', 'Size', 'Lines'))

    for fileName in fileStat:
        i += 1
        fs = fileStat[fileName]
        listFile.insert( tk.END,  "{:2}|{:<30}|{:>10,}|{:>7}".format( i, fs['name'], fs['tempFSize'], fs['tempFLine']))


def listTransFiles():
    filesAll = []
    for top, dirs, files in os.walk('./tl/'):                           # Находим файлы для перевода в дирректории
        for nm in files:
            filesAll.append(os.path.join(top, nm))

    print( 'make listFiles')
    return list(filter(lambda x: x.endswith('.rpy'), filesAll))


def listFileStats( fileList):
    fileStat = {}
    i        = 0

    for filePath in fileList:                           # Находим файлы для перевода в дирректории

        fileName = os.path.basename( filePath)
        fileSize = os.path.getsize( filePath)
        filesMax = len( fileList)
        i        += 1

        allFile = []
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
        if fileName not in fileStat: fileStat[fileName] = {}

        fileStat[fileName]['name'] = fileName
        fileStat[fileName]['size'] = fileSize
        fileStat[fileName]["path"] = filePath
        fileStat[fileName]['path'] = filePath
        fileStat[fileName]['lines'] = lines
        fileStat[fileName]["chars"] = linesLen
        fileStat[fileName]['tempFLine'] = 0
        fileStat[fileName]['tempFSize'] = 0
        fileStat[fileName]['filesMax'] = filesMax
        fileStat[fileName]['filesCur'] = i

    listFileUpdate( fileStat)
    print( 'make filesStats')
    return fileStat


def findCorrect( fix):                                                 # корректировка всяких косяков первода, надо перписать...

    fix = fix.replace(' ...', '...')
    fix = fix.replace( '\\ "', '\\"')

    fix = fix.replace( '"', '`')
    fix = fix.replace( '\\ n', '\\n')
    fix = fix.replace( '\\ N', '\\n')

    fix = fix.replace( '% (', ' %(')
    fix = fix.replace( '{я', '{i}')
    fix = fix.replace( '} ', '}')

    fix = fix.replace( 'Какие?', 'Что?')
    fix = fix.replace( 'Какие!', 'Что!')
    fix = fix.replace( 'Какие..', 'Что..')

    fix = fix.replace( 'Какой?', 'Что?')
    fix = fix.replace( 'Какой!', 'Что!')
    fix = fix.replace( 'Какой..', 'Что..')

    x = fix.find( 'Какие')
    if x >= 0:
        print( str( fix))
        pass

    return fix


def findSkobki( tLine, oLine):                                      # замена кривых, т.е. всех, переведенных тегов на оригинальные
    for reFind in reBrackets:
        oResultSC = re.findall( reFind, oLine)                              # ищем теги в скобках в оригинальной строке

        if oResultSC:
            tResultSC = re.findall( reFind, tLine)                          # ищем теги в скобках в переведенной строке
            for i in range( len( oResultSC)):
                try:
                    tLine = tLine.replace( tResultSC[i], oResultSC[i])              # заменяем переведенные кривые теги оригинальными по порядку
                except:
                    pass

    return tLine


def findTempBrackets( fileTRans):
    dictTemp   = {}

    text01     = textTag.get(1.0, tk.END)
    text02     = textEng.get(1.0, tk.END)
    textLine01 = text01.split('\n')
    textLine02 = text02.split('\n')

    i = 0
    for line in textLine01:
        if line != textLine02[i]:
            dictTemp[line] = textLine02[i]
            print( line + ' -=> ' + textLine02[i])
        i += 1

    for tempFile in fileTRans:
        fileNameTemp  = 'temp\\{}.tmp'.format( str( tempFile))

        # Read in the file
        with open( fileNameTemp, 'r', encoding='utf-8') as file :
            filedata = file.read()

        # Replace the target string
        for tempLine in dictTemp:

            if tempLine != dictTemp[tempLine]:
                # print( tempLine, dictTemp[tempLine])
                filedata = filedata.replace( tempLine, dictTemp[tempLine])

        with open( fileNameTemp, 'w', encoding='utf-8') as file:
            file.write(filedata)

    print(dictTemp)


def findZamena( oLine, dictZamena):

    oResultSC = re.findall( reFind, oLine)

    if oResultSC:
        for i in range( len( oResultSC)):
            dictZamena[oResultSC[i]] = oResultSC[i]              # выписываем в словарь тэги в квадратных скобках


def tryToTranslate( oLine, lineSize, file):

    fileName     = 'temp\\{}.transl'.format( str( file))
    fileTempSize = fileStat[file]['tempFLine']
    filesMax     = fileStat[file]['filesMax']
    filesCur     = fileStat[file]['filesCur']
    tLine        = GoogleTranslator( source='en', target='ru').translate( oLine)

    if fileTempSize != 0:
        fileReadProc = ( lineSize / fileTempSize) * 100
    else:
        fileReadProc = 0

    print( '-=> {:5}% {:2}/{} [{}]'.format( round( fileReadProc, 1), filesCur, filesMax, file))

    if tLine:
        f = open( fileName,'a', encoding='utf-8')
        f.write( tLine + '\n')
        f.close()


def makeTempFiles( fileTRans):

    clearFolder( 'tmp')
    clearFolder( 'transl')
    print( "start creating temp files...")
    # global dictZamena

    dictZamena = {}
    textTag['state'] = tk.NORMAL
    textTag.delete( '1.0', tk.END)
    textEng.delete( '1.0', tk.END)

    for file in fileTRans:

        allFile = []
        with open( file, encoding='utf-8') as f:
            skip    = 0
            fileSize= 0
            lines   = 0
            allFile = f.read()

            fileName = os.path.basename( file)
            fileText = allFile.split('\n')

            tmpFileName   = 'temp\\{}.tmp'.format( str( fileName))
            transFileName = 'temp\\{}.transl'.format( str( fileName))
            tmpFile       = open( tmpFileName, 'w', encoding='utf-8')
            # print( 'create tempFile [' + fileName + '] done')

            for line in fileText:

                result = re.search( reTrans[0], line)

                if result and len( result.group(1)) >= 1 and skip == 0:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                    skip     = 1
                    lines    += 1
                    oLine    = result.group(1)
                    fileSize = fileSize + len( oLine)

                    tmpFile.write( str( oLine) + '\n')

                    findZamena( oLine, dictZamena)
                else:
                    skip = 0

            fileStat[fileName]['tempFSize'] = fileSize
            fileStat[fileName]['tempFLine'] = lines
            tmpFile.close()

        # incomes = {'apple': 5600.00, 'orange': 3500.00, 'banana': 5000.00}
        sorted_income = {k: dictZamena[k] for k in sorted(dictZamena)}

    for zamane in sorted_income:
        textTag.insert( tk.END, zamane + '\n')
        textEng.insert( tk.END, zamane + '\n')
        # textTag.see(tk.END)
        # textEng.see(tk.END)

    textTag['state'] = tk.DISABLED
    listFileUpdate(fileStat)
    print( "temp files done!\n")


def makeTransFiles( fileTRans):
    global allStart
    clearFolder( 'transl')
    print( '\nstart translating...')

    for file in fileTRans:

        fileName        = os.path.basename( file)
        fileNameTemp    = 'temp\\{}.tmp'.format( str( fileName))
        lineCount       = -1

        with open( fileNameTemp, encoding='utf-8') as f:

            lineTemp    = ""
            allFile     = f.read()
            fileAllText = allFile.split('\n')

            for line in fileAllText:

                if not getattr( threadSTOP, "do_run"):
                    print( 'translate break.\n')
                    return

                lineCount    += 1
                lineTemp     = lineTemp + line + '\n'
                lineSize     = len( lineTemp)

                if lineSize >= 4700:
                    tryToTranslate( lineTemp, lineCount, fileName)
                    lineTemp    = ""

            if len( lineTemp) >= 5:
                tryToTranslate( lineTemp, lineCount, fileName)
                lineTemp    = ""

    threadSTOP.do_run = False
    btnTranslate['text']    = '3 translate start'
    print( 'translating done!\n')
    if allStart:
        allStart = False
        makeRPYFiles( fileTRans)


def makeRPYFiles( fileTRans):

    print( 'start compile renpy files...')
    for file in fileTRans:

        lineCount       = -1
        lineFoundCount  = 0
        fileName        = os.path.basename( file)
        fileNameTrans   = 'temp\\{}.transl'.format( str( fileName))
        fileNameDone    = 'transl\\{}'.format(str(fileName))
        allFile         = []

        fileTemp        = open( fileNameTrans, encoding='utf-8').read()
        linesTemp       = fileTemp.split('\n') # readlines()

        with open( file, encoding='utf-8') as f:
            skip    = 0
            allFile = f.read()

            fileAllText = allFile.split('\n')

            for line in fileAllText:

                lineCount = lineCount + 1
                result = re.search( reTrans[0], line)

                if result and len( result.group(1)) >= 1 and skip == 0:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)

                    skip  = 1
                    oLine = result.group(1)
                    tLine = linesTemp[lineFoundCount]

                    tLine = findCorrect( tLine)
                    tLine = findSkobki( tLine, oLine)                                       # заменяем теги

                    rLine = str( line.replace( str( oLine), tLine))                           # формируем результирующую строку ( не помню почему так, а не собрать нормальную, видимо потому, что бывают еще старые переводы с другим форматом)
                    rLine = str( rLine.replace("    # ", "    "))
                    rLine = str( rLine.replace("    old ", "    new "))

                    fileAllText[lineCount + 1] = rLine                                             # записываем ее в массив как следующую строку
                    lineFoundCount = lineFoundCount + 1

                elif result and len( result.group(1)) < 1:
                    lineFoundCount = lineFoundCount + 1
                    skip = 0

                else:
                    skip = 0

            new_rpy_tr = open( fileNameDone, 'w', encoding='utf-8')

            for i in fileAllText:
                new_rpy_tr.write(str(i) + '\n')

            # print( "make file [" + fileName + '] done')
            new_rpy_tr.close()

    print( 'compile renpy files done!!!\n')
    print( 'можно копировать все это ( папка /transl/) обратно в игру ( папка /game/tl/rus/)')


def makeALLFiles():
    global allStart
    allStart = True

    rescanFolders()
    makeTempFiles( fileTRans)
    treatTranslate( fileTRans)


def treatTranslate( fileTRans):
    global threadSTOP

    if btnTranslate['text'] == '3 translate start':
        btnTranslate['text']    = '3 translate stop'

        threadSTOP = threading.Thread( name='trans', target=makeTransFiles, args=( fileTRans,))
        threadSTOP.do_run = True
        threadSTOP.start()
    else:
        btnTranslate['text']    = '3 translate start'
        # t = getThreadByName('trans') #Get thread by name
        threadSTOP.do_run = False


#######################################################################################################

root= tk.Tk()
root.minsize( 750, 300)
root.geometry("1100x450")

root.columnconfigure(0, weight=0, minsize=50)
root.columnconfigure(1, weight=0, minsize=50)
root.columnconfigure(2, weight=1, minsize=50)
root.rowconfigure(   0, weight=2, pad=5)
root.rowconfigure(   1, weight=0, pad=5)

#######################################################################################################
listFile        = tk.Listbox( root, selectmode=tk.NORMAL, height=4, width=53, font=("Consolas", 8))
textLogs        = tk.Text( root, height=4, width=53, font=("Consolas", 8))

listFile.grid( row=0, column=0, sticky="NWES", padx=5, pady=5)
textLogs.grid( row=0, column=2, sticky="NWES", padx=5, pady=5)

group0          = tk.LabelFrame(root, padx=5, pady=10, text="        [game_tag]        -=>      'eng text'   ")
group0.grid( row=0, column=1, padx=5, pady=0, sticky='NWES')
group0.columnconfigure(0, weight=2, minsize=25)
group0.columnconfigure(1, weight=2, minsize=25)
group0.rowconfigure(   0, weight=2, pad=0)

textTag         = tk.Text( group0, font=("Consolas", 8), width=25)#, state=tk.DISABLED)
textEng         = tk.Text( group0, font=("Consolas", 8), width=25)

textTag.grid( row=0, column=0, sticky='NWES', padx=5)
textEng.grid( row=0, column=1, sticky='NWES', padx=5)

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

btnTLScan       = tk.Button( group1, text="0 rescan tl folder",   width=15, height=1, command= lambda: rescanFolders())
btnMakeTemp     = tk.Button( group1, text="1 make temp files",    width=15, height=1, command= lambda: makeTempFiles( fileTRans))
btnTempRepl     = tk.Button( group1, text="2 tags replace",       width=15, height=1, command= lambda: findTempBrackets( fileStat))
btnTranslate    = tk.Button( group1, text="3 translate start",    width=15, height=1, command= lambda: treatTranslate( fileTRans))
btnMakeRPY      = tk.Button( group1, text="4 make Renpy files",   width=15, height=1, command= lambda: makeRPYFiles( fileTRans))
btnALL          = tk.Button( group1, text="just Translate",       width=15, height=1, command= makeALLFiles)

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

rescanFolders()

root.after(1000, update)
root.mainloop()


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