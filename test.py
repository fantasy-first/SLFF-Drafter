from wrappers.sheets import models
from wrappers.sheets.api import Spreadsheet
from dynaconf import settings

spreadsheet = Spreadsheet(settings.DRAFT.DATA_STORE_SPREADSHEET_ID)
print(spreadsheet.event_info.contains_event('foo'))
print(spreadsheet.event_info.contains_event('foo2'))
spreadsheet.event_info.set_event_info(models.EventInfo('foo', '2019nyro', ['2791', '340', '3015', '5254', '20']))
print(spreadsheet.event_info.get_event_info('foo'))
spreadsheet.draft_results.set_pick(models.DraftResults(
    'justin', 'foo', 1, 1, [models.Pick('8:30 PM', False, '254'), models.Pick('8:37 PM', True, '3044')]
))