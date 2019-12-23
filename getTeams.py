# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 17:55:16 2019

@author: penko
"""

import requests
import json
import numpy as np
import pandas as pd

def getTeams():
    # API call
    teams = requests.get('https://api.overwatchleague.com/v2/teams?seasonId=2018')
    
    if teams.status_code != 200:
        print("Error: Could not retrieve data from server. Code ", teams.status_code, sep='')
        return None

    t_json = teams.json()
    
    t_df = pd.DataFrame( [ {
            "id": t['id'],
            "name": t['name'],
            "abbr_name": t['abbreviatedName'],
            "division_id": t['divisionId'],
            "location": t['location'],
            "color_primary": t['colors']['primary']['color'],
            "color_secondary": t['colors']['secondary']['color']
        } for t in t_json['data'] ] )

    return t_df      
