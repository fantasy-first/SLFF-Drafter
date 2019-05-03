class DraftState:
    BEFORE = 0
    DURING = 1
    AFTER = 2

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
        self.teamList = set()
        self.joinMessageId = None
        self.state = DraftState.BEFORE

    def getDraftKey(self):
        return self.draftKey

    def setJoinMessageId(self, joinMessageId):
        self.joinMessageId = joinMessageId

    def getJoinMessageId(self):
        return self.joinMessageId

    def addTeams(self, teamList):
        newTeams = set([self.parseTeam(t) for t in teamList])
        if None in newTeams:
            return False
        self.teamList |= newTeams
        return True 

    def getTeamList(self):
        sortedTeams = sorted(list(self.teamList))
        return [str(t[0])+t[1] for t in sortedTeams]

    @classmethod
    def parseTeam(cls, team):
        if team.isdigit():
            return (int(team), "")
        elif team[:-1].isdigit() and team[-1] in ["B", "C", "D", "E", "F"]:
            return (int(team[:-1]), team[-1:])
        else:
            return None

    @classmethod
    def getNewDraftKey(cls):
        draftKey = "off_{}".format(cls.nextIdNum)
        cls.nextIdNum += 1 # TODO write this to somewhere
        return draftKey