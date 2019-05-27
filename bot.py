import datetime
from typing import Dict

import discord
from discord.ext import commands
from dynaconf import settings
from tabulate import tabulate

from models.draft import Draft
from wrappers.sheets.api import Spreadsheet

Client = discord.Client()
bot = commands.Bot(command_prefix=".")

spreadsheet = Spreadsheet(settings.DRAFT.DATA_STORE_SPREADSHEET_ID)

# tba = tbapy.TBA(settings.tba.api_key)

nextIdNum = 1

# maps draftKey -> Draft
drafts = {}  # type: Dict[str, Draft]
# maps eventKey -> draftKey
eventKeys = {}  # type: Dict[str, str]


def get_readable_datetime(dt: datetime.datetime) -> str:
    return dt.strftime("%I:%M %p (%Z) on %a %b %d, %Y")


@bot.event
async def on_ready():
    print("I am running as " + bot.user.name)


def get_draft(key: str) -> Draft:
    if key[:3] == "off":
        return drafts[key]
    elif key in eventKeys:
        return drafts[eventKeys[key]]
    else:
        raise ValueError(f'Unable to find draft for key {key}')


@bot.command()
async def ping(ctx):
    latency = bot.latency
    print(ctx)
    print('-------------------')
    await ctx.send(latency)


"""
    Initialize a new draft
    Usage: .init draft_name draft_date reg_close_time draft_begin_time
    Example: .init "MidKnight Mayhem" 2019-05-02 12:00 15:00
"""


# TODO fix this broken function
@bot.command(pass_context=True)
async def test(ctx):
    await init._callback(ctx, "MidKnight Mayhem", "2019-06-01", "2:30", "4:30")
    await set_players._callback(ctx, "off_1",
                                "Brian_Maher", "pchild", "BrennanB", "jtrv", "jlmcmchl", "tmpoles", "saikiranra",
                                "TDav540")
    await add_teams._callback(ctx, "off_1", *[str(i) for i in range(981, 1041)])
    await start._callback(ctx, "off_1")


@bot.command(pass_context=True)
async def init(ctx, event_name, draft_date, reg_close_time, draft_begin_time):
    try:
        reg_close = f'{draft_date} {reg_close_time} -0400'
        reg_close_time_dt = datetime.datetime.strptime(reg_close, '%Y-%m-%d %H:%M %z')
        reg_close_time_dt += datetime.timedelta(hours=12)
    except ValueError:
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="ERROR in `init`")
        embed.add_field(
            name=f'Invalid date or time for registration close ("{reg_close_time}")',
            value="Please check your date and/or time to close registration and try again",
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    try:
        draft_begin = f'{draft_date} {draft_begin_time} -0400'
        draft_begin_time_dt = datetime.datetime.strptime(draft_begin, '%Y-%m-%d %H:%M %z')
        draft_begin_time_dt += datetime.timedelta(hours=12)
    except ValueError:
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="ERROR in `init`")
        embed.add_field(
            name=f'Invalid date or time for draft begin ("{draft_begin_time}")',
            value="Please check your date and/or time to begin the draft and try again",
            inline=False,
        )
        await ctx.send(embed=embed)
        return

    # TODO prevent drafts from happening in the past
    draft = Draft(
        name=event_name,
        reg_close_time=reg_close_time_dt,
        draft_begin_time=draft_begin_time_dt,
    )

    draft_key = draft.get_draft_key()

    readable_reg_close_time = get_readable_datetime(reg_close_time_dt)
    readable_draft_begin_time = get_readable_datetime(draft_begin_time_dt)

    title_msg = f'Created draft for "{event_name}" [id: {draft_key}]'
    embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title=title_msg)
    embed.add_field(name='To register for this draft:',
                    value=f'React to this message with {settings.DISCORD.REGISTER_EMOJI}')
    embed.add_field(name='Registration closes at:', value=readable_reg_close_time, inline=False)
    embed.add_field(name='Draft starts at:', value=readable_draft_begin_time, inline=False)
    embed.set_thumbnail(url=settings.DISCORD.THUMBNAIL)

    sent = await ctx.send(embed=embed)

    draft.set_join_message_id(sent.id)
    drafts[draft_key] = draft

    await sent.add_reaction(settings.DISCORD.REGISTER_EMOJI)
    spreadsheet.registration.add_event(draft_key, str(sent.id))


@init.error
async def init_error(ctx, error):
    usage = '.init event_name draft_date reg_close_time draft_begin_time'
    example = '.init IRI 2019-05-30 7:00 8:00'

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Usage: `{usage}`\n'
                       f'Example: `{example}`')
    else:  # uhhh
        await ctx.send(f'err: {error} ({type(error)})')


@bot.command(pass_context=True)
async def add_teams(ctx, draft_key, *args):
    if draft_key not in drafts:
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="ERROR in `.addteams`")
        embed.add_field(
            name='Invalid draft key',
            value="Please check your draft key and try again",
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    if not drafts[draft_key].add_teams(args):
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="ERROR in `.addteams`")
        embed.add_field(
            name='Invalid team number(s)',
            value="Please check your team list and try again",
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    new_teams = ", ".join(str(t) for t in args)
    team_list = ", ".join(drafts[draft_key].get_team_list())
    embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title=f"Successfully updated [{draft_key}]")
    embed.add_field(
        name='Team List',
        value=f'{team_list}',
        inline=True,
    )
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def remove_teams(ctx, draft_key, *args):
    if draft_key not in drafts:
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="ERROR in `.removeteams`")
        embed.add_field(
            name='Invalid draft key',
            value="Please check your draft key and try again",
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    if not drafts[draft_key].remove_teams(args):
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="ERROR in `.removeteams`")
        embed.add_field(
            name='Invalid team number(s)',
            value="Please check your team list and try again",
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    newTeams = ", ".join(str(t) for t in args)
    teamList = ", ".join(drafts[draft_key].get_team_list())
    embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR,
                          title=f"Successfully removed from team list for [{draft_key}]")
    embed.add_field(
        name='Removed {}'.format(newTeams),
        value="New team list: {}".format(teamList),
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def set_key(ctx, draft_key, event_key):
    if draft_key in drafts:
        drafts[draft_key].set_event_key(event_key)
        name = drafts[draft_key].get_name()
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="TBA key for {} set".format(name))
        embed.add_field(
            name=f'TBA Key for {name} [{draft_key}] is now {event_key}',
            value=f"Either key can be used to reference {name}",
            inline=False,
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title="ERROR in `.setkey`")
        embed.add_field(
            name=f'No draft found with key [{draft_key}]',
            value="Please check your draft key and try again",
            inline=False,
        )
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def set_players(ctx, draftKey, *args):
    draft = get_draft(draftKey)
    draft.set_players(args)


@bot.command(pass_context=True)
async def start(ctx, draft_key: str):
    """Initialize a Draft"""

    # # Check if there is an event key
    # event_data = tba.event(args[0])
    # try:
    #     error_testing = event_data['Errors']
    #     event_key = None
    # except:
    #     event_key = args[0]

    # # Set event name
    # if event_key is None:
    #     # Find team list
    #     team_list = []
    # else:
    #     event_name = event_data['name']

    draft = get_draft(draft_key)
    participants = await get_participants_from_reacts(ctx, draft)
    users = [await bot.fetch_user(p) for p in participants]
    usernames = [u.name for u in users]

    # todo: check for race conditions with changing usernames?
    draft.set_players(usernames)
    # todo: should we add api stuff to the draft model or keep it here?
    spreadsheet.registration.add_batch_registration(draft_key, [str(p) for p in participants])

    draft.start()
    table = draft.get_information()
    # attending_teams_data = tba.event_teams(event_key)
    # attending_teams = []
    # for team in attending_teams_data:  # Get team list
    #     attending_teams.append(team['key'][3:])
    # attending_teams.sort(key=lambda t: int(t))
    # attending_teams_string = ' '.join([str(t).rjust(4) for t in attending_teams])
    # random_list = attending_teams
    # shuffle(random_list)

    headers = draft.get_table_header()

    event_name = draft.get_name()

    team_list = draft.get_team_square()

    embed = discord.Embed(color=settings.DISCORD.TITLE_COLOR, title=event_name)
    embed.add_field(name='Picks', value=f'```{tabulate(table, headers, tablefmt="presto")}```',
                    inline=True)
    embed.add_field(name='Available', value=f'```{tabulate(team_list)}```')

    # embed.add_field(name='Available Teams', value="```" + attending_teams_string + "```", inline=False)
    await ctx.send(embed=embed)

    # random_list_string = ""
    # for team in random_list:
    #     random_list_string += team + "\n"

    # randoms = discord.Embed(color=0xe8850d, title="Randoms for " + event_name)
    # randoms.add_field(name='Randoms', value=random_list_string, inline=False)
    # await ctx.send(embed=randoms)


@bot.command(pass_context=True)
async def waiver(ctx, mode, event_key, *args):
    """Ugly Testing"""

    if ctx.message.author.id == "118000175816900615":
        if mode.lower() == "create":
            pass


async def get_participants_from_reacts(ctx, draft: Draft):
    msg_id = draft.get_join_message_id()
    if msg_id is None:
        return None
    msg = await ctx.fetch_message(msg_id)
    participants = []
    for reaction in msg.reactions:
        if reaction.emoji == settings.DISCORD.REGISTER_EMOJI:
            async for user in reaction.users():
                if user.id != settings.DISCORD.BOT_USER_ID:
                    participants.append(user.id)
    return participants


# todo: refactor this into separate file
# note: need access to the bot object instance for that^ to work; some import magic needed
async def registration_background_task():
    await bot.wait_until_ready()


if __name__ == "__main__":
    bot.run(settings.DISCORD.TOKEN)
