renTransFolder      = 'c:\\RenTrans\\'
workFolder          = 'workFolder\\'

settings = {
    'TRLEN'         : 4950,  # 4700 for GoogleTranslate
    'testWait'      : 0.07,
    'engTRANS'      : False,
    'backupFolder'  : 'Backup',
    'engLine'       : '\\n{i}{size=-5}{color=#999}',
    'itemSize'      : '{size=-5}{color=#777} ',

    'folderList'    : ( 'tl', 'temp', 'trans', 'tl_done'),

    'folderLOGS'    : 'logs\\',
    'gameFolder'    :  'D:\\AdGames\\',
    'gameFolderList': ['D:\\AdGames\\', 'c:\\AdGames\\' ],

    'folderWORK'    : workFolder,
    'folderRENTRANS': renTransFolder,
    'folderGAME'    : f'{renTransFolder}game\\',
    'folderTAGS'    : f'{renTransFolder}tags\\',
    'folderSDK'     : f'{renTransFolder}renpy-sdk\\',
    'folderTL'      : f'{renTransFolder}{workFolder}tl\\',
    'folderTEMP'    : f'{renTransFolder}{workFolder}temp\\',
    'folderTRANS'   : f'{renTransFolder}{workFolder}trans\\',
    'folderRPY'     : f'{renTransFolder}{workFolder}tl_done\\',

    'extension': [
        '.rpyc',
        '.rpy',
        '.ttf',
        '.otf'
    ],

    'extracts': {
        'scripts' : [
            '.rpyc',
            '.rpy' ],
        'fonts' : [
            '.ttf',
            '.otf' ],
        'scripts+fonts' : [
            '.rpyc',
            '.rpy',
            '.ttf',
            '.otf'],
        'audio' : [
            '.wav',
            '.mp3',
            '.ogg' ],
        'images' : [
            '.gif',
            '.webp',
            '.jpeg',
            '.png',
            '.jpg' ],
        'video': [
            '.mp4',
            '.avi',
            '.mov',
            '.webm'],
        'images+video' : [
            '.gif',
            '.webp',
            '.jpeg',
            '.png',
            '.mp4',
            '.avi',
            '.mov',
            '.webm',
            '.jpg' ],
    },

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
        'трахаются' : 'ебутся',
        'потрахаться':'поебаться',
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
        'мастурбируешь' : 'дрочишь',
        'Ницца'         : 'классно',
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
