import discord
#import tbapy
from discord.ext import commands
from random import shuffle
from tabulate import tabulate
import datetime
from draft import Draft
import asyncio
from keys import DISCORD_TOKEN

BOT_USER_ID = 573557278695882762

REGISTER_EMOJI = u"\U0001F44D"

Client = discord.Client()
bot = commands.Bot(command_prefix=".")

#tba = tbapy.TBA('9qTowkNEd3IarS0iDGB40d6Gqi4YJDlosHiLeLypQ3XfAEFeBp0bIYSqcBqB3fHb')

nextIdNum = 1

# maps draftKey -> Draft
drafts = {}
# maps eventKey -> draftKey
eventKeys = {}

def getReadableDatetime(dt):
    return dt.strftime("%H:%M on %b %d, %Y")

@bot.event
async def on_ready():
    print("I am running as " + bot.user.name)


# TODO refactor
def time_math(hour, minute, additions, margin):
    if margin == 0:
        pass
    else:
        for j in range(0, additions):
            minute += margin
            if minute >= 60:
                hour += 1
                minute -= 60
        if minute < 10:
            string_minute = "0" + str(minute)
        else:
            string_minute = minute
    return (str(hour) + ":" + str(string_minute)), hour, minute

# TODO refactor
def setup_draft(start_hour, start_minute, players):
    number_of_teams = len(players)
    r2_stats = time_math(start_hour, start_minute, number_of_teams - 1, 3)
    r3_stats = time_math(r2_stats[1], r2_stats[2], number_of_teams + 1, 2)
    table = []

    i = 0
    for player in players:
        team_setup = [player, time_math(start_hour, start_minute, i, 3)[0],
                      time_math(r2_stats[1], r2_stats[2], (number_of_teams - i), 2)[0],
                      time_math(r3_stats[1], r3_stats[2], i, 2)[0]]
        table.append(team_setup)
        i += 1
    return table


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
@bot.command(pass_context=True)
async def init(ctx, event_name, draft_date, reg_close_time, draft_begin_time):
    try:
        reg_close = "{} {}".format(draft_date, reg_close_time)
        reg_close_time_dt = datetime.datetime.strptime(
            reg_close, '%Y-%m-%d %H:%M')
    except ValueError:
        embed = discord.Embed(color=0xe8850d, title="ERROR in `init`")
        embed.add_field(
            name='Invalid date or time for registration close', 
            value="Please check your date and/or time to close registration and try again", 
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    try:
        draft_begin = "{} {}".format(draft_date, draft_begin_time)
        draft_begin_time_dt = datetime.datetime.strptime(
            draft_begin, '%Y-%m-%d %H:%M')
    except ValueError:
        embed = discord.Embed(color=0xe8850d, title="ERROR in `init`")
        embed.add_field(
            name='Invalid date or time for draft beginning', 
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

    draftKey = draft.getDraftKey()
    
    readable_reg_close_time = getReadableDatetime(reg_close_time_dt)
    readable_draft_begin_time = getReadableDatetime(draft_begin_time_dt)

    title_msg = 'Created draft for "{}" [id: {}]'.format(event_name, draftKey)
    
    embed = discord.Embed(color=0xe8850d, title=title_msg)
    embed.add_field(name='To register for this draft:', value='React to this message with {}'.format(REGISTER_EMOJI))
    embed.add_field(name='Registration closes at:', value=readable_reg_close_time, inline=False)
    embed.add_field(name='Draft starts at:', value=readable_draft_begin_time, inline=False)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/303583753022865408/539892100737531921/moon.png')

    sent = await ctx.send(embed=embed)

    draft.setJoinMessageId(sent.id)
    drafts[draftKey] = draft
    
    await sent.add_reaction(REGISTER_EMOJI)

    # TODO remove, this is for demo purposes
    #await asyncio.sleep(30)
    #partyPeople = await get_partcipants_from_reacts(ctx, draft)
    #print(partyPeople)    

@bot.command(pass_context=True)
async def addteams(ctx, draftKey, *args):
    if draftKey not in drafts:
        embed = discord.Embed(color=0xe8850d, title="ERROR in `.addteams`")
        embed.add_field(
            name='Invalid draft key', 
            value="Please check your draft key and try again", 
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    if not drafts[draftKey].addTeams(args):
        embed = discord.Embed(color=0xe8850d, title="ERROR in `.addteams`")
        embed.add_field(
            name='Invalid team number(s)', 
            value="Please check your team list and try again", 
            inline=False,
        )
        await ctx.send(embed=embed)
        return
    newTeams = ", ".join(str(t) for t in args)
    teamList = ", ".join(drafts[draftKey].getTeamList())
    embed = discord.Embed(color=0xe8850d, title="Successfully added to team list for [{}]".format(draftKey))
    embed.add_field(
        name='Added {}'.format(newTeams), 
        value="New team list: {}".format(teamList), 
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def start(ctx, event_name, *args):
    """Initialize a Draft"""

    # Check if there is an event key
    event_data = tba.event(args[0])
    try:
        error_testing = event_data['Errors']
        event_key = None
    except:
        event_key = args[0]
        

    # Set event name
    if event_key is None:
        # Find team list
        team_list = []
    else:
        event_name = event_data['name']



    table = setup_draft(8, 0, args)
    attending_teams_data = tba.event_teams(event_key)
    attending_teams = []
    for team in attending_teams_data:  # Get team list
        attending_teams.append(team['key'][3:])
    attending_teams.sort(key=lambda t: int(t))
    attending_teams_string = ' '.join([str(t).rjust(4) for t in attending_teams])
    random_list = attending_teams
    shuffle(random_list)

    headers = ["SLFF Team", "1st Pick", "2nd Pick", "3rd Pick"]

    embed = discord.Embed(color=0xe8850d, title=event_name)
    embed.add_field(name='Picks', value="```" + tabulate(table, headers, tablefmt="presto") + "```",
                    inline=True)

    embed.add_field(name='Available Teams', value="```" + attending_teams_string + "```", inline=False)
    await ctx.send(embed=embed)

    random_list_string = ""
    for team in random_list:
        random_list_string += team + "\n"

    randoms = discord.Embed(color=0xe8850d, title="Randoms for " + event_name)
    randoms.add_field(name='Randoms', value=random_list_string, inline=False)
    await ctx.send(embed=randoms)


@bot.command(pass_context=True)
async def waiver(ctx, mode, event_key, *args):
    """Ugly Testing"""

    if ctx.message.author.id == "118000175816900615":
        if mode.lower() == "create":
            pass

async def get_partcipants_from_reacts(ctx, draft):
    msgId = draft.getJoinMessageId()
    if msgId is None:
        return None
    msg = await ctx.fetch_message(msgId)
    participants = []
    for reaction in msg.reactions:
        if reaction.emoji == REGISTER_EMOJI:
            async for user in reaction.users():
                if user.id != BOT_USER_ID:
                    participants.append(user.id)
    return participants

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
