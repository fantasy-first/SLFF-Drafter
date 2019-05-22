from base64 import b64encode, b64decode
from typing import List


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
