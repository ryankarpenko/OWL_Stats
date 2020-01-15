# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 15:43:11 2019

@author: penko
"""

'''
# packages used in this function
import requests
import pandas as pd
'''

# Returns all players listed as currently on a team in the OWL db
# For all players to have ever played in a match, use getHistoricalPlayers()
def getCurrentPlayers(team_abbr = []):
    
    if not isinstance(team_abbr, list):
        team_abbr = [team_abbr]
    
    # API call
    players = requests.get('https://api.overwatchleague.com/players')
    
    # Server error checking
    if players.status_code != 200:
        print("Error: Could not retrieve data from server. Code ", players.status_code, sep='')
        return None
    
    p_json = players.json()
    
    # There is really good player info within teams
    teams = requests.get('https://api.overwatchleague.com/v2/teams')
    
    if teams.status_code != 200:
        print("Error: Could not retrieve data from server. Code ", teams.status_code, sep='')
        return None

    t_json = teams.json()   
    
    # Player data from players table
    p_df1 = pd.DataFrame( [ {
            "id": p['id'],
            "name": p['name'],
            "hometown": p['homeLocation'] if 'homeLocation' in p.keys() else 'None',
            "given_name": p['givenName'],
            "family_name": p['familyName'],
            "nationality": p['nationality'],
            "team_id": p['teams'][0]['team']['id'],
            "team_name": p['teams'][0]['team']['name'],
            "team_abbr": p['teams'][0]['team']['abbreviatedName'],
            "headshot": p['headshot']
        } for p in p_json['content'] ] )
    
    # Player data from Teams table
    # Commented out lines are technically available in this DF but would be
    # redundant given the other data frame.
    # However we need to make this data frame because the Number and Role elements
    # are only available from the Teams table.
    p_df2 = pd.DataFrame( [ {
            "id": player['id'],
            #"name": player['name'],
            #"hometown": player['homeLocation'] if 'homeLocation' in player.keys() else 'None',
            #"given_name": player['givenName'],
            #"family_name": player['familyName'],
            #"nationality": player['nationality'],
            #"heroes": player['attributes']['heroes'],
            #"number": player['attributes']['player_number'],
            "number": player['number'] if player['number'] != "" else "-",
            #"preferred_slot": player['attributes']['preferred_slot'],
            #"role": player['attributes']['role']
            "role": player['role'] if player['role'] != "" else "-"
            #"team_id": team['id'],
            #"team_name": team['name'],
            #"team_abbr": team['abbreviatedName'],
            #"headshot": player['headshot']
        } for team in t_json['data'] for player in team['players'] ] )
    
    # Some players have 3 heroes, others have 0, others have 1. Too weird
    # Therefore preferred heroes are not included for now. If I add them
    # later, it would be as a list within one column.
    
    #Now join the two
    p_df = p_df1.merge(p_df2, left_on='id', right_on='id', how='left')
    
    # Filter by team
    if len(team_abbr) > 0:
        p_df = p_df[p_df.team_abbr.isin(team_abbr)]
        
    return p_df