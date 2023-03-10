import re

from settings import settings
import filesClass as files

reString    = re.compile( r'(^\s*[\w$\"]+)')
reItem      = re.compile( r'^\s*\"(.+?)\".*?:')
reVars      = re.compile( r'\$\s*([\w-]+\s*[-+=]+\s*(?:True|False|[-+\d]+))')


def itemClearFromOld( line: str) -> str:
    """очищаем строку от добавленных ранее подсказок"""
    itemStart = line.find( settings['itemSize'])
    if itemStart > 0:
        line = line[0:itemStart]  # + line[itemEnd:]
    return line


def menuFindVars( _event, game):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    game.print( f'Find menu with variables ( backUp in [`bold`{game.backupFolder}`])...', True)

    pathGame        = game.getPathGame()
    itemsCountTotal = 0
    itemVarsTotal   = 0
    itemsReplaceTotal = 0
    newBackup       = True
    varStrLen       = len( settings['itemSize'])

    fileList = files.getFolderList(pathGame, '.rpy', withTL=False, silent=True)
    game.makeNewBackupFolder()

    for fileName, fileValue in fileList.items():

        items           = []
        itemsCount      = 0
        itemsReplace    = 0
        itemVars        = 0
        listText, _err  = files.readFileToList( fileName)

        for ind, line in enumerate(listText):
            # нашли строку, не пустую и не коментарий
            if re.match(reString, line):
                currentLevel = game.stringLevel4( line)
                # если есть открытая менюха - лен итемс больше 0
                if len(items) > 0:
                    # нашли переменную внутри менюхи - накапливаем в строке
                    res = re.search(reVars, line)
                    if res:
                        itemVars         += 1
                        itemVarsTotal    += 1
                        items[-1]['var'] += f'{res.group(1).replace( " ", "")}, '
                        # print(f'VARS = {line} =========== {res.group(1)}')
                    # пришла строка левее ластитема
                    if currentLevel <= items[-1]['lvl']:
                        # чистим правые елементы меню внутри итемс. все, что меньше
                        while len(items) > 0:
                            lastItem = items[-1]
                            # проверяем на левость элементы стека итемов и скидываем в них накопленные вары
                            if currentLevel <= lastItem['lvl']:
                                items.pop()
                                # просто обнуляем, если не нашли переменных в менюшке
                                if len(lastItem['var']) > varStrLen:
                                    # lineValue = re.sub( r'[\[\]]', '.', lineValue))
                                    itemsReplace            += 1
                                    itemsReplaceTotal       += 1
                                    # рубим строку по последней кавычке [0-до, 1-кавычка, 2-после]
                                    pieceOfString           = lastItem['str'].rpartition( '"')
                                    lastItem['str']         = itemClearFromOld( pieceOfString[0])
                                    # вставляем между кусками строки свое ( 0-наше-1-2)
                                    listText[lastItem['no']]= f'{pieceOfString[0]}{lastItem["var"][0:160]}"{pieceOfString[2]}'
                            else:
                                break
                # чекаем, это элемент меню, создаем новый итем и пихаем в стэк
                if re.match(reItem, line):
                    itemsCount      += 1
                    itemsCountTotal += 1

                    item = {}
                    item['lvl'] = currentLevel
                    item['no']  = ind
                    item['str'] = line
                    item['var'] = settings['itemSize']

                    items.append(item)
                    # print(f"{ind:4} {itemIND:3}. =>{currentLevel:2}, L={len(items)} + {line}")

        if itemsReplace > 0:
            if newBackup:
                newBackup = False
                game.makeNewBackupFolder()

            game.print( f'`green`{itemsReplace:3}` items from `green`{itemsCount:4}` replaced with [`red`{itemVars:3}` vars] in [`bold`{fileValue["fileShort"]}`]')
            files.copyMenuToBackUp( game, fileName)
            files.writeListToFile(fileName, listText)

    if itemsReplaceTotal > 0:
        game.print(f'Total: `bold`{itemsCountTotal}` menu items found, `bold`{itemsReplaceTotal}` was replaced, with `bold`{itemVarsTotal}` vars.')
    else:
        game.print( '`bold`No vars to replace was found...`', True)


def main():
    pass


if __name__ == '__main__':
    main()
