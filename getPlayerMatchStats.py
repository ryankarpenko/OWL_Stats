# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 19:08:41 2020

@author: penko

This function returns player stats for each map in the matches provided.
Match ids can be returned from the getSchedule() function, where you can
filter by team, stage, season, etc.

Note: The time_played element from the API is very inconsistent, so the variable
name itself is postfixed by "_bugged"

All stats such as elims, damage, etc. are totals for the map

The API for match stats does not return player names, along with a few
other useful pieces of information. But these can be easily joined/merged
on the ids (included here) with the help of other functions such as
getHistoricalPlayers(). But because that function takes so long to run, it is not
forced to run within getPlayerMatchStats().

"""

'''
# packages used in this function
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm, trange
'''

# The player match stats API call only returns player id's, not names.
# Due to the huge time difference between returning all current players and
# all historical players, the resulting DF is left with only player id's.
# If you want to get more player info, you can choose the appropriate player
# details function and join that with this DF
def getPlayerMatchStats(match_ids, map_no = [], player_ids = [], team_abbr = []):
        
    if not isinstance(match_ids, list):
        match_ids = [match_ids]
    
    if not isinstance(player_ids, list):
        player_ids = [player_ids]
        
    if not isinstance(team_abbr, list):
        team_abbr = [team_abbr]
    
    
    team_dat = getTeams()
    
    if not np.all([ t in list(team_dat['abbr_name']) for t in team_abbr ]):
        print("Error: All team abbreviations must be valid teams. Use getTeams() if you need a list of possible team abbreviations.")
    
    result = pd.DataFrame()
    
    for m in match_ids:
            
        match_info = requests.get('https://api.overwatchleague.com/matches/'+str(m))
        
        if match_info.status_code != 200:
            continue
        
        # Get number of games in match
        num_games = len(match_info.json()['games'])
        
        for g in tqdm(range(1,num_games+1)):
            print(str(g) + "/" + str(num_games+1))
            ms_stats = requests.get('https://api.overwatchleague.com/stats/matches/'+str(m)+'/maps/'+str(g))
                   
            if ms_stats.status_code != 200:
                continue
            
            ms_json = ms_stats.json()  
            
            ms_df = pd.DataFrame([{
                    "match_id": ms_json['esports_match_id'],
                    "game_id": ms_json['game_id'],
                    "game_num": ms_json['game_number'],
                    "season": ms_json['season_id'],
                    "map_guid": ms_json['map_id'],
                    "map_type": ms_json['map_type'],
                    "team_id": t['esports_team_id'],
                    "team_name": team_dat[team_dat['id'] == t['esports_team_id']]['name'].iloc[0],
                    "team_abbr": team_dat[team_dat['id'] == t['esports_team_id']]['abbr_name'].iloc[0],
                    "player_id": p['esports_player_id'],
                    "damage": next((item['value'] for item in p['stats'] if item['name'] == 'damage'), 0),
                    "elims": next((item['value'] for item in p['stats'] if item['name'] == 'eliminations'), 0),
                    "deaths": next((item['value'] for item in p['stats'] if item['name'] == 'deaths'), 0),
                    "healing": next((item['value'] for item in p['stats'] if item['name'] == 'healing'), 0),
                    "heroes_played": [ h['name'] for h in p['heroes'] ],
                    "time_played_sec_bugged": next((item['value'] for item in ms_json['stats'] if item['name'] == 'total_game_time'), 0)
                } for t in ms_json['teams'] for p in t['players'] ] )
            
            result = result.append(ms_df)
            
    if not result.empty:
        if len(team_abbr) > 0:
            result = result[result['team_abbr'].isin(team_abbr)]
            result.reset_index(inplace=True, drop=True)
        if len(player_ids) > 0:
            result = result[result['player_id'].isin(player_ids)]
        result.reset_index(inplace=True, drop=True)
            
    return result