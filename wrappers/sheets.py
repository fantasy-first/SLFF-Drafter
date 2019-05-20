import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Reference: https://developers.google.com/sheets/api/quickstart/python

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

DATA_STORE_SPREADSHEET_ID = '1rvjsDfInf9KWFUwwVjDwz2ZADeD_4Fx3LMmNws7exss'
CREDS_CACHE_FILENAME = 'token.pickle'
CREDENTIALS_JSON = 'credentials.json'


class SheetsWrapper:
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

    def read_sheet_range(self, sheet: str, sheet_range: str):
        result = self.sheet.values().get(spreadsheetId=sheet, range=sheet_range).execute()
        values = result.get('values', [])  # if nothing, default to []; todo: throw err? idk, handle
        return values


if __name__ == '__main__':
    sw = SheetsWrapper()
    sw.read_sheet_range(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
