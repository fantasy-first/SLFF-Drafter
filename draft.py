import datetime

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
        self.playerList = set()
        self.joinMessageId = None
        self.state = DraftState.BEFORE
        self.eventKey = None


    """
        Methods for reading draft metadata
    """
    def getName(self):
        return self.name

    def getDraftKey(self):
        return self.draftKey

    def getEventKey(self):
        return self.eventKey

    def getJoinMessageId(self):
        return self.joinMessageId

    """
        Methods for writing draft metadata
    """

    def setEventKey(self, eventKey):
        self.eventKey = eventKey

    def setJoinMessageId(self, joinMessageId):
        self.joinMessageId = joinMessageId

    """
        Methods for reading/modifying the draft list of FRC teams
    """

    def addTeams(self, teamList):
        newTeams = set([self.parseTeam(t) for t in teamList])
        if None in newTeams:
            return False
        self.teamList |= newTeams
        return True 

    def removeTeams(self, teamList):
        rmTeams = set([self.parseTeam(t) for t in teamList])
        if None in rmTeams:
            return False
        if len(rmTeams - self.teamList) > 0:
            return False
        self.teamList -= rmTeams
        return True 

    def getTeamList(self):
        sortedTeams = sorted(list(self.teamList))
        return [str(t[0])+t[1] for t in sortedTeams]

    """
        Methods for reading/modifying the list of players participating
    """

    def setPlayers(self, playerList):
        self.playerList = set(playerList)

    def getPlayers(self, playerList):
        return self.playerList

    """
        Utilities for various draft operations
    """

    @classmethod
    def getDraftSlotTimes(
        cls, 
        draft_begin_time, 
        n_players, 
        first_pick_time = 3, 
        second_pick_time = 2, 
        third_pick_time = 2
    ):
        slots = [draft_begin_time]
        firstRoundDelta = datetime.timedelta(seconds = 60*first_pick_time)
        for i in range(n_players-1):
            lastSlot = slots[-1]
            slots.append(lastSlot + firstRoundDelta)

        secondRoundDelta = datetime.timedelta(seconds = 60*second_pick_time)
        for i in range(n_players):
            lastSlot = slots[-1]
            slots.append(lastSlot + secondRoundDelta)     

        thirdRoundDelta = datetime.timedelta(seconds = 60*third_pick_time)
        for i in range(n_players):
            lastSlot = slots[-1]
            slots.append(lastSlot + thirdRoundDelta)

        return slots

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

if __name__ == "__main__":
    print(Draft.getDraftSlotTimes(datetime.datetime.strptime("2019-05-02 18:00", '%Y-%m-%d %H:%M'), 8))