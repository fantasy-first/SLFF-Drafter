class Draft:
    
    nextIdNum = 1
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

    async def getPartcipantsFromReacts(self, ctx, register_emoji, bot_user_id):
        if self.joinMessageId is None:
            return None
        msgId = self.getJoinMessageId()
        msg = await ctx.fetch_message(msgId)
        participants = []
        for reaction in msg.reactions:
            if reaction.emoji == register_emoji:
                async for user in reaction.users():
                    if user.id != bot_user_id:
                        participants.append(user.id)
        return participants

    @classmethod
    def getNewDraftKey(cls):
        draftKey = "off_{}".format(cls.nextIdNum)
        cls.nextIdNum += 1
        return draftKey