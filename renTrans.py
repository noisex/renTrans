import re
import os
import time
# import random
import threading

from textblob import TextBlob            # TextBlob
from datetime import datetime
# from googletrans import Translator
from deep_translator import GoogleTranslator

import tkinter as tk
import tkinter.ttk as ttk

filesAll        = []                                             # все файлы
fileTRans       = []                                             # все файлы для перевода
swPause         = 0
swStop          = 0

count           = 0
linesALL        = 0
linesCURRENT    = 0
timeSTART       = 0
timeNOW         = 0
TRANSFULL       = False
reTrans          = re.compile(r'"(.*)"( nointeract)?$'), 0, 0
# reTrans = re.compile(r'"(.*)"$'), 1, -1


def switchPause():        #controls back and forth switching between Pause and Resume
    global swPause
    swPause = not swPause

def switchStop():        #controls back and forth switching between Pause and Resume
    global swStop
    swStop = not swStop

def update():
    root.update()
    root.after(1000, update)


def read_all( file):                                                 # Возвращает имя текущего файла и его текст
    with open(file, encoding='utf-8') as f:
        # file_name = str( re.findall( r'[\w-]*?.rpy', file))
        file_name = os.path.basename( file)
        all_file = f.read()
        current_file_text = all_file.split('\n')
    return current_file_text, file_name


def correct(tLine):                                                 # корректировка всяких косяков первода, надо перписать...
    fix = tLine

    fix = fix.replace(' ...', '...')

    fix = fix.replace( '"', '`')
    fix = fix.replace( '\\ n', '\n')

    fix = fix.replace( '% (', ' %(')
    fix = fix.replace( '{я', '{i}')
    fix = fix.replace( '} ', '}')

    fix = fix.replace( 'Какие? ', 'Что? ')
    fix = fix.replace( 'Какой? ', 'Что? ')
    return fix


def findSkobki( tLine, oLine):                                      # замена кривых, т.е. всех, переведенных тегов на оригинальные

    oResultSC       = re.findall(r'(\[.+?\])', oLine)                        # ищем теги в квадратных скобках в оригинальной строке
    oResultFG       = re.findall(r'({.+?})', oLine)                           # ищем теги в фигурных скобках  в оригинальной строке
    oResultPR       = re.findall(r'(\%\(.+?\))', oLine)

    if oResultSC:
        tResultSC = re.findall(r'(\[.+?\])', tLine)                        # ищем теги в квадратных скобках в переведенной строке
        for i in range( len( oResultSC)):
            try:
                tLine = tLine.replace( tResultSC[i], oResultSC[i])              # заменяем переведенные кривые теги оригинальными по порядку
            except:
                pass

    if oResultFG:
        tResultFG = re.findall(r'({.+?})', tLine)                           # ищем теги в фигурных скобках  в переведеной строке
        for i in range( len( oResultFG)):
            try:
                tLine = tLine.replace( tResultFG[i], oResultFG[i])              # заменяем переведенные кривые теги оригинальными по порядку
            except:
                pass

    if oResultPR:
        tResultPR = re.findall(r'(\%\(.+?\))', oLine)                           # ищем теги с процентами и скобкой в переведеной строке
        for i in range( len( oResultPR)):
            try:
                tLine = tLine.replace( tResultFG[i], oResultPR[i])              # заменяем переведенные кривые теги оригинальными по порядку
            except:
                pass

    return tLine

def translateGooble( oLine):
    # time.sleep( 0.1)

    tLine = translated = GoogleTranslator( source='en', target='ru').translate( oLine)

    # translated = GoogleTranslator(source='auto', target='german').translate_file('path/to/file')

    # tBlob = str( oBlob.translate(to='ru'))                              # Translate
    # tLine = str( tBlob)
    # print( translator)
    return correct( tLine)

def translate_blob(oLine):                                          # возвращает перевод текущей строки
    # r = random.uniform( 0.35, 0.4)                                       # Рандомная пауза между запросами на перевод
    time.sleep( 0.35)

    oBlob = TextBlob(str( oLine))                                       # to TextBlob
    tBlob = str( oBlob.translate(to='ru'))                              # Translate
    tLine = str( tBlob)
    return correct( tLine)


def lineTranslate(all_file_text, currentFilename, timeSTART):          # Ищем строку для перевода
    global linesCURRENT
    global swPause

    count = -1                                                              # номер текущей строки
    skip = 0                                                                # пропускать или нет строку, надо когда записали в массив строку с переводом,чтобы ее не читать для "перевода"

    tmp_text = all_file_text
    lText = len( all_file_text)

    for line in all_file_text:
        count += 1
        linesCURRENT += 1

        if swPause==1:
            btnPause["text"]='Resume'
            time.sleep( 1)
        else:
            btnPause["text"]='Pause'

        result = re.search( reTrans[0], line)

        if result and skip == 0:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
            # oLine       = str( result.group(0))[reTrans[1]:reTrans[2]]

            oLine       = result.group(1)
            percLine    = ( count / lText) * 100
            percTotal   = round( ( linesCURRENT / linesALL) * 100, 2)

            timeNOW     = datetime.today().timestamp()
            timeDelta   = timeNOW - timeSTART
            timeFinish  = ( linesALL * timeDelta) / linesCURRENT
            timeEND     = timeSTART + timeFinish
            timeLaps    = timeFinish - timeDelta
            strPerc     = str( round( percLine, 2)) + "%"
            strPercTotal= str( percTotal)

            lblTimeFinish["text"]   = datetime.utcfromtimestamp( timeFinish).strftime("%Hч %Mм %Sсек")
            lblTimeEnd["text"]      = datetime.fromtimestamp( timeEND).strftime( "%d.%m.%y %H:%M:%S")
            lblTimeLaps["text"]     = datetime.utcfromtimestamp( timeLaps).strftime("%Hч %Mм %Sсек")
            pbCurrent['value']      = percLine
            pbTotal['value']        = percTotal
            # lblPercLine["text"]     = strPerc
            lblPercTotal["text"]    = strPerc + ' [' + strPercTotal + "%]"

            root.title( strPerc + " (" + strPercTotal + "%) " + currentFilename)

            try:
                findWords = re.findall(r'(\w+)', oLine)                                 # если в строке есть слово, то пытаемся перевести

                if findWords:
                    # tLine = oLine
                    tLine = translateGooble( oLine)
                    # tLine = translate_blob( oLine)                                      # пытаемся перевести
                else:
                    tLine = oLine                                                       # если нет, то берем орининальную строку

                # r = random.uniform( 0.01, 0.03)                                       # Рандомная пауза между запросами на перевод
                # time.sleep(r)
                # tLine = oLine                                                       # если нет, то берем орининальную строку

            except:
                tLine = oLine                                                       # если нет, то берем орининальную строку

            if TRANSFULL:                                                           # если хочется иметь копию оригинальной строки внизу переведенной в игре
                tLine = tLine + '\\n{i}{size=-10}{color=#999}' + oLine

            tLine = findSkobki( tLine, oLine)                                       # заменяем теги

            rLine = str( line.replace( str( oLine), tLine))                           # формируем результирующую строку ( не помню почему так, а не собрать нормальную, видимо потому, что бывают еще старые переводы с другим форматом)
            rLine = str( rLine.replace("    # ", "    "))
            rLine = str( rLine.replace("    old ", "    new "))

            # strTemp = '{:4} | {} -==> {}'.format( count, oLine, tLine) + '\n'

            textBox.insert( tk.END, oLine + '\n')
            textBox.see(tk.END)

            textTrans.insert( tk.END, tLine + '\n')
            textTrans.see(tk.END)

            tmp_text[count + 1] = rLine                                             # записываем ее в массив как следующую строку
            skip = 1                                                                # и пропускаем строку, так как туда только что записали перевод

        else:
            skip = 0                                                                # не скипать следующуя строку, пока не найдем строку для первода

    # Запись в файл
    textBox.insert( tk.END, '\n################\n  пишем в файл ' + currentFilename + '\n################\n\n')
    textBox.see(tk.END)

    textTrans.insert( tk.END, '\n################\n  пишем в файл ' + currentFilename + '\n################\n\n')
    textTrans.see(tk.END)

    new_rpy_tr = open('transl\\{}'.format(str(currentFilename)), 'w', encoding='utf-8')

    for i in tmp_text:
        new_rpy_tr.write(str(i) + '\n')

    new_rpy_tr.close()


def makeNewDirs():
    if not os.path.exists( 'transl'):                                   # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir('transl')
        textBox.insert( tk.END, 'Папка transl - из нее забираем перевод\n')

    if not os.path.exists( 'tl'):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir('tl')
        textBox.insert( tk.END, 'Папка tl - в нее кладем файлы для перевода\n')


def scanDirs():
    global fileTRans
    global count
    global linesALL

    filesAll    = []
    fileTRans   = []
    count       = 0
    linesALL    = 0

    makeNewDirs()

    for top, dirs, files in os.walk('./tl/'):                           # Находим файлы для перевода в дирректории
        for nm in files:
            filesAll.append(os.path.join(top, nm))
            count = count + 1

    i = 0
    listFile.delete(0, tk.END)
    fileTRans = list(filter(lambda x: x.endswith('.rpy'), filesAll))

    for file in fileTRans:
        i += 1
        listFile.insert( tk.END, str( i) + '. [' + file + ']')

        with open(file, encoding='utf-8') as f:
            all_file = f.read()
            current_file_text = all_file.split('\n')
            linesALL = linesALL + len( current_file_text)


def startRead( arg):
    timeSTART = datetime.today().timestamp()
    fileCount = 0

    lblTimeStart["text"]= datetime.fromtimestamp( timeSTART).strftime( "%d.%m.%y %H:%M:%S")
    # btnStart['state']   = tk.DISABLED
    btnScan['state']    = tk.DISABLED
    btnPause['state']   = tk.NORMAL

    for i in fileTRans:
        fileCount = fileCount + 1
        currentTextFromFile, currentFilename = read_all(i)

        lblFileName["text"] = "Файл: " + currentFilename + " ( " + str( fileCount) + " / " + str( count) + ")"

        lineTranslate(currentTextFromFile, currentFilename, timeSTART)

    # btnStart['state'] = tk.NORMAL
    btnScan['state']  = tk.NORMAL
    btnPause['state'] = tk.DISABLED


def starTreading():
    x = threading.Thread(target=startRead, args=(1,))

    if btnStart['text'] == 'Start':
        btnStart['text']    = 'Stop'
        pbCurrent['value']  = 0
        pbTotal['value']    = 0
        x.start()
    else:
        btnStart['text']    = 'Start'
        # x.set()
        return

    # x.join()

#################################################################################################################
root= tk.Tk()
root.minsize(770, 550)
root.geometry("1400x800")

root.columnconfigure(0, weight=0, minsize=250)
root.columnconfigure(1, weight=0, minsize=250)
root.columnconfigure(2, weight=1, minsize=70)
root.columnconfigure(3, weight=10, minsize=10)
root.rowconfigure(   2, weight=2)

lblFileName     = tk.Label(text="", font = 20, fg='#00f')
lblFileName.grid( row=0, column=1,  sticky="N", padx=10, pady=10)

#################################################################################################
group_1         = tk.LabelFrame(root, padx=15, pady=10, text="Время")
group_1.grid(row=1, column=0, padx=10, pady=10, sticky='NESW')

tk.Label(group_1, text="Начали:"  ).grid(row=0, sticky=tk.E)
tk.Label(group_1, text="Закончим:").grid(row=1, sticky=tk.E)
tk.Label(group_1, text="Всего:"   ).grid(row=2, sticky=tk.E)
tk.Label(group_1, text="Осталось:").grid(row=3, sticky=tk.E)

lblTimeStart    = tk.Label(group_1, text="")
lblTimeEnd      = tk.Label(group_1, text="")
lblTimeLaps     = tk.Label(group_1, text="", fg='#00f')
lblTimeFinish   = tk.Label(group_1, text="")

lblTimeStart.grid( row=0, column=1, sticky=tk.W)
lblTimeEnd.grid(   row=1, column=1, sticky=tk.W)
lblTimeFinish.grid(row=2, column=1, sticky=tk.W)
lblTimeLaps.grid(  row=3, column=1, sticky=tk.W)

####################################################################################################
group_2         = tk.LabelFrame(root, padx=15, pady=10, text="Прогресс")
group_2.grid(row=1, column=1, padx=10, pady=10, sticky='WNSE')

tk.Label(group_2, text="Проценты:").grid(row=0, column=0, sticky=tk.E)
tk.Label(group_2, text="Файл:"    ).grid(row=1, column=0, sticky=tk.E)
tk.Label(group_2, text="Общий:"   ).grid(row=2, column=0, sticky=tk.E)

lblPercTotal    = tk.Label(group_2, text="", fg='#00f')
pbCurrent       = ttk.Progressbar(group_2, mode="determinate", length = 200)
pbTotal         = ttk.Progressbar(group_2, mode="determinate", length = 200)

btnStart        = tk.Button( group_2, text="Start",  width=10, height=1, command=starTreading)
btnScan         = tk.Button( group_2, text="Rescan", width=10, height=1, command=scanDirs)
btnPause        = tk.Button( group_2, text="Pause",  width=10, height=1, command=switchPause, state=tk.DISABLED)

# lblPercLine.grid(  row=0, column=1, sticky=tk.W)
lblPercTotal.grid( row=0, column=1, sticky=tk.W)

pbCurrent.grid(  row=1, column=1, sticky=tk.E)
pbTotal.grid(    row=2, column=1, sticky=tk.E)

btnPause.grid( row=3, column=1)#, sticky=tk.E)
btnScan.grid(  row=3, column=1, sticky=tk.W)
btnStart.grid( row=3, column=1, sticky=tk.E)

#######################################################################################################
listFile        = tk.Listbox(root, selectmode=tk.MULTIPLE, height=4, width=70)
scrlFile        = tk.Scrollbar(root, command=listFile.yview)
listFile.configure(yscrollcommand=scrlFile.set)
listFile.grid( row=1, column=2, columnspan=1, sticky="NSEW", padx=0, pady=0)
scrlFile.grid( row=1, column=2, rowspan=1, sticky=tk.NE+tk.SE)

#######################################################################################################
group_3         = tk.LabelFrame(root, padx=5, pady=5, text="Перевод")
group_3.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky='NSWE')
group_3.columnconfigure(0, weight=1)
group_3.columnconfigure(1, weight=1)
group_3.rowconfigure(0, weight=2)

textBox         = tk.Text( group_3, font=("Consolas", 9))
textTrans       = tk.Text( group_3, font=("Consolas", 9))
# scrlText        = tk.Scrollbar( group_3, command=textBox.yview)
# textBox.configure(yscrollcommand=scrlText.set)

textBox.grid(  row=0, column=0, sticky="NSWE", padx=10)
textTrans.grid(row=0, column=1, sticky="NSWE", padx=10)
# scrlText.grid( row=0, column=0, sticky="NSWE", padx=10)


# textBox.configure(yscrollcommand=scrlText.set)
# scrlText.grid( row=7, columnspan=6, sticky=tk.NE+tk.SE)

# listFile.grid( row=0, column=4, rowspan=5, sticky="NSEW", padx=5, pady=3)
# listFile.configure(yscrollcommand=scrlFile.set)
# scrlFile.grid( row=0, column=4, rowspan=5, sticky=tk.NE+tk.SE)

scanDirs()

all_file = 0
current_file_text = ""

root.after(1000, update)

root.mainloop()