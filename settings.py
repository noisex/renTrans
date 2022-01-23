workFolder          = 'workFolder\\'  # noqa: E221

settings = {
    'TRLEN'         : 4990,  # 4700 for GoogleTranslate
    'testWait'      : 0.1,
    'engTRANS'      : False,
    'engLine'       : '\\n{i}{size=-3}{color=#999}',
    'itemSize'      : '{size=-5}{color=#777}',
    'gameFolder'    : 'D:\\AdGames\\',
    'backupFolder'  : 'Backup',
    'workFolder'    : workFolder,  # noqa: E203
    'folderTL'      : workFolder + 'tl\\',
    'folderTEMP'    : workFolder + 'temp\\',
    'folderTRANS'   : workFolder + 'trans\\',
    'folderRPY'     : workFolder + 'tl_done\\',  # noqa: E203
    'folderSDK'     : 'renpy-sdk\\',
    'folderPython'  : 'lib\\windows-i686\\python.exe',

    'extension': [
        '.rpyc',
        '.ttf',
        '.otf'
    ],

    'fileSkip': [
        'gui.rpy',
        'common.rpy',
        'options.rpy',
        'screens.rpy',
        'xxx_transparent.rpy',
        'xxx_toggle_menu.rpy',
        'qFont.ttf',
        'webfont.ttf',
        'cormac.ttf'
    ],

    'wordDic': {
        'вереск'    : 'Хизер',
        'мед'       : 'милый',
        'медовый'   : 'милый',
        'членом'    : 'хуем',
        'члена'     : 'хуя',
        'члены'     : 'хуи',
        'члене'     : 'хуе',
        'член'      : 'хуй',
        'петух'     : 'хуй',
        'петуху'    : 'хую',
        'члену'     : 'хую',
        'киска'     : 'пизда',
        'киску'     : 'пизду',
        'киски'     : 'пизды',
        'киске'     : 'пизде',
        'киской'    : 'пиздой',
        'трахать'   : 'ебать',
        'трахаю'    : 'ебу',
        'трахнул'   : 'выебал',
        'трахал'    : 'ебал',
        'трахнуть'  : 'выебать',
        'трахни'    : 'выеби',
        'трахаешь'  : 'ебешь',
        'трахают'   : 'ебут',
        'трахнули'  : 'выебали',
        'трахаться' : 'ебаться',
        'олухи'     : 'сиськи',
        'щенки'     : 'сиськи',
        'задницу'   : 'жопу',
        'диплом'    : 'кончить',
        'перебирать': 'дрочить',
        'мастурбировать': 'дрочить',
        'мастурбирую'   : 'дрочу',
    },

    'encList': [
        # 'utf_8',
        # 'cp1251',
        # 'cp1252',

        'cp437',
        'CP866',
        'KOI8-R',
        'utf_8'
        # 'utf_16le',
        # 'utf_7',
        # 'bz2_codec',
        # 'hex_codec',
        # 'raw_unicode_escape',
        # 'string_escape',
        # 'undefined',
        # 'unicode_escape',
        # 'uu_codec',
        # 'zlib_codec'
    ],
}
