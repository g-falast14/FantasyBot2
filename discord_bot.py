# discord imports
import discord
from discord.ext import commands, tasks
# other imports
import fantasy
from fantasy import YahooLeague, YahooPlayer, YahooPick
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
       #print(f'{player['name']}, {player['eligible_positions']}')

@tasks.loop(minutes=1)
async def check_transactions():
    # trades_announcement channel id
    channel_id = 1272611448605904976
    curr_transaction = get_trade_info()
    curr_transaction_id = league.lg.transactions('trade', '2')[0]['transaction_key']
    # if transactions are different, output new trade
    if curr_transaction_id != league.prev_transaction_id:
        # reassign transaction
        league.prev_transaction_id = curr_transaction_id
        # get bot channel
        channel = bot.get_channel(channel_id)
      #  await channel.send('TRADE ALERT:')
        print('TRADE ALERT:')
        for key in curr_transaction: # key is owner name, val is list of player/pick objs
            owner_info = curr_transaction[key]
            print(f'{key} trades:')
            for item in owner_info:
                if item.type == 'Player':
                # await channel.send(f'{key} trades {curr_transaction[key]}')
                    print(f'{item.name}, ')
                elif item.type == 'Pick':
                    # item is a pick, print appropriately
                    if item == owner_info[-1]: # just to make sure commas line up if last pick in list
                        print(f'Round {item.round}')
                    else:
                        print(f'Round {item.round}, ')
    else:
        print('no new trades')
    await asyncio.sleep(60)

@bot.event
async def on_ready():
    print("fantasy bot is running")
    await bot.tree.sync()
    check_transactions.start()

def get_trade_info():
    transactions = league.lg.transactions('trade', '2')[0]
    players = transactions['players']
    # dict for storing player info with key as team name, value with list of players being traded
    announcement = {}
    idx = 0
    while idx < players['count']:  # number of players is associated in dict with key 'count' and value as # of players
        player_name = players[str(idx)]['player'][0][2]['name']['full']
        owner = players[str(idx)]['player'][1]['transaction_data'][0]['source_team_name']
        # create player object
        player_object = YahooPlayer(player_name, owner)
        # check if owner name is already in dict
        if owner not in announcement:
            # add to new list with owner as key if not
            announcement[owner] = [player_object]
        else:
            # otherwise, append to corresponding list
            announcement[owner].append(player_object)
        idx += 1

    # check for picks
    if 'picks' in transactions:
        for pick in transactions['picks']:
            # grab pick owner and round
            pick_owner = pick['pick']['source_team_name']
            round = pick['pick']['round']
            # create pick object
            temp_pick = YahooPick(round, pick_owner)
            # add to owner list in announcement
            announcement[pick_owner].append(temp_pick)

    return announcement

# run bot
bot.run(token)


