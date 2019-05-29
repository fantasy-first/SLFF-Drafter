import inspect
import os
import pickle
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple, Optional, Dict

from dynaconf import settings
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class DataStatus(Enum):
    FRESH = 0
    MODIFIED = 1


class SheetRange:
    """
    Wrapper class that represents a sheet range, e.g. "EventInfo!A1:F50"
    """

    def __init__(self, sheet_name: str, col_first: str, row_first: Optional[int], col_last: str,
                 row_last: Optional[int]):
        self.sheet_name = sheet_name
        self.col_first = col_first
        self.col_last = col_last
        self.row_first = row_first
        self.row_last = row_last

    def __str__(self) -> str:
        cell1 = self.col_first + ('' if self.row_first is None else str(self.row_first))
        cell2 = self.col_last + ('' if self.row_last is None else str(self.row_last))
        return f'{self.sheet_name}!{cell1}:{cell2}'


class AbstractWorksheet(ABC):

    @property
    @abstractmethod
    def headers(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def sheet_range(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def row_class(self):
        raise NotImplementedError()

    def __init__(self):
        self.rows = []
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
                flow = InstalledAppFlow.from_client_secrets_file(settings.GOOGLE.CREDENTIALS_JSON,
                                                                 settings.GOOGLE.SCOPES)
                creds = flow.run_local_server()

            # Save the credentials for next run
            with open(settings.GOOGLE.CREDS_CACHE_FILENAME, 'wb') as token:
                pickle.dump(creds, token)

        # Build and store objects for future use
        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()

    def get_range_by_key_index_pairs(self, key_index_pairs: List[Tuple[str, str]]) -> SheetRange:
        data = self.read_sheet_range(settings.DRAFT.DATA_STORE_SPREADSHEET_ID, self.sheet_range)

        for i, row in enumerate(data, start=2):
            if all(row[field] == val for val, field in key_index_pairs):
                sr = SheetRange(self.name, self.sheet_range.col_first, i, self.sheet_range.col_last, i)
                return sr

        # todo: how do we handle this?
        raise Exception(f'Unable to find row in {self.sheet_range} (key-indices {key_index_pairs})')

    def get_range_by_key(self, key: str, index: str) -> SheetRange:
        """
        Retrieves the range representing a single row that contains a key in the given row index.
        :param key: value to search for
        :param index: index in the row to search for the value
        :return: a SheetRange representing a single row
        """
        return self.get_range_by_key_index_pairs([(key, index)])

    def read_sheet_range(self, spreadsheet_id: str, sheet_range: SheetRange) -> List[Dict[str, str]]:
        """
        Reads the sheet at the given range.
        :param spreadsheet_id: spreadsheet ID
        :param sheet_range: the range to read from
        :return: a list of lists containing data from the sheet
        """
        result = self.sheet.values().get(spreadsheetId=spreadsheet_id, range=str(sheet_range)).execute()
        values = result.get('values')  # todo: throw err? idk, handle
        ret = []

        if sheet_range.row_last is None:  # if we are grabbing the entire sheet
            index = 1  # skip the first row that contains header info
        else:  # otherwise
            index = 0  # just grab the whole thing

        # convert a list of strings to a dict, mapping headers to values
        for row in values[index:]:
            new_dict = {}
            for header, val in zip(self.headers, row):
                new_dict[header] = val

            ret.append(new_dict)

        return ret

    def append_sheet_range(self, spreadsheet_id: str, sheet_range: SheetRange, data: List[List[str]]):
        """
        Appends data to the sheet in the given range.
        todo: find out what happens if we try to append to a range that doesn't have any more cells available?
        :param spreadsheet_id: spreadsheet ID
        :param sheet_range: the range to append to
        :param data: the data to append to the sheet
        """
        body = {'values': data}
        self.sheet.values().append(
            spreadsheetId=spreadsheet_id, range=str(sheet_range),
            valueInputOption='RAW', body=body
        ).execute()
        # todo: log?

    def update_sheet_range(self, spreadsheet_id: str, sheet_range: SheetRange, data: List[List[Optional[str]]]):
        """
        Updates data in the given range of the sheet
        :param spreadsheet_id: spreadsheet ID
        :param sheet_range: the range to append to
        :param data: the data to update within the given range
        """
        body = {'values': data}
        self.sheet.values().update(
            spreadsheetId=spreadsheet_id, range=str(sheet_range),
            valueInputOption='RAW', body=body
        ).execute()
        # todo: log?

    def add_row(self, row: 'AbstractRow'):
        self.rows.append(row)

    def get_all_rows(self):
        # Get all data in the sheet
        entire_sheet = self.read_sheet_range(settings.DRAFT.DATA_STORE_SPREADSHEET_ID, self.sheet_range)
        ret = []
        # for each row of data in the sheet
        for sheet_row in entire_sheet:
            ret.append(self.row_class(  # instantiate a new Row class
                **{  # and use the headers for each row as arguments for the row class constructor
                    id_: sheet_row[id_] for id_ in self.headers
                }
                # for example, this would call EventInfo(event_id='foo'),
                # or DraftResults(player='Justin', draft_key='2019iri')
            ))
            if ret[-1] not in self.rows:
                self.rows.append(ret[-1])

        return ret


class AbstractRow(ABC):
    def __init__(self, **kwargs):
        self.__prop_tracker = {}
        for k, v in kwargs.items():
            setattr(self, k, v)
            self.__prop_tracker[k] = DataStatus.FRESH

    @property
    @abstractmethod
    def worksheet(self) -> AbstractWorksheet:
        pass

    def __setattr__(self, key, value):
        calling_method = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
        if calling_method != '__init__':
            self.__prop_tracker[key] = DataStatus.MODIFIED

        super().__setattr__(key, value)

    def __getattr__(self, item):
        if item not in self.__prop_tracker:
            self.refresh()

        return super().__getattribute__(item)

    def refresh(self):
        srange = self.get_sheet_range()
        data = self.worksheet.read_sheet_range(settings.DRAFT.DATA_STORE_SPREADSHEET_ID, srange)[0]
        for col_name, val in data.items():
            self.__setattr__(col_name, val)
            self.__prop_tracker[col_name] = DataStatus.FRESH

        self.post_refresh()

    def get_sheet_range(self) -> SheetRange:
        return self.worksheet.get_range_by_key_index_pairs([
            (getattr(self, identifier), identifier) for identifier in self.get_identifiers()
        ])

    def save(self):
        self.pre_save()

        try:
            sr = self.get_sheet_range()
            self.worksheet.update_sheet_range(settings.DRAFT.DATA_STORE_SPREADSHEET_ID, sr, [
                [getattr(self, v) for v in self.worksheet.headers]
            ])
        except Exception:  # todo: custom exception from get_sheet_range
            self.worksheet.append_sheet_range(
                settings.DRAFT.DATA_STORE_SPREADSHEET_ID,
                self.worksheet.sheet_range,
                [
                    [getattr(self, v) for v in self.worksheet.headers]
                ]
            )

    @staticmethod
    @abstractmethod
    def get_identifiers() -> List[str]:
        pass

    def post_refresh(self):
        pass

    def pre_save(self):
        pass

    def __eq__(self, other):
        return isinstance(other, AbstractRow) and all(
            [getattr(self, k) == getattr(other, k) for k in self.get_identifiers()])
