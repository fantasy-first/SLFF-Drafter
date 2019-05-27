import os.path
import pickle
from typing import Union, List, Tuple

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dynaconf import settings

from wrappers.sheets import models

# Reference: https://developers.google.com/sheets/api/quickstart/python\

class SheetRange:
    """
    Wrapper class that represents a sheet range, e.g. "EventInfo!A1:F50"
    """

    def __init__(self, sheet_name: str, col_first: str, row_first: Union[int, None], col_last: str,
                 row_last: Union[int, None]):
        self.sheet_name = sheet_name
        self.col_first = col_first
        self.col_last = col_last
        self.row_first = row_first
        self.row_last = row_last

    def __str__(self) -> str:
        cell1 = self.col_first + ('' if self.row_first is None else str(self.row_first))
        cell2 = self.col_last + ('' if self.row_last is None else str(self.row_last))
        return f'{self.sheet_name}!{cell1}:{cell2}'


class Sheet:
    def __init__(self, name: str, total_range: SheetRange, spreadsheet: 'Spreadsheet', headers: List[str]):
        """
        Wrapper class that represents a single Sheet within a larger Google Spreadsheet.
        :param name: name of the sheet (the tab at the bottom)
        :param total_range: the total range of all data in the sheet (e.g. "A:C")
        :param spreadsheet: the parent spreadsheet
        """
        self.name = name
        self.total_range = total_range
        self.spreadsheet = spreadsheet
        self.headers = headers

    def get_range_by_key_index_pairs(self, key_index_pairs: List[Tuple[str, str]]) -> SheetRange:
        data = self.read_range(self.total_range)
        for i, row in enumerate(data[1:], start=2):
            if all(row[i] == k for k, i in key_index_pairs):
                return SheetRange(self.name, self.total_range.col_first, i, self.total_range.col_last, i)

        # todo: how do we handle this?
        raise Exception(f'Unable to find row in {self.total_range} (key-indices {key_index_pairs})')

    def get_range_by_key(self, key: str, index: str) -> SheetRange:
        """
        Retrieves the range representing a single row that contains a key in the given row index.
        :param key: value to search for
        :param index: index in the row to search for the value
        :return: a SheetRange representing a single row
        """
        return self.get_range_by_key_index_pairs([(key, index)])

    def read_range(self, sheet_range: SheetRange = None) -> List[dict]:
        """
        Reads the given range and returns the equivalent data within the sheet
        :param sheet_range: range to read data from
        :return: data from the sheet within the given range
        """
        if sheet_range is None:
            sheet_range = self.total_range

        data = self.spreadsheet.wrapper.read_sheet_range(self.spreadsheet.spreadsheet_id, sheet_range)
        ret = []
        for row in data:
            ret.append({header: x for header, x in zip(self.headers, row)})

        return ret

    def append_row(self, single_row: List[str]):
        """
        Appends a single row to the sheet
        :param single_row: single row of data to append
        """
        self.spreadsheet.wrapper.append_sheet_range(
            self.spreadsheet.spreadsheet_id,
            self.total_range,
            [single_row]
        )

    def update_range(self, srange: SheetRange, data: List[List[Union[str, None]]]):
        """
        Updates the given range with the given data
        :param srange: the range to update with data
        :param data: the data to put in the given range
        """
        self.spreadsheet.wrapper.update_sheet_range(
            self.spreadsheet.spreadsheet_id,
            srange, data
        )


class EventInfoSheet(Sheet):
    """
    Implementation of Sheet according to the EventInfo sheet. This contains data relevant to an event itself. See
    models.EventInfo for more information.
    """

    def __init__(self, name: str, total_range: SheetRange, spreadsheet: 'Spreadsheet', headers: List[str]):
        super().__init__(name, total_range, spreadsheet, headers)

    def contains_event(self, event_id: str) -> bool:
        """
        Checks if the EventInfo sheet contains the given event
        :param event_id: SLFF event id
        :return: true if the event is in the sheet, false otherwise
        """
        try:
            self.get_range_by_key(event_id, 'event_id')
            return True
        except:
            return False

    def set_event_info(self, event_info: models.EventInfo):
        """
        Sets the event info in the sheet. Adds it if it is not already there.
        :param event_info: event info to add to the sheet
        """
        if self.contains_event(event_info.event_id):
            self.update_range(self.get_range_by_key(event_info.event_id, 'event_id'), [event_info.to_data()])

    def get_event_info(self, event_id: str) -> models.EventInfo:
        """
        Retrieves an EventInfo object from the sheet.
        :param event_id: SLFF event id
        :return: EventInfo instance representing the given event
        """
        if self.contains_event(event_id):
            data = self.read_range(self.get_range_by_key(event_id, 'event_id'))
            event_info = models.EventInfo(
                data[0]['event_id'], data[0]['tba_key'], models.EventInfo.team_list_from_b64(data[0]['teams_b64'])
            )
            return event_info
        else:
            # todo: handle?
            raise Exception('Event info not found')


class DraftResultsSheet(Sheet):
    """
    Implementation of Sheet according to the DraftResults sheet. This contains information relevant to draft results,
    such as picks and pick order. See models for more info.
    """

    def __init__(self, name: str, total_range: SheetRange, spreadsheet: 'Spreadsheet', headers: List[str]):
        super().__init__(name, total_range, spreadsheet, headers)

    def set_pick(self, draft_results: models.DraftResults):
        """
        Sets the pick for the player given the specified DraftResults object.
        :param draft_results: information containing a player's picks
        """
        if not self.contains_player_at_event(draft_results.player, draft_results.event_id):
            raise Exception(f'Unable to find player {draft_results.player} at event {draft_results.event_id} in db')

        srange = self.get_range_by_key_index_pairs(
            [(draft_results.player, 'player'), (draft_results.event_id, 'event_id')])
        data = draft_results.to_data()
        self.update_range(srange, [data])

    def contains_player_at_event(self, player: str, event_id: str):
        """
        Checks if the sheet has the player-event combination stored.
        :param player: player name
        :param event_id: SLFF event id
        :return: true if player-event is in the sheet, false otherwise
        """
        try:
            self.get_range_by_key_index_pairs([(player, 'player'), (event_id, 'event_id')])
            return True
        except:
            return False


# Todo: singleton
class Spreadsheet:
    def __init__(self, spreadsheet_id: str):
        """
        Class representing an entire Google Spreadsheet.
        :param spreadsheet_id: the id of the doc, located in the URL
        """
        self.wrapper = SheetsWrapper()
        self.spreadsheet_id = spreadsheet_id
        self.event_info = EventInfoSheet('EventInfo', SheetRange('EventInfo', 'A', None, 'C', None), self,
                                         ['event_id', 'tba_key', 'teams_b64'])

        draft_results_headers = ['player', 'event_id', 'tier', 'pick_number']
        for i in range(1, settings.DRAFT.MAX_ROUND_COUNT + 1):
            draft_results_headers.extend([f'pick{i}_time', f'pick{i}_randomed', f'pick{i}_team'])

        self.draft_results = DraftResultsSheet('DraftResults', SheetRange('DraftResults', 'A', None, 'M', None), self,
                                               draft_results_headers)


# todo: singleton
class SheetsWrapper:
    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(settings.GOOGLE.CREDS_CACHE_FILENAME):
            with open(settings.GOOGLE.CREDS_CACHE_FILENAME, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(settings.GOOGLE.CREDENTIALS_JSON, settings.GOOGLE.SCOPES)
                creds = flow.run_local_server()

            # Save the credentials for next run
            with open(settings.GOOGLE.CREDS_CACHE_FILENAME, 'wb') as token:
                pickle.dump(creds, token)

        # Build and store objects for future use
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        self.service = service  # I don't know what this object does
        self.sheet = sheet
        self.__creds = creds  # Do we need to store this?

    def read_sheet_range(self, spreadsheet_id: str, sheet_range: SheetRange) -> List[List[str]]:
        """
        Reads the sheet at the given range.
        :param spreadsheet_id: spreadsheet ID
        :param sheet_range: the range to read from
        :return: a list of lists containing data from the sheet
        """
        result = self.sheet.values().get(spreadsheetId=spreadsheet_id, range=str(sheet_range)).execute()
        values = result.get('values', [])  # if nothing, default to []; todo: throw err? idk, handle
        return values

    def append_sheet_range(self, spreadsheet_id: str, sheet_range: SheetRange, data: List[List[str]]):
        """
        Appends data to the sheet in the given range.
        todo: find out what happens if we try to append to a range that doesn't have any more cells available?
        :param spreadsheet_id: spreadsheet ID
        :param sheet_range: the range to append to
        :param data: the data to append to the sheet
        """
        body = {
            'values': data
        }
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=str(sheet_range),
            valueInputOption='RAW', body=body
        ).execute()
        # todo: log?

    def update_sheet_range(self, spreadsheet_id: str, sheet_range: SheetRange, data: List[List[Union[str, None]]]):
        """
        Updates data in the given range of the sheet
        :param spreadsheet_id: spreadsheet ID
        :param sheet_range: the range to append to
        :param data: the data to update within the given range
        """
        body = {
            'values': data
        }
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=str(sheet_range),
            valueInputOption='RAW', body=body
        ).execute()
        # todo: log?
