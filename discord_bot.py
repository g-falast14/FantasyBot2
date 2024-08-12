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
async def get_trades(ctx: commands.Context):
    await ctx.send('grabbing trades')
    try:
      trade = fantasy.update_trades()
    except Exception as e:
        print(e)
        return
    await ctx.send(f'TRADE ALERT: {trade}')
    print(trade)

# dictionary storing last transaction
prev_transaction = None
@tasks.loop(minutes=1)
async def check_transactions():
    try:
        # get most recent league transaction
        transaction = league.lg.transactions('trade', '1')
        if transaction != prev_transaction:
            # transactions are not the same, meaning a new trade has gone through
            trader1 = transaction['trader_team_name']
            trader2 = transaction['tradee team name']
            # check for picks
            # if 'picks' in transaction:
            #     # there were picks in the trade, needs to be formatted appropriately


    except Exception as e:
        print('transactions error')
        print(e)
    await asyncio.sleep(60)


@bot.event
async def on_ready():
    print("fantasy bot is running")
    await bot.tree.sync()
    check_transactions.start()


# run bot
bot.run(token)


