# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 16:26:35 2020

@author: penko

Return stats for each player within a certain season.

It seems the API does not return season stats for players who are no longer in
the league. So you can see Sinatraa's 2018 stats, but not xQc's.

Additionally, some team values are incorrect, so use them with caution.

"""

'''
# packages used in this function
import requests
import numpy as np
import pandas as pd
'''

def getPlayerSeasonStats(years = [2019], postseason = False, player_ids = [], team_abbr = []):
    
    if not isinstance(years, list):
        years = [years]
        
    if not isinstance(player_ids, list):
        player_ids = [player_ids]

 
    if not isinstance(team_abbr, list):
        team_abbr = [team_abbr]
        
    if len(team_abbr) > 0:
        print("Warning: For some seasons, several players are listed under the wrong team. As a result, filtering by using the team_abbr parameter may produce undesirable results. The most consistent season for team accuracy appears to be 2018.")
    
    team_data = getTeams()
    if not np.all([ t in list(team_data['abbr_name']) for t in team_abbr ]):
        print("Error: All team abbreviations must be valid teams. Use getTeams() if you need a list of possible team abbreviations.")
        

    if not all([(y in [2018,2019]) for y in years]):
        print('Error: Years must be 2018, 2019, or both.')
        return None
    
    if postseason not in [True, False]:
        print('Error: Postseason argument must be either True or False')
        return None
    
    
    result = pd.DataFrame()
    
    for y in years:
        if postseason == True:
            s_stats = requests.get("https://api.overwatchleague.com/stats/players?stage_id=postseason&season="+str(y))
        else:
            s_stats = requests.get("https://api.overwatchleague.com/stats/players?stage_id=regular_season&season="+str(y))
    
        if s_stats.status_code != 200:
            print('Failed')
            continue
        
        ss_json = s_stats.json()
        
        # Cache of historical players made on Jan 13, 2020 due to long run time of getHistoricalPlayers()
        #hist_players = pd.read_pickle("./hist_01132020.pkl")
        
        ss_df = pd.DataFrame( [ { 
                "player_id": p['playerId'],
                "name": p['name'],
                "season": y,
                "team_id": p['teamId'],
                "team_name": team_data[team_data['id'] == p['teamId']]['name'].iloc[0],
                "team_abbr": team_data[team_data['id'] == p['teamId']]['abbr_name'].iloc[0],
                "role": p['role'],
                "elims_10min": p['eliminations_avg_per_10m'],
                "deaths_10m": p['deaths_avg_per_10m'],
                "hero_dmg_10m": p['hero_damage_avg_per_10m'],
                "healing_10m": p['healing_avg_per_10m'],
                "ults_earned_10m": p['ultimates_earned_avg_per_10m'],
                "final_blows_10m": p['final_blows_avg_per_10m'],
                "elims_total": p['eliminations_avg_per_10m']*(p['time_played_total']/600),
                "deaths_total": p['deaths_avg_per_10m']*(p['time_played_total']/600),
                "hero_dmg_total": p['hero_damage_avg_per_10m']*(p['time_played_total']/600),
                "healing_total": p['healing_avg_per_10m']*(p['time_played_total']/600),
                "ults_earned_total": p['ultimates_earned_avg_per_10m']*(p['time_played_total']/600),
                "final_blows_total": p['final_blows_avg_per_10m']*(p['time_played_total']/600),
                "time_played_min": p['time_played_total']/60
            } for p in ss_json['data'] ] )
        
        result = result.append(ss_df)
    
    if not result.empty:  
        if len(team_abbr) > 0:
            result = result[result['team_abbr'].isin(team_abbr)]
            result.reset_index(inplace=True, drop=True)
        if len(player_ids) > 0:
            result = result[result['player_id'].isin(player_ids)]
        result.reset_index(inplace=True, drop=True)
    
    return result
