import os.path
import pickle
from base64 import b64encode
from typing import Union, List

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Reference: https://developers.google.com/sheets/api/quickstart/python

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

DATA_STORE_SPREADSHEET_ID = '1rvjsDfInf9KWFUwwVjDwz2ZADeD_4Fx3LMmNws7exss'
CREDS_CACHE_FILENAME = 'token.pickle'
CREDENTIALS_JSON = 'credentials.json'


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

    @classmethod
    def get_range_from_cell(cls, wrapper: 'SheetsWrapper', spreadsheet_id: str, total_range: 'SheetRange',
                            cell_value, cell_index: int = 0) -> 'SheetRange':
        """
        Iterates through a sheet (across the total range of the sheet), searching for cell_value and returning
        the range that represents the single row containing that cell_value in the index cell_index. It is effectively
        just a lookup using cell_value as the primary key value.
        :param wrapper: the instance of the SheetsWrapper class needed for reading
        :param spreadsheet_id: the ID of the spreadsheet
        :param total_range: the total range of the sheet to check across
        :param cell_value: the value to search for
        :param cell_index: the index within the total_range to check against
        :return: the SheetRange object representing the row containing the cell_value
        """
        data = wrapper.read_sheet_range(spreadsheet_id, total_range)
        for i, row in enumerate(data[1:], start=2):
            if row[cell_index] == cell_value:
                srange = SheetRange(total_range.sheet_name, total_range.col_first, i, total_range.col_last, i)
                return srange

        # todo: how do we handle this?
        raise Exception(f'Unable to find {cell_value} in {total_range} (index {cell_index})')


class SheetsWrapper:
    EVENT_INFO_RANGE = SheetRange('EventInfo', 'A', None, 'C', None)

    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(CREDS_CACHE_FILENAME):
            with open(CREDS_CACHE_FILENAME, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
                creds = flow.run_local_server()

            # Save the credentials for next run
            with open(CREDS_CACHE_FILENAME, 'wb') as token:
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

    def update_sheet_range(self, spreadsheet_id: str, sheet_range: SheetRange, data: List[List[str]]):
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

    def event_in_event_info(self, event_id: str) -> bool:
        """
        Checks if the given event ID is already in the EventInfo sheet or not.
        :param event_id: SLFF event id
        :return: true if the event is in the EventInfo sheet, false otherwise
        """
        data = self.read_sheet_range(DATA_STORE_SPREADSHEET_ID, SheetsWrapper.EVENT_INFO_RANGE)
        for row in data[1:]:
            if row[0] == event_id:
                return True

        return False

    def set_event_info(self, event_id: str, tba_key: Union[str, None], team_list: List[str]):
        """
        Sets the event info in the EventInfo sheet. If the event_id is already in the sheet, update the information
        accordingly instead of appending a new row.
        :param event_id: SLFF event id
        :param tba_key: TBA event key
        :param team_list: the teams that are participating at the event
        """
        if self.event_in_event_info(event_id):
            return self.__update_event_info(event_id, tba_key, team_list)

        comma_separated_teams = ','.join(team_list)

        # base 64 encode the team list for 1. compression and 2. easier to handle CSVs when we don't know how many teams
        # will be at the event
        teams_encoded = b64encode(comma_separated_teams.encode())
        self.append_sheet_range(
            DATA_STORE_SPREADSHEET_ID, SheetsWrapper.EVENT_INFO_RANGE,
            [[event_id, tba_key, teams_encoded.decode()]]
        )

    def __update_event_info(self, event_id: str, tba_key: Union[str, None], team_list: List[str]):
        """
        Updates the event info in the sheet with the given information.
        :param event_id: SLFF event id
        :param tba_key: TBA event key
        :param team_list: the teams that are participating at the event
        """
        comma_separated_teams = ','.join(team_list)
        teams_encoded = b64encode(comma_separated_teams.encode())
        srange = SheetRange.get_range_from_cell(self, DATA_STORE_SPREADSHEET_ID, SheetsWrapper.EVENT_INFO_RANGE,
                                                event_id)

        self.update_sheet_range(
            DATA_STORE_SPREADSHEET_ID, srange,
            [[event_id, tba_key, teams_encoded.decode()]]
        )


if __name__ == '__main__':
    sw = SheetsWrapper()
    sw.set_event_info('foo', '2019nyro', ['2791', '340', '3015', '5254'])
    sw.set_event_info('foo', '2019nyro', ['2791', '340', '5254'])
