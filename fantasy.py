from yahoo_fantasy_api import Team
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

class YahooLeague:
    # lg = None
    # tms = {}
    # managers = {}
    def __init__(self):
        print("initializing league....")
        # connect to yahoo api
        sc = OAuth2(None, None, from_file="oauth2.json")
        # dictionary with emails originally stored as keys with team objects as values
        # the key gets replaced with the users discord username once they use the verify command
        self.tms = {}
        self.managers = {}
        # store transactions for updating purposes
        self.prev_transaction = None
        # get game object
        gm = yfa.Game(sc, 'nhl')
        # create league
        self.lg = gm.to_league('453.l.438')
        temp_teams = self.lg.teams()
        for key in self.lg.teams():
            # create team object
            team = Team(sc=sc, team_key=key)
            # grab email for verification
            user = temp_teams.get(key).get('managers')
            # for some reason you have to do this to access emails since the user list has 1 dictionary in it
            email = user[0]['manager'].get('email')
            # add email to team objects
            team.email = email
            # put in map with email and then team objects
            self.tms[email] = team
            # also store managers for later use
            self.managers[email] = user[0]['manager']

        print("league initialized!")
