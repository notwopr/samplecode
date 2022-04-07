class BotParams():
    def __init__(self, botid, botname, botdesc, botfunc):
        self.botid = botid
        self.botname = botname
        self.botdesc = botdesc
        self.botpath = f'/{botid}'
        self.botrs = '/result'
        self.botfunc = botfunc
