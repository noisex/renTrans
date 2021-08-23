import os
import re

from deep_translator import GoogleTranslator


###############################################################################################################################

reTrans          = re.compile(r'"(.*\w+.*)"( nointeract)?$'), 0, 0

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


def makeTempFiles( fileTRans):

    for file in fileTRans:

        allFile = []
        with open( file, encoding='utf-8') as f:
            skip    = 0
            allFile = f.read()

            fileName = os.path.basename( file)
            current_file_text = allFile.split('\n')

            tmpFileName = 'temp\\{}.tmp'.format( str( fileName))
            transFileName = 'temp\\{}.transl'.format( str( fileName))

            tmpFile     = open( tmpFileName, 'w', encoding='utf-8')

            try:
                os.remove( tmpFileName)
                os.remove( transFileName)
            except:
                pass

            for line in current_file_text:

                result = re.search( reTrans[0], line)

                if result and len( result.group(1)) >= 1 and skip == 0:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                    skip = 1
                    oLine    = result.group(1)
                    tmpFile.write(str( oLine) + '\n')
                    # print( oLine)
                else:
                    skip = 0

            tmpFile.close()


def listTransFiles():
    filesAll = []
    for top, dirs, files in os.walk('./tl/'):                           # Находим файлы для перевода в дирректории
        for nm in files:
            filesAll.append(os.path.join(top, nm))

    return list(filter(lambda x: x.endswith('.rpy'), filesAll))


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

def readTmpToTrans( fileTRans):

    for file in fileTRans:

        fileName     = os.path.basename( file)
        fileNameTrans = 'temp\\{}.transl'.format( str( fileName))
        fileNameTemp  = 'temp\\{}.tmp'.format( str( fileName))

        print( "File: " + fileName)

        with open( fileNameTemp, encoding='utf-8') as f:

            lineTemp    = ""
            allFile     = f.read()
            fileAllText = allFile.split('\n')

            for line in fileAllText:
                lineTemp = lineTemp + line + '\n'

                lineSize = len( lineTemp)

                if lineSize >= 4500:
                    tryToTranslate( lineTemp, lineSize, fileNameTrans)
                    lineTemp    = ""

            if len( lineTemp) >= 5:
                tryToTranslate( lineTemp, lineSize, fileNameTrans)
                lineTemp    = ""


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

makeNewDirs()
fileTRans = listTransFiles()
print( fileTRans)

makeTempFiles( fileTRans)
readTmpToTrans( fileTRans)
compileTrans( fileTRans)














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
