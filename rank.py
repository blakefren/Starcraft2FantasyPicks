# Read players, API key, and run API calls to Aligulac.

import json
import pandas as pd

from urllib import parse
from urllib import request


DEBUG = False
API_FILENAME = 'api.key'
API_KEY = None
PLAYER_IN_FILENAME = 'players.txt'
PLAYER_OUT_FILENAME = 'ranks.csv'
BASE_URL = 'http://aligulac.com/api/v1/'
NUM_PLAYERS_QUERY = 100  # Adjust as needed.
BEST_OF = 3


# Parse/store relevant player info.
class Player:
    def __init__(self, info={}):
        self.name = info['tag'].lower()
        self.ratings = info['current_rating']
        self.current_rating = self.ratings['rating']
        self.form = info['form']
        self.id = info['id']


# Parse/store relevant inference info.
class InferenceResults:
    def __init__(self, info={}):
        self.p1 = info['pla']['tag'].lower()
        self.p2 = info['plb']['tag'].lower()
        self.prob1 = info['proba']
        self.prob2 = info['probb']


# Return the Aligulac API key from api.key.
def read_api_key_file(fname=''):
    api_key = ''
    with open(fname, newline='') as f:
        api_key = f.read()
    return api_key
    

# Return a list of players from players.txt.
def read_player_file(fname=''):
    players_df = pd.read_csv(fname, header=None)
    return [s.lower() for s in players_df[0].values.tolist()]


# Call Aligulac API to get top NUM_PLAYERS_QUERY players
def get_top_player_data(players=[]):
    querystring = parse.urlencode({
        'current_rating__isnull': 'false',
        'current_rating__decay__lt': '4',
        'order_by': '-current_rating__rating',
        'limit': NUM_PLAYERS_QUERY,
        'apikey': API_KEY,
    })
    url = BASE_URL + 'player?' + querystring
    player_dict = {p: None for p in players}
    jdata = None
    with request.urlopen(url) as f:
        data = f.read().decode('utf-8')
        jdata = json.loads(data)
    for item in jdata['objects']:
        p = Player(item)
        if p.name not in player_dict: continue
        player_dict[p.name] = p
    return player_dict


def get_match_data(p1_id, p2_id):
    assert p1_id != p2_id
    querystring = parse.urlencode({
        'bo': BEST_OF,
        'apikey': API_KEY,
    })
    url = BASE_URL + f'predictmatch/{p1_id},{p2_id}/?' + querystring
    jdata = None
    with request.urlopen(url) as f:
        data = f.read().decode('utf-8')
        jdata = json.loads(data)
    return InferenceResults(jdata)


if __name__ == '__main__':
    # Get key, players, and player data.
    API_KEY = read_api_key_file(API_FILENAME)
    PLAYERS = read_player_file(PLAYER_IN_FILENAME)
    player_dict = get_top_player_data(PLAYERS)
    match_dict = {p: {} for p in PLAYERS}

    # Run inference on every player pair.
    for p1 in player_dict.keys():
        if player_dict[p1] is None: continue
        p1_id = player_dict[p1].id
        for p2 in player_dict.keys():
            if player_dict[p2] is None: continue
            p2_id = player_dict[p2].id
            if p1_id == p2_id:
                continue
            elif match_dict[p1].get(p2, False) or match_dict[p2].get(p1, False):
                continue
            ir = get_match_data(p1_id, p2_id)
            if DEBUG:
                print(f'Prob of {ir.p1} beating {ir.p2} in a Bo3: {round(ir.prob1, 3)}')
            match_dict[ir.p1][ir.p2] = round(ir.prob1, 3)
            match_dict[ir.p2][ir.p1] = round(ir.prob2, 3)

    # Format and save results.
    results_df = pd.DataFrame(data=match_dict)
    if DEBUG: print(results_df)
    results_df.median().sort_values(ascending=False).to_csv(PLAYER_OUT_FILENAME, header=['median_win_prob'], index_label='player')
