
import fantasy
from fantasy import YahooLeague

league = YahooLeague()
transactions = league.lg.transactions('trade', '2')[0]
print(transactions['picks'])

picks_dict = {}
for pick in transactions['picks']:
    pick_owner = pick['pick']['source_team_name']
    round = pick['pick']['round']
    print(f'pick owner: {pick_owner}, round: {round}')
    # check if picks_dict already contains list of owner associated picks
    if pick_owner not in picks_dict:
        temp = [round]
        picks_dict[pick_owner] = temp
    else:
        picks_dict[pick_owner].append(round)

print(transactions)

# print(transaction)
