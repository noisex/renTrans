workFolder          = 'workFolder\\'  # noqa: E221

settings = {
    'TRLEN'         : 4950,  # 4700 for GoogleTranslate
    'testWait'      : 0.07,
    'engTRANS'      : False,
    'engLine'       : '\\n{i}{size=-5}{color=#999}',
    'itemSize'      : '{size=-5}{color=#777}',
    'gameFolder'    : 'D:\\AdGames\\',
    'gameFolderList': ['D:\\AdGames\\', 'E:\\!adgame done\\' ],
    'backupFolder'  : 'Backup',
    'folderList'    : ( 'tl', 'temp', 'ind', 'trans', 'tl_done'),
    'workFolder'    : workFolder,  # noqa: E203
    'folderTL'      : workFolder + 'tl\\',
    'folderTEMP'    : workFolder + 'temp\\',
    'folderIND'     : workFolder + 'ind\\',
    'folderTRANS'   : workFolder + 'trans\\',
    'folderRPY'     : workFolder + 'tl_done\\',  # noqa: E203
    'folderGAME'    : workFolder + 'game\\',  # noqa: E203
    'folderLOGS'    : 'logs\\',
    'folderSDK'     : 'renpy-sdk\\',
    'extension': [
        '.rpyc',
        '.rpy',
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
        'трахай'    : 'еби',
        'трахнул'   : 'выебал',
        'трахал'    : 'ебал',
        'трахнуть'  : 'выебать',
        'трахни'    : 'выеби',
        'трахну'    : 'выебу',
        'трахаешь'  : 'ебешь',
        'трахаешься': 'ебешься',
        'трахаетесь': 'ебетесь',
        'трахается' : 'ебется',
        'трахают'   : 'ебут',
        'трахает'   : 'ебет',
        'трахнули'  : 'выебали',
        'трахаться' : 'ебаться',
        'потрахаться' : 'поебаться',
        'олухи'     : 'сиськи',
        'олухами'   : 'сиськами',
        'щенки'     : 'сиськи',
        'задницу'   : 'жопу',
        'заднице'   : 'жопе',
        'попу'      : 'жопу',
        'попку'     : 'жопу',
        'попкой'    : 'жопой',
        'диплом'    : 'кончить',
        'перебирать': 'дрочить',
        'мастурбировать': 'дрочить',
        'мастурбирую'   : 'дрочу',
        'мастурбирует'  : 'дрочит',
        'мастурбируют'  : 'дрочат',
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
