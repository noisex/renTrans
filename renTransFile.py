import os
import re
import time
import threading
import multiprocessing

import tkinter as tk
import tkinter.ttk as ttk

from deep_translator import GoogleTranslator

###############################################################################################################################

dictZamena  = {}
fileTRans   = []
fileStat    = {}
threadSTOP  = False
proc = False

reTrans     = re.compile(r'"(.*\w+.*)"( nointeract)?$'), 0, 0
reBrackets  = [
    '(\\[.+?\\])',          # квадратные скобки  - []
    '({.+?})',              # фигурные скобки    - {}
    '(\\%\\(.+?\\))'        # процент со скобкой - %()
]


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
    # dirName = "/Users/ben/downloads/"
    test = os.listdir(dirName)

    for item in test:
        if item.endswith( fileExt):
            os.remove(os.path.join(dirName, item))


def listFileUpdate( fileStat):
    i = 0
    listFile.delete(0, tk.END)
    listFile.insert( tk.END,  "{:^33}|{:^10}|{:^7}".format( 'File', 'Size', 'Lines'))

    for fileName in fileStat:
        i += 1
        fs = fileStat[fileName]
        listFile.insert( tk.END,  "{:2}|{:<30}|{:>10,}|{:>7}".format( i, fs['name'], fs['tempFSize'], fs['tempFLine']))


def filesStats( fileList):
    fileStat = {}
    i        = 0

    # listFile.delete(0, tk.END)
    # listFile.insert( tk.END,  "{:^33}|{:^10}|{:^7}".format( 'File', 'Size', 'Lines'))

    for filePath in fileList:                           # Находим файлы для перевода в дирректории

        fileName = os.path.basename( filePath)
        fileSize = os.path.getsize( filePath)
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
        # print( filePath, fileName, words, characters, lines, linesLen)
        if fileName not in fileStat: fileStat[fileName] = {}

        fileStat[fileName]['name'] = fileName
        fileStat[fileName]['size'] = fileSize
        fileStat[fileName]["path"] = filePath
        fileStat[fileName]['path'] = filePath
        fileStat[fileName]['lines'] = lines
        fileStat[fileName]["chars"] = linesLen
        fileStat[fileName]['tempFLine'] = ''
        fileStat[fileName]['tempFSize'] = 0

        # listFile.insert( tk.END,  "{:2}|{:<30}|{:>10,}|{:>7,}".format( i, fileName, fileSize, lines))
    listFileUpdate( fileStat)

    return fileStat


def listTransFiles():
    filesAll = []
    for top, dirs, files in os.walk('./tl/'):                           # Находим файлы для перевода в дирректории
        for nm in files:
            filesAll.append(os.path.join(top, nm))

    return list(filter(lambda x: x.endswith('.rpy'), filesAll))


def correct( fix):                                                 # корректировка всяких косяков первода, надо перписать...

    fix = fix.replace(' ...', '...')
    fix = fix.replace( '\\ "', '\\"')

    fix = fix.replace( '"', '`')
    fix = fix.replace( '\\ n', '\\n')
    fix = fix.replace( '\\ N', '\\n')

    fix = fix.replace( '% (', ' %(')
    fix = fix.replace( '{я', '{i}')
    fix = fix.replace( '} ', '}')

    fix = fix.replace( 'Какие?', 'Что?')
    fix = fix.replace( 'Какой?', 'Что?')
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


def findZamena( oLine, dictZamena):

    reFind = '(\\[.+?\\])'
    oResultSC = re.findall( reFind, oLine)

    if oResultSC:
        for i in range( len( oResultSC)):
            dictZamena[oResultSC[i]] = oResultSC[i]              # заменяем переведенные кривые теги оригинальными по порядку


def makeTempFiles( fileTRans):

    clearFolder( 'tmp')
    clearFolder( 'transl')

    global dictZamena

    dictZamena = {}
    textBox['state'] = tk.NORMAL
    textBox.delete( '1.0', tk.END)
    textTrans.delete( '1.0', tk.END)

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

    for zamane in dictZamena:
        textBox.insert( tk.END, zamane + '\n')
        textTrans.insert( tk.END, zamane + '\n')
        # textBox.see(tk.END)
        # textTrans.see(tk.END)

    textBox['state'] = tk.DISABLED
    listFileUpdate(fileStat)



def tryToTranslate( oLine, lineSize, file):
    print(" -=> ", lineSize, file)

    # tLine       = ""
    # fileName    = os.path.basename( file)
    # tmpFileName = 'temp\\{}.transl'.format( str( fileName))
    tLine       = GoogleTranslator( source='en', target='ru').translate( oLine)

    if tLine:
        f = open( file,'a', encoding='utf-8')
        f.write( tLine + '\n')
        f.close()


def tempReplace( fileTRans):
    text = textTrans.get(1.0, tk.END)
    textTemp = text.split('\n')

    i = 0
    for line in dictZamena:
        dictZamena[line] = textTemp[i]
        i += 1

    for tempFile in fileTRans:
        fileNameTemp  = 'temp\\{}.tmp'.format( str( tempFile))

        # Read in the file
        with open( fileNameTemp, 'r', encoding='utf-8') as file :
            filedata = file.read()

        # Replace the target string
        for tempLine in dictZamena:

            if tempLine != dictZamena[tempLine]:
                # print( tempLine, dictZamena[tempLine])
                filedata = filedata.replace( tempLine, dictZamena[tempLine])

        with open( fileNameTemp, 'w', encoding='utf-8') as file:
            file.write(filedata)


def readTmpToTrans( fileTRans):
    clearFolder( 'transl')

    for file in fileTRans:

        fileName        = os.path.basename( file)
        fileNameTrans   = 'temp\\{}.transl'.format( str( fileName))
        fileNameTemp    = 'temp\\{}.tmp'.format( str( fileName))
        # fileCount       = 0

        with open( fileNameTemp, encoding='utf-8') as f:

            lineTemp    = ""
            allFile     = f.read()
            fileAllText = allFile.split('\n')

            for line in fileAllText:
                # lineCount += 1

                if not getattr( threadSTOP, "do_run"): return

                lineTemp = lineTemp + line + '\n'

                lineSize = len( lineTemp)

                if lineSize >= 4700:
                    tryToTranslate( lineTemp, lineSize, fileNameTrans)
                    lineTemp    = ""

            if len( lineTemp) >= 5:
                tryToTranslate( lineTemp, lineSize, fileNameTrans)
                lineTemp    = ""


def treatTranslate( fileTRans):
    global threadSTOP

    if btnTranslate['text'] == '3 translate start':
        btnTranslate['text']    = '3 translate stop'

        threadSTOP = threading.Thread( name='trans', target=readTmpToTrans, args=( fileTRans,))
        threadSTOP.do_run = True
        threadSTOP.start()
    else:
        btnTranslate['text']    = '3 translate start'
        # t = getThreadByName('trans') #Get thread by name
        threadSTOP.do_run = False


def compileTrans( fileTRans):

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

                    tLine = correct( tLine)
                    tLine = findSkobki( tLine, oLine)                                       # заменяем теги

                    rLine = str( line.replace( str( oLine), tLine))                           # формируем результирующую строку ( не помню почему так, а не собрать нормальную, видимо потому, что бывают еще старые переводы с другим форматом)
                    rLine = str( rLine.replace("    # ", "    "))
                    rLine = str( rLine.replace("    old ", "    new "))

                    fileAllText[lineCount + 1] = rLine                                             # записываем ее в массив как следующую строку

                    # print( file, lineCount, tLine, rLine)

                    lineFoundCount = lineFoundCount + 1
                    # tmpFile.write(str( oLine) + '\n')
                    # print( oLine)

                elif result and len( result.group(1)) < 1:
                    lineFoundCount = lineFoundCount + 1
                    skip = 0

                else:
                    skip = 0

            new_rpy_tr = open( fileNameDone, 'w', encoding='utf-8')

            for i in fileAllText:
                new_rpy_tr.write(str(i) + '\n')

            print( "File done:", fileName)
            new_rpy_tr.close()


def rescanFolders():
    makeNewDirs()

    global fileTRans
    global fileStat

    fileTRans = listTransFiles()
    fileStat  = filesStats( fileTRans)

    return fileTRans, fileStat

def justTranslate( fileTRans):
    makeTempFiles( fileTRans)
    treatTranslate( fileTRans)
    compileTrans( fileTRans)


#################################################################################################################
class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 280   #pixels
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


root= tk.Tk()
root.minsize( 400, 300)
root.geometry("800x400")

root.columnconfigure(0, weight=0, minsize=50)
root.columnconfigure(1, weight=0, minsize=50)
root.columnconfigure(2, weight=1, minsize=50)


listFile = tk.Listbox( root, selectmode=tk.NORMAL, height=4, width=53, font=("Consolas", 8))
listFile.grid( row=0, column=0, sticky="NSEW", padx=5, pady=5)

rescanFolders()

group_3  = tk.LabelFrame(root, padx=5, pady=0, text="Тэги")
group_3.grid(row=0, column=1, padx=5, pady=0, sticky='NSWE')
group_3.columnconfigure(0, weight=0, minsize=15)
group_3.columnconfigure(1, weight=0, minsize=15)
# group_3.rowconfigure(0, weight=2)

textBox         = tk.Text( group_3, font=("Consolas", 9), width=15)#, state=tk.DISABLED)
textTrans       = tk.Text( group_3, font=("Consolas", 9), width=15)

textBox.grid(  row=0, column=0, sticky="NSWE", padx=5)
textTrans.grid(row=0, column=1, sticky="NSWE", padx=5)

btnTLScan       = tk.Button( root, text="0 rescan tl folder",   width=15, height=1, command= lambda: rescanFolders())
btnMakeTemp     = tk.Button( root, text="1 make temp files",    width=15, height=1, command= lambda: makeTempFiles( fileTRans))
btnTempRepl     = tk.Button( root, text="2 tags replace",       width=15, height=1, command= lambda: tempReplace( fileStat))
btnTranslate    = tk.Button( root, text="3 translate start",     width=15, height=1, command= lambda: treatTranslate( fileTRans))
btnMakeRPY      = tk.Button( root, text="4 make Renpy files",   width=15, height=1, command= lambda: compileTrans( fileTRans))
btnALL          = tk.Button( root, text="just Translate",       width=15, height=1, command= lambda: justTranslate( fileTRans))

btnTLScan.grid(   row=1, column=0, sticky=tk.W)
btnMakeTemp.grid( row=1, column=0, sticky=tk.N)
btnTempRepl.grid( row=1, column=0, sticky=tk.E)
btnTranslate.grid(row=1, column=1, sticky=tk.W)
btnMakeRPY.grid(  row=1, column=1, sticky=tk.E)
btnALL.grid(      row=1, column=2, sticky=tk.E)

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

root.after(1000, update)
root.mainloop()

# makeTempFiles( fileTRans)

# for fileName in fileStat:
#     fs = fileStat[fileName]

#     print( "{:>30}| Size: {:9,} | Lines: {:6} | Chars: {:7} | tempFSize [{}]".format( fs['name'], fs['size'], fs['lines'], fs['chars'], fs['tempFSize']))


# readTmpToTrans( fileTRans)
# compileTrans( fileTRans)


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

############################
# # Read in the file
# with open('file.txt', 'r') as file :
#   filedata = file.read()

# # Replace the target string
# filedata = filedata.replace('ram', 'abcd')

# # Write the file out again
# with open('file.txt', 'w') as file:
#   file.write(filedata)
###################################







# lineSize = 0
# for file in fileTRans:
#     i += 1
#         translated = GoogleTranslator( source='en', target='ru').translate_file( tmpFileName)
#         if translated:
#             transFileName = 'tl\\{}.trans'.format( str( file_name))
#             transFile = open( transFileName, 'w', encoding='utf-8')
#             print( translated)
#             print( lineSize)
#             # for line in translated:
#                 # print( line)
#             transFile.write( translated)
#             transFile.close()


# def terTest( fileTRans):
#     # while getattr( threadSTOP, "do_run", True):
#     while True:
#         myAttr = getattr( threadSTOP, "do_run")
#         print( "sadsadsa", myAttr)
#         time.sleep( 1)
#         if not myAttr:
#             return
#     print("Stopping as you wish.")