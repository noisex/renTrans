import os
# import pandas as pd
# import time
import shutil
# import logging

from settings import settings
from guiClass import YoFrame

app = YoFrame()

folderTL    = settings['folderTL']  # 'workFolder\\tl\\'
folderTEMP  = settings['folderTEMP']  # 'workFolder\\temp\\'
folderTRANS = settings['folderTRANS']  # 'workFolder\\trans\\'
folderRPY   = settings['folderRPY']  # 'workFolder\\tl_done\\'
folderIND   = settings['folderIND']  # 'workFolder\\tl_done\\'
rootPath    = os.path.abspath(os.getcwd()) + '\\'  # C:\GitHub\renTrans\
folderSDK   = rootPath + settings['folderSDK']  # noqa: E221
fileSkip    = settings['fileSkip']

# logFileName = f"{settings['folderLOGS']}mainlog_{time.strftime('%Y.%m.%d')}.log"
# logging.basicConfig(filename=logFileName, format='%(asctime)s %(message)s', datefmt='%Y.%m.%d %H:%M:%S', encoding='utf-8', level=logging.INFO)


def readFileToList( fileName: str) -> tuple:
    try:
        with open(fileName, encoding='utf-8') as infile:
            fileText = infile.read().split('\n')
        return fileText, False
    except BaseException as error:
        app.print(f'{error}!')
        return fileName, error


def writeListToFile( fileName: str, fileText: list) -> None:
    listLen = len(fileText)
    if listLen >= 1:
        smartDirs(fileName)
        with open(fileName, 'w', encoding='utf-8') as f:
            for ind, line in enumerate(fileText, 1):
                # if ind < listLen:
                #     f.write( line + '\n')
                # else:
                #     f.write(line)
                f.write(line + '\n')


def smartDirs( fileName: str) -> None:
    try:
        os.makedirs(os.path.dirname(fileName))
    except FileExistsError:
        pass


def makeNewDirs():
    if not os.path.exists( folderRPY):                                   # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderRPY)
        app.print( f'Папка {folderRPY} - из нее забираем перевод')
    if not os.path.exists( folderTL):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderTL)
        app.print( f'Папка {folderTL} - в нее кладем файлы для перевода')
    if not os.path.exists( folderTEMP):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderTEMP)
        app.print( f'Папка {folderTEMP} - она просто нужна...')
    if not os.path.exists( folderTRANS):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderTRANS)
        app.print( f'Папка {folderTRANS} - она просто нужна...')
    if not os.path.exists( folderIND):                                       # создаем дирректорию для файлов с переводом (если нужно)
        os.mkdir( folderIND)
        app.print( f'Папка {folderIND} - она просто нужна...')


# TODO rewrite listwalk vs listdir
def clearFolder( dirName: str, fileExt='.rpy' ):
    if os.path.exists( dirName):
        try:
            if fileExt == '*':
                shutil.rmtree( dirName)
                smartDirs( dirName)
        except BaseException as error:
            app.print( f'`red`Error.` Cant clear folder [{dirName}] ({error})')

        else:
            test = os.listdir(dirName)
            for item in test:
                try:
                    if item.endswith( fileExt):
                        os.remove(os.path.join(dirName, item))
                except BaseException as error:
                    app.print(f'`red`Error.` Cant delete file [{item}] ({error})')
    else:
        smartDirs( dirName)
        app.print( f'`red`Error.` Path [`bold`{dirName}`] not exists.')


# def readCSVToDic( fileName: str) -> dict:
#     data = pd.read_csv(fileName + ".csv", sep=sep)
#     # data.
#     print(data)
#
#
# def readCSVToList( fileName: str) -> dict:
#     data = pd.read_csv(fileName + ".csv", sep=sep)
#     # data.
#     print(data)


# def writeDictToFile( fileName: str, fileText: dict) -> None:
#     listLen = len(fileText)
#     if listLen >= 1:
#         smartDirs(fileName)
#         header = ['id', 'text']
#         data = pd.DataFrame(fileText, columns=header)
#         data.to_csv(fileName + '.csv', sep=sep, index=False)
#
#         # with open(fileName, 'w', encoding='utf-8') as f:
#         #     for ind, line in enumerate( fileText, 1):
#         #         f.write( line + '\n')
