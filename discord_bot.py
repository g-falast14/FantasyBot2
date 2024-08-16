# discord imports
import discord
from discord.ext import commands, tasks
# other imports
import fantasy
from fantasy import YahooLeague
import asyncio

# initialize league
league = YahooLeague()
# initialize bot
bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
with open('token') as file:
    token = file.read()


@bot.hybrid_command()
async def verify(ctx: commands.Context):
    email = ctx.message.content[len('!verify '):]

    try:
        await ctx.send('Verifying ' + email)
    except Exception as e:
        await ctx.send('You need to include your Yahoo ID!')

    # check if id is valid
    if email not in league.tms:
        await ctx.send('Please enter a valid email and try again')
        return

    # if id is valid, update key with discord id
    # store old value
    temp = league.tms[email]
    # update key
    league.tms[ctx.author.name] = temp

    await ctx.send(f'Successfully verified Discord user {ctx.author.name} with Yahoo user {email}')
    return

@bot.hybrid_command()
async def roster(ctx: commands.Context):
    # grab associated discord user
    user = league.tms[ctx.author.name]
    # print roster
    roster = user.roster()
    for player in roster:
        await ctx.send(f'{player['name']}, {player['eligible_positions']}', ephemeral=True)

@tasks.loop(minutes=1)
async def check_transactions():
    # trades_announcement channel id
    channel_id = 1272611448605904976
    curr_transaction = get_trade_info()
    # if transactions are different, output new trade
    if curr_transaction != league.prev_transaction:
        # reassign transaction
        league.prev_transaction = curr_transaction
        # get bot channel
        channel = bot.get_channel(channel_id)
        await channel.send('TRADE ALERT:')
     #   print('TRADE ALERT:')
        for key in curr_transaction:
            await channel.send(f'{key} trades {curr_transaction[key]}')
    await asyncio.sleep(60)

@bot.event
async def on_ready():
    print("fantasy bot is running")
    await bot.tree.sync()
    check_transactions.start()

def get_trade_info():
    # grab players dictionary, it's buried
    players = league.lg.transactions('trade', '2')[0]['players']
    # dict for storing player info with key as team name, value with list of players being traded
    announcement = {}
    idx = 0
    while idx < players['count']: # number of players is associated in dict with key 'count' and value as # of players
        player_name = players[str(idx)]['player'][0][2]['name']['full']
        owner = players[str(idx)]['player'][1]['transaction_data'][0]['source_team_name']
        # check if owner name is already in dict
        if owner not in announcement:
            # add to new list with owner as key if not
            announcement[owner] = [player_name]
        else:
            # otherwise, append to corresponding list
            announcement[owner].append(player_name)
        idx += 1
    return announcement

# run bot
bot.run(token)


