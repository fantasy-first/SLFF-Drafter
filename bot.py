import discord
import tbapy
from discord.ext import commands
from random import shuffle
from tabulate import tabulate

Client = discord.Client()
bot = commands.Bot(command_prefix=".")

tba = tbapy.TBA('9qTowkNEd3IarS0iDGB40d6Gqi4YJDlosHiLeLypQ3XfAEFeBp0bIYSqcBqB3fHb')


@bot.event
async def on_ready():
    print("I'm alive")
    print("I am running as " + bot.user.name)


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

@bot.command(pass_context=True)
async def init(ctx, event_name, reg_close_time, draft_begin_time):
    embed = discord.Embed(color=0xe8850d, title=event_name)
    embed.add_field(name='Registration closes at:', value=reg_close_time, inline=False)
    embed.add_field(name='Draft starts at:', value=draft_begin_time, inline=False)
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/303583753022865408/539892100737531921/moon.png')
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


bot.run("NTczNTU3Mjc4Njk1ODgyNzYy.XMsk7g.O87PcUymC7KpkfonklSJpe-ZjQQ")
