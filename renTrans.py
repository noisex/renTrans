from settings import settings


class RenTrans:
    _init = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if self._init:
            return
        self._init = self.instance

        self.settings = settings
        self.game = {
            'gameName'      : None,
            'folderGames'   : None,
            'folderGame'    : None,
            'folderLIBs'    : None,
            'folderWork'    : None,
            'folderTL'      : None,
            'folderTemp'    : None,
            'folderTrans'   : None,
            'folderDone'    : None,
            'folderSDK'     : None,
        }
