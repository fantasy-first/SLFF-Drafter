import datetime
import random
from typing import List, Tuple, Set

import tabulate


class DraftState:
    BEFORE = 0
    DURING = 1
    AFTER = 2


class Draft:
    next_id_num = 1  # TODO read this from somewhere

    def __init__(self, name: str, reg_close_time: datetime.datetime, draft_begin_time: datetime.datetime):
        """
        @param name: a string representing a human-readable name for the event
        @param reg_close_time: a datetime object corresponding to the close of signups
        @param draft_begin_time: a datetime object corresponding to the first player's slot time
        """
        self.name = name
        self.reg_close_time = reg_close_time
        self.draft_begin_time = draft_begin_time
        self.draft_key = self.get_new_draft_key()
        self.team_list = set()
        self.player_list = set()
        self.join_message_id = None  # todo: add type
        self.state = DraftState.BEFORE
        self.event_key = None  # type: str
        self.time_slots = None  # todo: add type
        self.draft_order = None  # todo: add type

    """
    Methods for reading draft metadata
    """

    def get_name(self) -> str:
        return self.name

    def get_draft_key(self) -> str:
        return self.draft_key

    def get_event_key(self) -> str:
        return self.event_key

    def get_join_message_id(self):  # todo: add return type
        return self.join_message_id

    def get_draft_begin_time(self) -> datetime.datetime:
        return self.draft_begin_time

    def get_information(self) -> List[List[str]]:
        if self.state == DraftState.BEFORE:
            # TODO provide a preview with signed up players, the current team list, any other fun stats
            return []
        elif self.state == DraftState.DURING:
            # TODO instead of just showing time slots, show picks that have happened too
            table = []
            n_players = len(self.player_list)
            # table.append(["Player", "Pick 1", "Pick 2", "Pick 3"])
            for i, player in enumerate(self.player_list):
                first_pick_slot = self.time_slots[i].strftime("%H:%M")
                second_pick_slot = self.time_slots[2 * n_players - 1 - i].strftime("%H:%M")
                third_pick_slot = self.time_slots[2 * n_players + i].strftime("%H:%M")
                table.append([player, first_pick_slot, second_pick_slot, third_pick_slot])
            print(tabulate.tabulate(table))
            return table

    """
    Methods for writing draft metadata
    """

    def set_event_key(self, event_key: str):
        self.event_key = event_key

    def set_join_message_id(self, join_message_id):  # todo: add param type
        self.join_message_id = join_message_id

    def generate_draft_order(self):
        self.draft_order = list(self.player_list)
        random.shuffle(self.draft_order)

    def generate_time_slots(
            self,
            first_pick_time: int = 3,
            second_pick_time: int = 2,
            third_pick_time: int = 2):
        n_players = len(self.player_list)
        slots = [self.draft_begin_time]
        first_round_delta = datetime.timedelta(seconds=60 * first_pick_time)
        for i in range(n_players - 1):
            last_slot = slots[-1]
            slots.append(last_slot + first_round_delta)

        second_round_delta = datetime.timedelta(seconds=60 * second_pick_time)
        for i in range(n_players):
            last_slot = slots[-1]
            slots.append(last_slot + second_round_delta)

        third_round_delta = datetime.timedelta(seconds=60 * third_pick_time)
        for i in range(n_players):
            last_slot = slots[-1]
            slots.append(last_slot + third_round_delta)

        self.time_slots = slots

    def start(self):
        self.generate_draft_order()
        self.generate_time_slots()
        self.state = DraftState.DURING

    """
    Methods for reading/modifying the draft list of FRC teams
    """

    def add_teams(self, team_list: List[str]) -> bool:
        new_teams = set([self.parse_team(t) for t in team_list])
        if None in new_teams:
            return False
        self.team_list |= new_teams
        return True

    def remove_teams(self, team_list: List[str]) -> bool:
        rm_teams = set([self.parse_team(t) for t in team_list])
        if None in rm_teams:
            return False
        if len(rm_teams - self.team_list) > 0:
            return False
        self.team_list -= rm_teams
        return True

    def get_team_list(self):
        sorted_teams = sorted(list(self.team_list))
        return [str(t[0]) + t[1] for t in sorted_teams]

    """
    Methods for reading/modifying the list of players participating
    """

    def set_players(self, player_list: Set[str]):
        self.player_list = set(player_list)

    def get_players(self) -> Set[str]:
        return self.player_list

    """
    Static utilities for various draft operations
    """

    @classmethod
    def parse_team(cls, team: str) -> Tuple[int, str]:
        if team.isdigit():
            return int(team), ""
        elif team[:-1].isdigit() and team[-1] in ["B", "C", "D", "E", "F"]:
            return int(team[:-1]), team[-1:]
        else:
            raise ValueError(f'Unable to parse a team from {team}')

    @classmethod
    def get_new_draft_key(cls) -> str:
        draft_key = "off_{}".format(cls.next_id_num)
        cls.next_id_num += 1  # TODO write this to somewhere
        return draft_key


if __name__ == "__main__":
    start = datetime.datetime.strptime("2019-05-02 18:00", '%Y-%m-%d %H:%M')
    reg_close = datetime.datetime.strptime("2019-05-02 12:00", '%Y-%m-%d %H:%M')
    draft = Draft("Test Draft", reg_close, start)
    draft.set_players({"Brian_Maher", "pchild", "BrennanB", "jtrv", "jlmcmchl", "tmpoles", "saikiranra", "TDav540"})
    draft.add_teams([str(i) for i in range(1, 31)])
    draft.start()
    print(tabulate.tabulate(draft.get_information()))
