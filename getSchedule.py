# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 22:13:56 2019

@author: penko
"""

'''
# packages used in this function
import requests
import json
import numpy as np
import pandas as pd
'''

# Does not currently support All-Star due to missing data for All-Star events
def getSchedule(years = [2019], regular_season = True, preseason = False, playoffs = False, all_star = False, stages = [1,2,3,4], team_abbr = []):
    # Need lists for iteration
    if not isinstance(stages, list):
        stages = [stages]
    if not isinstance(years, list):
        years = [years]
    if not isinstance(team_abbr, list):
        team_abbr = [team_abbr]
    
    # Make stages unique
    stages_copy = list(set(stages))    
    
    # Parameter error checking
    if not all([isinstance(x, int) for x in stages]):
        print('Error: All stage values must be integers.')
        return None
    if not all([(x >= 0 and x <= 4) for x in stages]):
        print('Error: All stage values must be either 1, 2, 3, or 4.')
        return None
    if not all([(y >= 2018 and y <= 2019) for y in years]):
        print('Error: Years must be either 2018, 2019, or both.')
        return None
    #EDIT ONCE TEAM FUNC IS DONE
    
    # Need to create stage id's since they don't match properly
    # Translation goes from argument -> id
    
    #if team_abbr not in getTeams()['abbr']
    if regular_season == False:
        stages_copy = []
    # The OWL API has different stage id's for the different seasons
    # so we have to create the stage_ids each time in the year loop below
    
    def date_print(obj):
        result = [obj[5:7], r"/", obj[8:10], r"/", obj[0:4]]
        return "".join(result)
    
    result = pd.DataFrame()
    
    for y in years:
        # Making stage_ids. Refer to above comment for reasoning
        stage_ids = []
        #2018
        if y == 2018:
            if preseason == True:
                stage_ids.append(0)
            stage_translate = {1: 1, 2: 2, 3: 3, 4: 4}
            for s in stages_copy:
                stage_ids.append(stage_translate[s])
            if playoffs == True:
                stage_ids.append(5)
        #2019
        else:
            stage_translate = {1: 0, 2: 1, 3: 3, 4: 4}
            for s in stages_copy:
                stage_ids.append(stage_translate[s])
            if playoffs == True:
                stage_ids.extend([5,6])
            #if all_star == True:
            #    stage_ids.append(2)
        
        # API call
        schedule = requests.get('https://api.overwatchleague.com/schedule?locale=en_US&season='+str(y))
        
        # Server error checking
        if schedule.status_code != 200:
            print("Error: Could not retrieve data from server. Code ", schedule.status_code, sep='')
            return None
    
        # JSON object
        s_json = schedule.json()
    
        # Temp df object, re-used for each season/year
        s_df = pd.DataFrame()
        
        # Large list comprehension of dictionaries that is passed into a
        #   DataFrame object. Queries
        s_df = pd.DataFrame( [ {
            "match_id": m['id'],
            "date": "".join([m['startDate'][5:7], r"/", m['startDate'][8:10], r"/", m['startDate'][0:4]]),
            "season": y,
            "stage_id": s_json['data']['stages'][s]['id'],
            "stage_name": s_json['data']['stages'][s]['slug'],
            "week_id": w['id'],
            "week_name": w['name'],
            "team_a_id": m['competitors'][0]['id'],
            "team_a_name": m['competitors'][0]['name'],
            "team_a_abbr": m['competitors'][0]['abbreviatedName'],
            "team_a_score": m['scores'][0]['value'],
            "team_b_id": m['competitors'][1]['id'],
            "team_b_name": m['competitors'][1]['name'],
            "team_b_abbr": m['competitors'][1]['abbreviatedName'],
            "team_b_score": m['scores'][1]['value'],
            "winner_id": "DRW" if m['scores'][0]['value'] == m['scores'][1]['value'] else m['competitors'][0]['id'] if m['scores'][0]['value'] > m['scores'][1]['value'] else m['competitors'][1]['id'],
            "winner_name": "DRW" if m['scores'][0]['value'] == m['scores'][1]['value'] else m['competitors'][0]['name'] if m['scores'][0]['value'] > m['scores'][1]['value'] else m['competitors'][1]['name'],
            "winner_abbr": "DRW" if m['scores'][0]['value'] == m['scores'][1]['value'] else m['competitors'][0]['abbreviatedName'] if m['scores'][0]['value'] > m['scores'][1]['value'] else m['competitors'][1]['abbreviatedName']
        } for s in stage_ids for w in s_json['data']['stages'][s]['weeks'] for m in w['matches'] ] )
        
        # Filter for team
        if len(team_abbr) > 0:
            s_df = s_df[((s_df.team_a_abbr.isin(team_abbr)) | (s_df.team_b_abbr.isin(team_abbr)))]
        
        result = result.append(s_df)
    
    return result