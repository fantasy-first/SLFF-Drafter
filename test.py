from wrappers.firstelastic import FRCES
from dynaconf import settings

from models.sheets import EventInfoRow, event_info, EventInfoSheet, DraftResultsSheet, DraftResultsRow

assert (settings.DISCORD.TOKEN is not None)
assert (settings.DISCORD.TITLE_COLOR == 0xe8850d)
assert (settings.TBA.API_KEY == "9qTowkNEd3IarS0iDGB40d6Gqi4YJDlosHiLeLypQ3XfAEFeBp0bIYSqcBqB3fHb")
print("Should be a thumbs up:", settings.DISCORD.REGISTER_EMOJI)

es = FRCES(2019)
assert (len(es.get_event_teams('2019vabla')) == 34)

# spreadsheet = Spreadsheet(settings.DRAFT.DATA_STORE_SPREADSHEET_ID)
# print(spreadsheet.event_info.contains_event('foo'))
# print(spreadsheet.event_info.contains_event('foo2'))
# spreadsheet.event_info.set_event_info(models.EventInfo('foo', '2019nyro', ['2791', '340', '3015', '5254', '20']))
# print(spreadsheet.event_info.get_event_info('foo'))
# spreadsheet.draft_results.set_pick(models.DraftResults(
#     'justin', 'foo', 1, 1, [models.Pick('8:30 PM', False, '254'), models.Pick('8:37 PM', True, '3044')]
# ))

# given the following sheet in gsheets
# row1: event_id, tba_key, teams_B64
# row2: foo, 2019nyro, asjuieofnasiluefh

# r = ExampleRow()
# r.event_id = 'foo'
# print(r.tba_key)  # prints 2019nyro
# r.tba_key = '2018nyro'
# r.save()  # commits 2018nyro to the sheet
# print(r.tba_key)  # prints 2018nyro

rows = event_info.get_all_rows()
print(rows[0].event_id, rows[0].tba_key, rows[0].teams_b64)
print(rows[1].event_id, rows[1].tba_key, rows[1].teams_b64)

print(rows)
print(EventInfoSheet().get_all_rows())

print(EventInfoRow(event_id='foo').tba_key)

new_row = DraftResultsRow(player='Justin', event_id='foo', pick_ids_b64=['64'])
new_row.save()

another = DraftResultsRow(player='Justin', event_id='foo')
print(another.pick_ids_b64)
another.pick_ids_b64 = ['254']
another.save()

third = DraftResultsRow(player='Justin', event_id='bar', pick_ids_b64=['330'])
third.save()

again = DraftResultsRow(player='Justin', event_id='foo')
print(again.pick_ids_b64)
