# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 11:30:32 2019

@author: penko

Get information about a match such as the winner, the date, players involved, etc.
Fairly similar to getPlayerMatchStats, but due to separated calls in the API,
these functions serve slightly different purposes. You might think of
getMatches() as returning qualitative information about the map, players etc
while getPlayerMatchStats() returns quantitative data about players.

"""

'''
# packages used in this function
import requests
import pandas as pd
'''

# In R, Metlover calls /match/*matchid* repeatedly and concatenates them.
# After some testing, I found that after only 6 or so matches, this
# one-at-a-time approach is slower than getting all the matches for a season
# at once and filtering them by matchid. Of course, this requires more data,
# but i think time is more crucial, and only the desired matches are returned.
# BUT what if I have match id's from multiple seasons? The solution: make
# three calls for each season (18, 19, 20). Then find the matches for each season.
# Then combine those matches into one list
def getMatches(match_ids):    
    
    if not isinstance(match_ids, list):
        match_ids = [match_ids]
       
    result = pd.DataFrame()
    
    modes = getMaps(unique=True, only_OWL_modes=True)
    countryDict = getCountryDict()
    
    # Do the whole thing for each year, then concatenate. So that you cover all
    #   possible match_ids
    for y in [2018,2019,2020]:
        matches = requests.get("https://api.overwatchleague.com/matches?season="+str(y))
        
        if matches.status_code != 200:
            continue
        
        m_json_large = matches.json()
        
        m_json = [ m for m in m_json_large['content'] if m['id'] in match_ids ]
        
        # This is pretty grody and should probably be split up into smaller helper functions.
        match_df = pd.DataFrame( [ {
            # Match info
            "match_id": m['id'],
            "date": m['startDate'],
            "season": y,
            "team_a_id": m['competitors'][0]['id'] if "id" in m['competitors'][0].keys() else None,
            "team_a_name": m['competitors'][0]['name'] if "name" in m['competitors'][0].keys() else None,
            "team_a_abbr": m['competitors'][0]['abbreviatedName'] if "abbreviatedName" in m['competitors'][0].keys() else None,
            "team_a_score": m['scores'][0]['value'] if "value" in m['scores'][0].keys() else None,
            "team_b_id": m['competitors'][1]['id'] if "id" in m['competitors'][1].keys() else None,
            "team_b_name": m['competitors'][1]['name'] if "name" in m['competitors'][1].keys() else None,
            "team_b_abbr": m['competitors'][1]['abbreviatedName'] if "abbreviatedName" in m['competitors'][1].keys() else None,
            "team_b_score": m['scores'][1]['value'] if "value" in m['scores'][1].keys() else None,
            "winner_id": None if ("scores" not in m.keys() or "value" not in m['scores'][0].keys() or "value" not in m['scores'][1].keys()) else "DRW" if m['scores'][0]['value'] == m['scores'][1]['value'] else m['competitors'][0]['id'] if m['scores'][0]['value'] > m['scores'][1]['value'] else m['competitors'][1]['id'],
            "winner_name": None if ("scores" not in m.keys() or "value" not in m['scores'][0].keys() or "value" not in m['scores'][1].keys()) else "DRW" if m['scores'][0]['value'] == m['scores'][1]['value'] else m['competitors'][0]['name'] if m['scores'][0]['value'] > m['scores'][1]['value'] else m['competitors'][1]['name'],
            "winner_abbr": None if ("scores" not in m.keys() or "value" not in m['scores'][0].keys() or "value" not in m['scores'][1].keys()) else "DRW" if m['scores'][0]['value'] == m['scores'][1]['value'] else m['competitors'][0]['abbreviatedName'] if m['scores'][0]['value'] > m['scores'][1]['value'] else m['competitors'][1]['abbreviatedName'],
            "games": [ {
                # game (game) info
                "game_id": mp['id'] if "id" in mp.keys() else None,
                "game_num": mp['number'] if "number" in mp.keys() else None,
                "map_guid": mp['attributes']['mapGuid'] if "mapGuid" in mp['attributes'].keys() else None,
                "map_name": mp['attributes']['map'] if "map" in mp['attributes'].keys() else None,
                "map_type": modes[modes['id_string']==mp['attributes']['map']]['mode_name'].iloc[0] if len(modes[modes['id_string']==mp['attributes']['map']]['mode_name']) > 0 else None,
                "team_a_game_score": mp['attributes']['mapScore']['team1'] if ("mapScore" in mp['attributes'].keys() and "team1" in mp['attributes']['mapScore'].keys()) else None,
                "team_b_game_score": mp['attributes']['mapScore']['team2'] if ("mapScore" in mp['attributes'].keys() and "team2" in mp['attributes']['mapScore'].keys()) else None,
                "team_a_players": [ {
                    # Team A players info
                    "player_id": pl['player']['id'] if "id" in pl['player'].keys() else None,
                    "player_name": pl['player']['name'] if "name" in pl['player'].keys() else None,
                    "player_family_name": pl['player']['familyName'] if "familyName" in pl['player'].keys() else None,
                    "player_given_name": pl['player']['givenName'] if "givenName" in pl['player'].keys() else None,
                    "player_country_code": pl['player']['nationality'] if "nationality" in pl['player'].keys() else None,
                    "player_country": countryDict[pl['player']['nationality']] if "nationality" in countryDict.keys() else None,
                    "player_headshot": pl['player']['headshot'] if "headshot" in pl['player'].keys() else None,
                    "player_home": pl['player']['homeLocation'] if "homeLocation" in pl['player'].keys() else None,
                    "player_number": pl['player']['attributes']['player_number'] if "player_number" in pl['player']['attributes'].keys() else None,
                    "player_role": pl['player']['attributes']['role'] if "role" in pl['player']['attributes'].keys() else None
                    } for pl in mp['players'] if pl['team']['id'] == m['competitors'][0]['id'] ],
                "team_b_players": [ {
                    # Team B players info
                    "player_id": pl['player']['id'] if "id" in pl['player'].keys() else None,
                    "player_name": pl['player']['name'] if "name" in pl['player'].keys() else None,
                    "player_family_name": pl['player']['familyName'] if "familyName" in pl['player'].keys() else None,
                    "player_given_name": pl['player']['givenName'] if "givenName" in pl['player'].keys() else None,
                    "player_country_code": pl['player']['nationality'] if "nationality" in pl['player'].keys() else None,
                    "player_country": countryDict[pl['player']['nationality']] if "nationality" in countryDict.keys() else None,
                    "player_headshot": pl['player']['headshot'] if "headshot" in pl['player'].keys() else None,
                    "player_home": pl['player']['homeLocation'] if "homeLocation" in pl['player'].keys() else None,
                    "player_number": pl['player']['attributes']['player_number'] if "player_number" in pl['player']['attributes'].keys() else None,
                    "player_role": pl['player']['attributes']['role'] if "familyName" in pl['player']['attributes'].keys() else None
                    } for pl in mp['players'] if pl['team']['id'] == m['competitors'][1]['id'] ]
                } for mp in m['games'] ]
        } for m in m_json ] )
        
        result = result.append(match_df)
    
    return result
