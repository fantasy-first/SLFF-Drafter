from base64 import b64encode, b64decode
from typing import List, Optional


class EventInfo:
    def __init__(self, event_id: str, tba_key: str, team_list: List[str]):
        """
        Helper class to make passing data around a little bit easier.
        :param event_id: SLFF event id
        :param tba_key: TBA event key
        :param team_list: List of teams competing at the event
        """
        self.event_id = event_id
        self.tba_key = tba_key
        self.team_list = team_list

    def to_data(self) -> List[str]:
        """
        Converts the EventInfo instance to a list of data
        :return: a list representing the event info
        """
        comma_separated_teams = ','.join(self.team_list)

        # base 64 encode the team list so it's easier to handle CSVs when we don't know how many teams
        # will be at the event
        teams_b64 = b64encode(comma_separated_teams.encode()).decode()
        return [self.event_id, self.tba_key, teams_b64]

    def __str__(self):
        return ','.join(self.to_data())

    @staticmethod
    def team_list_from_b64(teams_b64: str) -> List[str]:
        """
        Takes a b64 encoded string and converts it to a team list
        :param teams_b64: team list encoded in base 64
        :return: list of teams represented by strings
        """
        decoded = b64decode(teams_b64).decode()
        return decoded.split(',')


class Pick:
    def __init__(self, time: Optional[str], randomed: Optional[bool], team: Optional[str]):
        """
        Helper class for DraftResults model.
        :param time: time of the pick (format t.b.d.)
        :param randomed: true if the pick was randomed to the player, false otherwise
        :param team: the actual team picked
        """
        self.time = time
        self.randomed = randomed
        self.team = team


class DraftResults:
    def __init__(self, player: str, event_id: str, tier: Optional[int], pick_number: Optional[int], picks: List[Pick]):
        """
        Helper class for storing draft results.
        :param player: player name
        :param event_id: SLFF event id
        :param tier: tier the player is in
        :param pick_number: specifies pick order (e.g. 1, 2, 3, ... 9, 10, ...)
        :param picks: list of Picks that have been completed by the player (so size 0 to N)
        """
        self.player = player
        self.event_id = event_id
        self.tier = tier
        self.pick_number = pick_number
        self.picks = picks

        while len(self.picks) != 3:
            self.picks.append(Pick(None, None, None))

    def to_data(self) -> List[Optional[str]]:
        """
        Converts object to data needed to post to the sheet.
        :return: a list representing the draft results
        """
        ret = [self.player, self.event_id, self.tier, self.pick_number]
        for pick in self.picks:
            ret.extend([pick.time, pick.randomed, pick.team])

        return ret


class Registration:
    def __init__(self, event_id: str, message_id: str, player_list: List[str]):
        """
        Class to hold draft registration data
        :param event_id: SLFF event id
        :param message_id: bot's message ID that people react to in order to sign up
        :param player_list: list of player IDs that are signed up for the draft
        """
        self.event_id = event_id
        self.message_id = message_id
        self.player_list = player_list

    def to_data(self) -> List[Optional[str]]:
        """
        Converts object to data needed to post to the sheet.
        :return: a list representing registration data
        """
        players = ','.join(self.player_list)

        # base 64 encode the player list so it's easier to handle CSVs when we don't know how many players
        # will drafting the event
        teams_b64 = b64encode(players.encode()).decode()
        return [self.event_id, self.message_id, teams_b64]

    @staticmethod
    def player_list_from_b64(players_b64: str) -> List[str]:
        """
        Helper class to convert from/to b64
        :param players_b64: the b64 encoded comma-separated player list
        :return: a list of player IDs
        """
        if players_b64 == '':
            return []

        decoded = b64decode(players_b64).decode()
        return decoded.split(',')
