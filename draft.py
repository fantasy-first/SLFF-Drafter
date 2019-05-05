import datetime
import random
import tabulate

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
        self.timeSlots = None
        self.draftOrder = None

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

    def getDraftBeginTime(self):
        return self.draft_begin_time

    def getInformation(self):
        if self.state == DraftState.BEFORE:
            # TODO provide a preview with signed up players, the current team list, any other fun stats
            pass
        elif self.state == DraftState.DURING:
            # TODO instead of just showing time slots, show picks that have happened too
            table = []
            n_players = len(self.playerList)
            #table.append(["Player", "Pick 1", "Pick 2", "Pick 3"])
            for i, player in enumerate(self.playerList):
                firstPickSlot = self.timeSlots[i].strftime("%H:%M")
                secondPickSlot = self.timeSlots[2*n_players-1-i].strftime("%H:%M")
                thirdPickSlot = self.timeSlots[2*n_players+i].strftime("%H:%M")
                table.append([player, firstPickSlot, secondPickSlot, thirdPickSlot])
            print(tabulate.tabulate(table))
            return table

    """
        Methods for writing draft metadata
    """

    def setEventKey(self, eventKey):
        self.eventKey = eventKey

    def setJoinMessageId(self, joinMessageId):
        self.joinMessageId = joinMessageId

    def generateDraftOrder(self):
        self.draftOrder = list(self.playerList)
        random.shuffle(self.draftOrder)

    def generateTimeSlots(
        self,
        first_pick_time = 3, 
        second_pick_time = 2, 
        third_pick_time = 2,
    ):
        n_players = len(self.playerList)
        slots = [self.draft_begin_time]
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

        self.timeSlots = slots

    def start(self):
        self.generateDraftOrder()
        self.generateTimeSlots()
        self.state = DraftState.DURING

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
        Static utilities for various draft operations
    """

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
    start = datetime.datetime.strptime("2019-05-02 18:00", '%Y-%m-%d %H:%M')
    reg_close = datetime.datetime.strptime("2019-05-02 12:00", '%Y-%m-%d %H:%M')
    draft = Draft("Test Draft", reg_close, start)
    draft.setPlayers(["Brian_Maher", "pchild", "BrennanB", "jtrv", "jlmcmchl", "tmpoles", "saikiranra", "TDav540"])
    draft.addTeams([str(i) for i in range(1, 31)])
    draft.start()
    print(tabulate.tabulate(draft.getInformation()))