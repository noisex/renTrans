# "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$",
# https://www.sublimetext.com/docs/build_systems.html#exec_options
import os
import re
import shutil
import threading
import subprocess
from datetime import datetime
from shutil import ignore_patterns  # copytree, rmtree

import filesClass as files
from guiClass import YoFrame
from settings import settings
from gameClass import GameRenpy
from tagsReplace import TagsClass
from fontTools.ttLib import TTFont
from menuFinder import menuFindVars
from transClass import Translator, RPAClass
from tlBackScript import backTLtoScriptClick
########################################################################################################################


app     = YoFrame()
game    = GameRenpy( app)
rpaArch = RPAClass(  app, game)
trans   = Translator(app)
tags    = TagsClass( game)
reTrans = re.compile( r'"(.+?)"')
# reTrans     = re.compile(r'(["])')
# reTrans     = re.compile(r'"(.*[a-zA-Z].*")(?:( \(.*\))?)')
# reTrans     = re.compile(r'"(.*[\w].*?)"')
# reTrans     = re.compile( r'"(.*?[A-Za-z].*?)"')
########################################################################################################################


def btnCopyTLStuff(event, old=None, new=None, updateList=True):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    if not old:
        old = f'{pathGame}tl\\rus\\'
    if not new:
        new = files.folderTL

    if os.path.exists( old):    # and os.path.exists( new):
        files.smartDirs( new)
        files.clearFolder( new, '*')
        shutil.copytree( old, new, dirs_exist_ok=True, ignore=ignore_patterns('*.rpyc', 'xxx_*', 'common.rpy', 'options.rpy', 'screens.rpy'))
        app.print( f'From [`bold`{old}`] copied to [`bold`{new}`].')
        if updateList:
            listFileStats( event)
    else:
        app.print( f'`red`ERROR:` folder [`bold`{old}`] not found. {os.path.exists( new)}')


def btnCopyFontsStuff(_event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    char = 1060
    # app.print( 'Start search non-rus fonts and replace them...', True)
    try:
        shutil.copytree( settings['folderGAME'], pathGame, dirs_exist_ok=True)
        app.print(f'Your game stuff from [`bold`{settings["folderGAME"]}`] copied.', True)
    except FileNotFoundError:
        app.print( f'`red`Error.` Folder [`bold`{settings["folderGAME"]}`] not found.', True)

    fileList = files.getFolderList(pathGame, '.ttf, .otf')

    for fileName, fileValue in fileList.items():
        font = TTFont( fileName)
        for cmap in font['cmap'].tables:
            if cmap.isUnicode():
                if char in cmap.cmap:
                    app.print( f"`green`Good RUS` font: [`bold`{fileValue['fileShort']}`]")
                else:
                    app.print( f"`navy`Badz ENG` font: [`bold`{fileValue['fileShort']}`]")
                    try:
                        files.copyMenuToBackUp( game, fileName, 'backupFonts')
                        shutil.copy2( pathGame + 'webfont.ttf', fileName)  # complete target filename given
                    except FileNotFoundError as error:
                        app.print( f'`red`Error.` `bold`{error}`')
                break


def getListFilesRPA():
    game.inArchiveRPY = 0
    game.inArchiveRPC = 0
    game.inArchiveTTF = 0
    pathGame    = game.getPathGame()

    if pathGame:
        fileList = files.getFolderList(pathGame, '.rpa', onlyRoot=True, silent=True)
        archFileList = rpaArch.rpaGetFilesStats( fileList)

        for archFile, archValues in archFileList.items():
            app.print( f'-=> [`bold`{archValues["size"]:7,.1f}` mb] [`bold`{archValues["count"]:6,}` files] in [`bold`{archFile}`]')
            game.inArchiveRPY += archValues["rpyFiles"]
            game.inArchiveRPC += archValues["rpycFiles"]
            game.inArchiveTTF += archValues["fontsFiles"]

        if game.inArchiveRPY + game.inArchiveRPC + game.inArchiveTTF > 0:
            app.print( "")

            if game.inArchiveRPY >= 1:
                app.print( f'[`red`{game.inArchiveRPY}`] `navy`RPY` files in achieves.')
            if game.inArchiveRPC >= 1:
                app.print( f'[`red`{game.inArchiveRPC}`] `navy`RPYC` files in achieves.')
            if game.inArchiveTTF >= 1:
                app.print( f'[`red`{game.inArchiveTTF}`] `bold`Fonts` files in archives.')


def listFileStats( _event, path=False, withTL=True, withStat=False, ext='.rpy'):
    if not path:
        path = files.folderTL
    fileList = files.getFolderList(path, ext=ext, withTL=withTL, withStat=withStat)
    app.listFileUpdate( fileList)
    if path == files.folderTL:
        tags.load( fileList)


def btnMakeTempFiles( _event):
    files.clearFolder( files.folderTEMP, '*')
    # files.clearFolder( files.folderIND, '*')
    app.print( 'Make temp files for translate.', True)

    fileList = files.getFolderList(files.folderTL, '.rpy', silent=True)

    for fileName in fileList:
        tempFileName    = files.folderTEMP + fileList[fileName]['fileShort']
        # indFileName     = files.folderIND + fileList[fileName]['fileShort']
        oList = []
        # iList = []
        skipLLines = 0

        fileText, _error = files.readFileToList( fileName)

        for line in fileText:
            if ( skipLLines <= 0) and ( r' "' in line):
                line = line.replace( r'\"', r"'")
                skipLLines = 3
                result = reTrans.findall( line)
                if len( result) > 0:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                    # if result is not None:                            # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                    # print( result.groups(), result.group(0))
                    # oList.append( result.group(1))
                    # print( len(result), result)
                    oList.append( result[ len( result) - 1])
                    # iList.append( str(ind))
            else:
                skipLLines -= 1
        files.writeListToFile( tempFileName, oList)
        # files.writeListToFile( indFileName, iList)

    app.pbTotal.pbReset()
    fileList = files.getFolderList( files.folderTEMP, ext='.rpy', withTL=True, withStat=True)
    totalLines, totalSizes, _, _, _ = getDicLastData( fileList)
    app.listFileUpdate(fileList)
    app.labelsSet(totalLines, totalSizes)
    # listFileStats( event, path=files.folderTEMP, withTL=True, withStat=True)


def getDicLastData( fileList: dict) -> tuple:
    totalLines = 0
    totalSizes = 0
    lastKey    = list(fileList.keys())[-1]

    if 'linesTotal' in fileList[lastKey]:
        totalLines = fileList[lastKey]['linesTotal']
    if 'sizeTotal' in fileList[lastKey]:
        totalSizes = fileList[lastKey]['sizeTotal']
    totalRPY   = fileList[lastKey]['totalRPY']
    totalRPYC  = fileList[lastKey]['totalRPYC']
    totalRPA   = fileList[lastKey]['totalRPA']
    return totalLines, totalSizes, totalRPY, totalRPYC, totalRPA


def btnMakeTransFilesThread():
    files.clearFolder( files.folderTRANS, '*')
    app.print( f'Translating from [`green`{app.lang.get()}`] to [`green`{app.trans.get()}`] language start...', True)

    fileList    = files.getFolderList(files.folderTEMP, '*', withStat=True, silent=True)
    totalLines,  totalSizes, _, _, _  = getDicLastData( fileList)
    totalFiles  = len( fileList)
    currentFile = currentLine = currentSize = 0

    app.listFileUpdate( fileList)
    app.labelsSet( totalLines, totalSizes)
    trans.listTransPrepare()

    for fileName, fileValue in fileList.items():
        app.listTLupdate( currentFile)
        currentFile += 1

        fileAllText, error = files.readFileToList( fileName)

        if not error:
            # print( totalLines, totalSizes, totalFiles, currentFile, fileValue['lines'], fileValue['size'], fileName)
            tList, error = trans.listTranslate( fileAllText, fileValue['fileShort'], tl=totalLines, ts=totalSizes, tf=totalFiles, cl=currentLine, cs=currentSize, cf=currentFile)
            currentLine += fileValue['lines']
            currentSize += fileValue['size']

            if not error:
                files.writeListToFile( files.folderTRANS + fileValue['fileShort'], tList)
            else:
                app.print( 'Error. Something going wrong...', lastLine=True)
                return
    # reset button state text
    app.print('Translation ake done complite.', lastLine=True)
    btnMakeTransFiles( False)
    app.listTLupdate( -1)


def btnMakeTransFiles(_event):
    # if app.btnTranslate['text'] == 'translate start':
    if ( 'trans' not in trans.threadSTOP) or ( not getattr( trans.threadSTOP['trans'], "do_run")):
        app.btnTranslate['text'] = 'translate stop'
        trans.threadSTOP['trans'] = threading.Thread(name='trans', target=btnMakeTransFilesThread, args=( ))
        trans.threadSTOP['trans'].do_run = True
        trans.threadSTOP['trans'].start()
    else:
        app.btnTranslate['text'] = 'translate start'
        # t = getThreadByName('trans') #Get thread by name
        trans.threadSTOP['trans'].do_run = False


def btnMakeRPYFiles(_event):
    app.print( 'compile renpy RPY files...', True)
    files.clearFolder( files.folderRPY, '*', )
    game.wordDicCount = 0

    fileList = files.getFolderList(files.folderTRANS, '.rpy', silent=True)

    for fileName in fileList:

        fileNameTrans   = files.folderTRANS + fileList[fileName]['fileShort']
        fileNameDone    = files.folderRPY   + fileList[fileName]['fileShort']
        fileNameOrig    = files.folderTL    + fileList[fileName]['fileShort']

        linesTranslated, _error = files.readFileToList( fileNameTrans)
        linesOriginal, _error   = files.readFileToList( fileNameOrig)

        skipLLines = 0
        tIND = 0

        for oIND, line in enumerate( linesOriginal):

            if (skipLLines <= 0) and (r' "' in line):
                skipLLines = 3
                line = line.replace(r'\"', r"'")
                result = reTrans.findall(line)

                if len(result) > 0:  # если нашли строку с парой кавычек и это не переведенная строка ( не скип)
                    oLine = result[len(result) - 1]
                    tLine = linesTranslated[tIND]

                    tLine = game.correctOpenBrackets( tLine, oLine)
                    tLine = game.correctTranslate( tLine)
                    tLine = game.correctWordDic( tLine)
                    tLine = game.correctTagsBrackets( tLine, oLine)                                       # заменяем теги

                    if settings['engTRANS']:                                                 # если хочется иметь копию оригинальной строки внизу переведенной в игре
                        tLine += settings['engLine'] + oLine

                    # tempLine = linesOriginal[oIND+1]
                    tempLine = line.replace( oLine, tLine)
                    tempLine = tempLine.replace("    # ", "    ").replace("    old ", "    new ")

                    linesOriginal[oIND+1] = tempLine

                    tIND += 1

            else:
                skipLLines -= 1

        files.writeListToFile(fileNameDone, linesOriginal)
    app.print( f"wordDic replaced [`green`{game.wordDicCount}`] times.")


def runExternalCmd( path):
    app.print( '')
    if path and os.path.exists( path) and path.endswith( 'exe'):
        app.print( f'Start [`bold`{path}`]...')
        subprocess.call( f'"{path}"')
    else:
        app.print( f'Path not found: [{path}]')


def runThreadCmd( path):
    if path and os.path.exists( path):
        game.threadSTOP['run'] = threading.Thread( name='run', target=runExternalCmd, args=( path,))
        game.threadSTOP['run'].do_run = True
        game.threadSTOP['run'].start()


def btnRunGameClick( _event):
    pathGame = game.getPath()
    if not pathGame:
        return
    # arr_txt = [x for x in os.listdir() if x.endswith(".txt")]
    exeName = os.listdir( pathGame)
    exeName = sorted( list( filter(lambda fileName: fileName.endswith('.exe'), exeName)))[-1]

    if exeName and len( exeName) > 1:
        runThreadCmd( f'{pathGame}{exeName}')


def btnRunSDKClick( _event):
    if game.getPathGame():
        if os.path.exists( game.gameTLRUS):
            app.askClearFolder(game.gameTLRUS, f"Clear folder before run SDK? [{game.gameTLRUS}]")

    if not os.path.exists( f"{files.folderSDK}\\renpy.exe"):
        app.print( f"SDK exe not found [{files.folderSDK}\\renpy.exe]", lastLine=True)
    elif not os.path.exists( f"{files.folderSDK}"):
        app.print( f"SDK folder not found [{files.folderSDK}]. Check setting file or SDK folder.", lastLine=True)
    else:
        runThreadCmd( f'{files.folderSDK}renpy.exe')


def btnRPAExtractThread(pathGame):
    fileList = files.getFolderList(pathGame, '.rpa', onlyRoot=True)
    dicRPA = rpaArch.rpaGetListFilesExt( fileList)
    rpaArch.rpaExtractFiles( dicRPA, pathGame)


def btnRPAExtract(_event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    app.pbTotal.pbReset()
    game.threadSTOP['run'] = threading.Thread(name='run', target=btnRPAExtractThread, args=(pathGame,))
    game.threadSTOP['run'].do_run = True
    game.threadSTOP['run'].start()


# todo херня со четчиком гуд/бэд/еррор
def btnDecompileThread():
    if not game.pathPython:
        app.print( 'Python 2.7 in current folder not found!')
        return

    pathGame = game.getPathGame()
    if not pathGame:
        return

    app.pbTotal.pbSet()
    app.print( 'Start decompiling rpyc files..', True)

    good = 0
    bad = 0
    percent = 0
    filesRPY = files.getFolderList(pathGame, '.rpyc')
    filesTotal = len( filesRPY)

    if app.varDecompile.get():
        varDeco = '"unrpyc01.py"'
    else:
        varDeco = '"unrpyc00.py"'

    for fileCurrent, fileName in enumerate( filesRPY, 1):
        cmd = f'"{game.pathPython}" -O -E {varDeco} -c --init-offset "{fileName}"'  # -l "rus" -T "{fileName}.trans"'
        # print( cmd)  #{files.rootPath}
        p = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  #, cwd= f'{game.gameFolder}!renpy-7.3.5-sdk\\')
        out, _err = p.communicate()
        out = out.decode('UTF-8')
        # print( out, _err)

        result = out.split('\n')
        for line in result:
            if line == '1\r':
                good += 1
            elif line == '0\r':
                bad += 1
            elif len( line) > 3:
                percent = ( fileCurrent / filesTotal) * 100
                app.print( f'`rain{ round( percent)}`{line}`')
        app.pbTotal.pbSet( percent, f'{fileCurrent}/{filesTotal}')
    app.print( f'Decompiling complete. [{good}] files done with [{bad}] errors.', False)


def btnDecompile( _event):
    pathGame = game.getPathGame()
    if not pathGame:
        return

    game.threadSTOP['rpy'] = threading.Thread(name='rpy', target=btnDecompileThread)  #, args=( filesRPY))
    game.threadSTOP['rpy'].start()


def btnCopyRPYBack( event):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    btnCopyTLStuff(event, old=files.folderRPY, new=f'{pathGame}tl\\rus\\', updateList=False)


def btnWordDicClick( _event=None):
    pathGame = game.getPathGame()
    if not pathGame:
        return
    app.print( "")
    fileList = files.getFolderList(pathGame, ['.txt', '.rpy', '.json'])  # + 'tl\\rus\\')
    game.wordDicCount = 0
    # print( fileList)
    for fileName in fileList:
        tempList = []
        wordCountLocal = game.wordDicCount
        fileLines, _error = files.readFileToList( fileName)
        for line in fileLines:
            line = game.correctWordDic(line)  # , fileList[fileName]['fileShort'])
            tempList.append( line)
        if game.wordDicCount != wordCountLocal:
            files.writeListToFile( fileName, tempList)
    app.print( f"wordDic replaced [`green`{game.wordDicCount}`] times.")


def listGamesDClick( _event):
    game.listGameDClick()
    app.gameNameLabelSet()

    fileList = files.getFolderList( game.getPathGame(), '*', silent=True)
    _, _, game.inFolderRPY, game.inFolderRPC, game.inFolderRPA = getDicLastData( fileList)

    colRPY  = "`red`" if game.inFolderRPY > 0 else "`black`"
    colRPYC = "`red`" if game.inFolderRPC > 0 else "`black`"
    colRPA  = "`red`" if game.inFolderRPA > 0 else "`black`"

    app.print( f'in folder: [{colRPY}{game.inFolderRPY}`] `navy`RPY` [{colRPYC}{game.inFolderRPC}`] `navy`RPYC` [{colRPA}{game.inFolderRPA}`] `navy`RPA` files.', lastLine=True)

    getListFilesRPA()
    game.setGameNameBlock()


# todo активировать 0й таб при копировании файлов в ТЛ
def tabOnChange( event):
    tabID = event.widget.index("current")
    if tabID == 0:
        return

    tabName     = event.widget.tab( tabID, "text")
    child       = app.tabList[tabName]['lb']
    folderName  = files.folderWork + tabName

    if child.lastScan < files.getFolderTime( folderName):
        fileList = files.getFolderList(folderName, '*', withStat=True, silent=True)
        app.listFileUpdate(fileList, lb=child)
        child.lastScan = datetime.today().timestamp()


#######################################################################################################


def main():
    files.makeNewDirs()
    game.gameListScan( app)

    fileList = files.getFolderList(files.folderTL, ext='.rpy', withTL=True, withStat=True)
    if len( fileList) > 0:
        totalLines, totalSizes, _, _, _ = getDicLastData(fileList)
        app.labelsSet(totalLines, totalSizes)

    app.listFileUpdate(fileList)
    tags.load( fileList)

    app.listGames.bind(     '<Double-1>',           listGamesDClick, add=True)
    app.btnGameRescan.bind( '<ButtonRelease-1>',    game.gameListScan)
    app.cbGameFolder.bind(  "<<ComboboxSelected>>", game.gameListScan)
    app.cbGamesSort.bind(   "<<ComboboxSelected>>", game.gameListScan)

    app.btnExtract.bind(    '<ButtonRelease-1>', btnRPAExtract)
    app.btnDecompile.bind(  '<ButtonRelease-1>', btnDecompile)
    app.btnRunRenpy.bind(   '<ButtonRelease-1>', btnRunSDKClick)
    app.btnFontsCopy.bind(  '<ButtonRelease-1>', btnCopyFontsStuff)
    app.btnMenuFinder.bind( '<ButtonRelease-1>', lambda event, _game=game: menuFindVars( event, _game))
    app.btnCopyTL.bind(     '<ButtonRelease-1>', btnCopyTLStuff)

    app.btnTLScan.bind(     '<ButtonRelease-1>', listFileStats)
    app.btnMakeTemp.bind(   '<ButtonRelease-1>', btnMakeTempFiles)
    app.btnTranslate.bind(  '<ButtonRelease-1>', btnMakeTransFiles)
    app.btnMakeRPY.bind(    '<ButtonRelease-1>', btnMakeRPYFiles)
    app.btnCopyRPY.bind(    '<ButtonRelease-1>', btnCopyRPYBack)
    app.btnRunGame.bind(    '<ButtonRelease-1>', btnRunGameClick)

    app.btnTagCopy.bind(    '<ButtonRelease-1>', tags.copyRight)
    app.btnTagClear.bind(   '<ButtonRelease-1>', app.tagsClear)
    app.btnTempRepl.bind(   '<ButtonRelease-1>', tags.replace)
    app.btnTagsSave.bind(   '<ButtonRelease-1>', tags.saveFile)
    app.btnTagsLoad.bind(   '<ButtonRelease-1>', tags.loadFile)

    app.chAllEcxt['command'] = getListFilesRPA

    app.filemenu.insert_command( 1, label="Find & Replace")
    app.filemenu.insert_command( 2, label="WordDIC replacer", command=btnWordDicClick)
    app.filemenu.insert_command( 3, label="backTL to script", command=lambda: backTLtoScriptClick( game))

    app.tabControl.bind("<<NotebookTabChanged>>", tabOnChange)
    app.mainloop()


if __name__ == "__main__":
    main()
