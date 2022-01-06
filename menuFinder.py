import os
import shutil
import re
import logging

folderIN = "game"
# folderOUT = 'output'
folderBak = '_backup'
folderBackWrite = ''

itemDict = {}
itemSize = '{size=-5}{color=#777}'

reMenu   = '\\s{4,}menu:'
reSpace  = '\\s{4}'

logging.basicConfig(filename='menuFinder.log', format='%(asctime)s %(message)s', datefmt='%Y.%m.%d %H:%M:%S', encoding='utf-8', level=logging.ERROR)
#######################################################################################

def fileCopy( filePath=str):

    fileBackPath = f'{folderBackWrite}\\{os.path.dirname( filePath)}\\'
    fileBackFile = fileBackPath + os.path.basename( filePath)

    os.makedirs( fileBackPath, exist_ok=True)
    shutil.copy2( filePath, fileBackFile) # complete target filename given

    print( filePath, fileBackFile)


def makeNewDirs():
    global folderBackWrite
    folderBackWrite = folderBak

    i = 0
    while os.path.exists( folderBackWrite):                  # приписывает число к имени, если есть такой файл
        i += 1
        folderBackWrite = '{} ({:02})'.format( folderBak, i)


def listTransFiles():
    makeNewDirs()
    filesAll = []
    for top, dirs, files in os.walk( folderIN):                           # Находим файлы для перевода в дирректории
        for nm in files:
            filesAll.append(os.path.join(top, nm))

    # print( '[make listFiles]')
    return sorted( list(filter(lambda x: x.endswith('.rpy'), filesAll)))


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


def menuFileWrite( filePath=str, fileText=list):
    if len( itemDict[filePath]) < 2:
        return

    lineID = 0
    fileCopy( filePath)

    tmpFile = open( f'{filePath}', 'w', encoding='utf-8')
    logging.error( f'[{filePath}]')

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


def findMenuStart( fileList):

    for filePath in fileList:
        with open( filePath, encoding='utf-8') as infile:
            fileText = infile.read().split('\n')

        itemDict[filePath] = {}
        menuFileRead( filePath, fileText)
        menuFileWrite( filePath, fileText)

#################################################################################################

logging.error( f' -=> start...\n' )

findMenuStart( listTransFiles())

logging.error( f' -=> end.\n' )

# for keys, values in menuDict.keys():  .values() .items() !!!!
    # m = menuDict[i]
    # print( f'{i} = {m}')
    # print( f'{i} = {m}')

# for files in itemDict:
#     logging.error( f'[{files}]' )

#     for itemStr in itemDict[files]:
#         logging.error( f'-=> [{itemStr}] = [{itemDict[files][itemStr]}]' )
#         pass

# print( list( itemDict.keys())[-1])


    # tmpFile = open( f'{fileName}', 'w', encoding='utf-8')
    # logging.error( f'[{fileName}]')

    # for line in fileText:
    #     lineID += 1

    #     if lineID in itemDict[filePath]:

    #         if line.find( '" ') > 10:   # если вконце меню есть ИФ или еще что-то
    #             strReplace = '" '
    #         else:
    #             strReplace = '":'

    #         line = line.replace( strReplace, itemDict[filePath][lineID] + strReplace)
    #         logging.error( f'-=> [{lineID}] = [{line.strip()}]')

        # tmpFile.write( line + '\n')
    # tmpFile.close()