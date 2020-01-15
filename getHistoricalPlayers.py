# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 19:51:23 2020

@author: penko
"""

'''
# packages used in this function
import requests
import pandas as pd
'''

# Get all players to have ever played in an OWL match
# This is pretty slow compared to getCurrentPlayers() because it has to loop
# through every match ever instead of just from the Players API call.
# So use it only if you need it.

# split_same_team_by_season = True means that if a player played for a team for multiple
#   seasons, all of those seasons will be shown separately. Otherwise
#   only the most recent season for that team will be shown.
# past_teams = True means that a player's former teams will be shown as well
def getHistoricalPlayers(split_same_team_by_season = False, past_teams = False):
    # So we can get team names, etc.
    t_list = getTeams()
    
    # So that we can tell which players are active
    curr = getCurrentPlayers()
    
    result = pd.DataFrame()
    
    # Add to result DF for each season
    for y in [2018,2019,2020]:
        all_m = requests.get("https://api.overwatchleague.com/matches?season="+str(y))
            
        if all_m.status_code != 200:
            continue
        
        print(y)
        
        mh_json = all_m.json()
         
        pl_df = pd.DataFrame( [ { 
                "id": pl['player']['id'],
                "name": pl['player']['name'],
                "hometown": pl['player']['homeLocation'] if 'homeLocation' in pl['player'].keys() else None,
                "given_name": pl['player']['givenName'] if "givenName" in pl['player'].keys() else None,
                "family_name": pl['player']['familyName'] if "familyName" in pl['player'].keys() else None,
                "nationality": pl['player']['nationality'] if "nationality" in pl['player'].keys() else None,
                "season": y,
                "team_id": pl['team']['id'] if ("team" in pl.keys() and "id" in pl['team'].keys()) else None,
                "team_name": t_list[t_list['id'] == pl['team']['id']]['name'].iloc[0] if len(t_list[t_list['id'] == pl['team']['id']]['name']) > 0 and "team" in pl.keys() and "id" in pl['team'].keys() else None,
                "team_abbr": t_list[t_list['id'] == pl['team']['id']]['abbr_name'].iloc[0] if len(t_list[t_list['id'] == pl['team']['id']]['name']) > 0 and "team" in pl.keys() and "id" in pl['team'].keys() else None,
                "headshot": pl['player']['headshot'] if "headshot" in pl['player'].keys() else None,
                "number": pl['player']['attributes']['player_number'] if "player_number" in pl['player']['attributes'].keys() else None,
                "role": pl['player']['attributes']['role'] if "role" in pl['player']['attributes'].keys() else None
            } for m in mh_json['content'] for mp in m['games'] for pl in mp['players'] if "players" in mp.keys() ] )
        
        result = result.append(pl_df, ignore_index=True)
        
    # Filter results based on parameters
    if split_same_team_by_season == True and past_teams == True:
        result.drop_duplicates(subset=['id','name','team_id','season'], inplace=True, keep='last')
        result.reset_index(inplace=True)
    elif split_same_team_by_season == True and past_teams == False:
        curTeams = result.drop_duplicates(subset=['id','name'], inplace=False, keep='last')
        result.drop_duplicates(subset=['id','name','team_id','season'], inplace=True, keep='last')
        result.reset_index(inplace=True)
        droplist = []
        for i, r in result.iterrows():
            if r['team_id'] != curTeams[curTeams['id']==r['id']]['team_id'].iloc[0]:
                droplist.append(i)
        result.drop(index = droplist, inplace = True)
    elif split_same_team_by_season == False and past_teams == True:
        result.drop_duplicates(subset=['id','name','team_id'], inplace=True, keep='last')
        result.reset_index(inplace=True)
    else: # split_same_team_by_season == False and past_teams == False
        result.drop_duplicates(subset=['id','name'], inplace=True, keep='last')
        result.reset_index(inplace=True)

    # Add column for active vs. inactive players. Based on list of current players in OWL db        
    result['active'] = [ "Active" if p in list(curr['id']) else "Inactive" for p in result['id'] ]
    
    return result
