from wrappers.sheets import models
from wrappers.sheets.api import Spreadsheet, DATA_STORE_SPREADSHEET_ID

spreadsheet = Spreadsheet(DATA_STORE_SPREADSHEET_ID)
print(spreadsheet.event_info.contains_event('foo'))
print(spreadsheet.event_info.contains_event('foo2'))

spreadsheet.event_info.set_event_info(models.EventInfo('foo', '2019nyro', ['2791', '340', '3015', '5254', '20']))

print(spreadsheet.event_info.get_event_info('foo'))
