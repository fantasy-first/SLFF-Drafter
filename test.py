from wrappers.sheets import models
from wrappers.sheets.api import Spreadsheet
from wrappers.firstelastic import FRCES
from dynaconf import settings

assert(settings.DISCORD.TOKEN is not None)
assert(settings.DISCORD.TITLE_COLOR == 0xe8850d)
assert(settings.TBA.API_KEY == "9qTowkNEd3IarS0iDGB40d6Gqi4YJDlosHiLeLypQ3XfAEFeBp0bIYSqcBqB3fHb")
print("Should be a thumbs up:", settings.DISCORD.REGISTER_EMOJI)

es = FRCES(2019)
assert(len(es.get_event_teams('2019vabla')) == 34)

spreadsheet = Spreadsheet(settings.DRAFT.DATA_STORE_SPREADSHEET_ID)
print(spreadsheet.event_info.contains_event('foo'))
print(spreadsheet.event_info.contains_event('foo2'))
spreadsheet.event_info.set_event_info(models.EventInfo('foo', '2019nyro', ['2791', '340', '3015', '5254', '20']))
print(spreadsheet.event_info.get_event_info('foo'))
spreadsheet.draft_results.set_pick(models.DraftResults(
    'justin', 'foo', 1, 1, [models.Pick('8:30 PM', False, '254'), models.Pick('8:37 PM', True, '3044')]
))