from typing import Type, List

from util.convert import b64_to_list, list_to_b64
from wrappers.sheets import AbstractWorksheet, AbstractRow, SheetRange


class EventInfoSheet(AbstractWorksheet):
    @property
    def row_class(self) -> Type[AbstractRow]:
        return EventInfoRow

    @property
    def headers(self):
        return ['event_id', 'tba_key', 'teams_b64']

    @property
    def sheet_range(self):
        return SheetRange('EventInfo', 'A', None, 'C', None)

    @property
    def name(self):
        return 'EventInfo'


event_info = EventInfoSheet()


class EventInfoRow(AbstractRow):
    @staticmethod
    def get_identifiers() -> List[str]:
        return ['event_id']

    @property
    def worksheet(self) -> AbstractWorksheet:
        return event_info

    def post_refresh(self):
        if type(self.teams_b64) is str:
            self.teams_b64 = b64_to_list(self.teams_b64)

    def pre_save(self):
        if type(self.teams_b64) is list:
            self.teams_b64 = list_to_b64(self.teams_b64)


class DraftResultsSheet(AbstractWorksheet):

    @property
    def headers(self):
        return ['player', 'event_id', 'pick_ids_b64']

    @property
    def sheet_range(self):
        return SheetRange('DraftResults', 'A', None, 'C', None)

    @property
    def name(self):
        return 'DraftResults'

    @property
    def row_class(self):
        return DraftResultsRow


draft_results = DraftResultsSheet()


class DraftResultsRow(AbstractRow):
    @property
    def worksheet(self) -> AbstractWorksheet:
        return draft_results

    @staticmethod
    def get_identifiers() -> List[str]:
        return ['player', 'event_id']

    def post_refresh(self):
        if type(self.pick_ids_b64) is str:
            self.pick_ids_b64 = b64_to_list(self.pick_ids_b64)

    def pre_save(self):
        if type(self.pick_ids_b64) is list:
            self.pick_ids_b64 = list_to_b64(self.pick_ids_b64)
