# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 16:26:35 2020

@author: penko
"""

'''
# packages used in this function
import requests
import numpy as np
import pandas as pd
'''

def getPlayerSeasonStats(years = [2019], player_ids = [], team_abbr = []):
    
    if not isinstance(years, list):
        years = [years]
        
    if not isinstance(player_ids, list):
        player_ids = [player_ids]

    # Team filter functionality removed due to bug in OWL API
    '''  
    if not isinstance(team_abbr, list):
        team_abbr = [team_abbr]
    
    team_data = getTeams()
    if not np.all([ t in list(team_data['abbr_name']) for t in team_abbr ]):
        print("Error: All team abbreviations must be valid teams. Use getTeams() if you need a list of possible team abbreviations.")
    '''

    if not all([(y in [2018,2019]) for y in years]):
        print('Error: Years must be 2018, 2019, or both.')
        return None
    
    
    result = pd.DataFrame()
    
    for y in years:
        s_stats = requests.get("https://api.overwatchleague.com/stats/players?seasonId="+str(y))
    
        if s_stats.status_code != 200:
            print('Failed')
            continue
        
        ss_json = s_stats.json()
        
        # Cache of historical players made on Jan 13, 2020 due to long run time of getHistoricalPlayers()
        #hist_players = pd.read_pickle("./hist_01132020.pkl")
        
        # So the p['teamId'] in this API return is for the player's CURRENT
        # team, which is less than helpful for players who have changed teams.
        # Since calling getHistoricalPlayers is very time-intensive, I will
        # just take out the team values for now,
        # and you can merge the team data later as you see fit.
        # Fortunately, getPlayerMatchStats() does not have this problem.
        ss_df = pd.DataFrame( [ { 
                "player_id": p['playerId'],
                "name": p['name'],
                #"team_id": p['teamId'],
                #"team_name": team_data[team_data['id'] == p['teamId']]['name'].iloc[0],
                #"team_abbr": team_data[team_data['id'] == p['teamId']]['abbr_name'].iloc[0],
                "role": p['role'],
                "elims_10min": p['eliminations_avg_per_10m'],
                "deaths_10m": p['deaths_avg_per_10m'],
                "hero_dmg_10m": p['hero_damage_avg_per_10m'],
                "healing_10m": p['healing_avg_per_10m'],
                "ults_earned_10m": p['ultimates_earned_avg_per_10m'],
                "final_blows_10m": p['final_blows_avg_per_10m'],
                "elims_total": p['eliminations_avg_per_10m']*(p['time_played_total']/10),
                "deaths_total": p['deaths_avg_per_10m']*(p['time_played_total']/10),
                "hero_dmg_total": p['hero_damage_avg_per_10m']*(p['time_played_total']/10),
                "healing_total": p['healing_avg_per_10m']*(p['time_played_total']/10),
                "ults_earned_total": p['ultimates_earned_avg_per_10m']*(p['time_played_total']/10),
                "final_blows_total": p['final_blows_avg_per_10m']*(p['time_played_total']/10),
                "time_played": p['time_played_total']
            } for p in ss_json['data'] ] )
        
        result = result.append(ss_df)
    
    if not result.empty:  
        # Team filter functionality removed due to bug in OWL API  
        #if len(team_abbr) > 0:
        #    result = result[result['team_abbr'].isin(team_abbr)]
        #    result.reset_index(inplace=True, drop=True)
        if len(player_ids) > 0:
            result = result[result['player_id'].isin(player_ids)]
        result.reset_index(inplace=True, drop=True)
    
    return result
