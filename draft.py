class Draft:
    
    nextIdNum = 1 # TODO read this from somewhere
    """
        @param name: a string representing a human-readable name for the event
        @param reg_close_time: a datetime object corresponding to the close of signups
        @param draft_begin_time: a datimetime object corresponding to the first player's slot time
    """
    def __init__(self, name, reg_close_time, draft_begin_time):
        self.name = name
        self.reg_close_time = reg_close_time
        self.draft_begin_time = draft_begin_time
        self.draftKey = self.getNewDraftKey()
        self.teamList = []
        self.joinMessageId = None

    def getDraftKey(self):
        return self.draftKey

    def setJoinMessageId(self, joinMessageId):
        self.joinMessageId = joinMessageId

    def getJoinMessageId(self):
        return self.joinMessageId

    @classmethod
    def getNewDraftKey(cls):
        draftKey = "off_{}".format(cls.nextIdNum)
        cls.nextIdNum += 1 # TODO write this to somewhere
        return draftKey