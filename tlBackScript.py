import re
import filesClass as files

# from main import app, game

reTL = re.compile( r'^# .*:(\d+)')


# todo rename old rus files
def backTLtoScriptClick( game):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    needBackup  = True
    fileCount   = 0
    fileTLList  = files.getFolderList( game.gameTLRUS, ext='.rpy', withTL=True, withStat=False)

    for fileName in fileTLList:

        lineCount           = 0
        fileCount          += 1
        fileScript          = fileName.replace( '\\tl\\rus', '')
        fileLines, _error   = files.readFileToList( fileName)
        scriptLines, _error = files.readFileToList( fileScript)

        for ind, line in enumerate( fileLines):
            # строка в ТЛ файле: # game/filename_script.rpy:9 <==-- находим номер строки
            result = re.findall( reTL, line)
            if (result):
                lineCount += 1
                # собираем начальные пробелы из оригинальной строки
                newLevel = " " * game.stringLevel4( scriptLines[int(result[0]) - 1])
                # убираем первые 4 пробелы из переводной строки
                newLine  = fileLines[ind + 4].replace( "    ", "", 1)
                newLine  = newLevel + newLine
                # print( newLevel, oldLevel, scriptLines[int(result[0]) - 1], newLine)
                scriptLines[int(result[0]) - 1] = newLine

        if lineCount > 0:
            if needBackup:
                needBackup = False
                game.makeNewBackupFolder()
                game.print( " ")
            files.copyMenuToBackUp( game, fileScript)
            files.writeListToFile( fileScript, scriptLines)
            game.print( f"`navy`{lineCount:5}` replaces in [`bold`{fileScript}`]")
    game.print( f"`green`{fileCount:5}` files done.")


def main():
    pass


if __name__ == '__main__':
    main()
