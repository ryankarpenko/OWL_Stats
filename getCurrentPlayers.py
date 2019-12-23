# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 15:43:11 2019

@author: penko
"""

import requests
import json
import numpy as np
import pandas as pd

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
    
    '''
    print([ str(str(i) + " " +n['name']) for i, n in enumerate(p_json['content']) ] )
    print([ t['team']['name'] for t in p_json['content'][138]['teams']])
    print( [ p['teams'][0]['team']['name'] for p in p_json['content'] ] )
    print(p_json['content'][0].keys())
    print(np.unique([[*n] for n in p_json['content']]))
    
    
    for n in p_json['content']:
        if 'homeLocation' in n.keys():
            print(n['homeLocation'])
        else:
            print(" ")
            
    print( [ n['homeLocation'] if 'homeLocation' in n.keys() else 'None' for n in p_json['content'] ])
    '''
    
    p_df = pd.DataFrame()
    
    p_df = pd.DataFrame( [ {
            "id": p['id'],
            "name": p['name'],
            "hometown": [ p['homeLocation'] if 'homeLocation' in p.keys() else 'None' for p in p_json['content'] ],
            "given_name": p['givenName'],
            "family_name": p['familyName'],
            "nationality": p['nationality'],
            "team_id": p['teams'][0]['team']['id'],
            "team_name": p['teams'][0]['team']['name'],
            "team_abbr": p['teams'][0]['team']['abbreviatedName']
        } for p in p_json['content'] ] )
    
    if len(team_abbr) > 0:
        p_df = p_df[p_df.teamAbbr.isin(team_abbr)]
        
    return p_df