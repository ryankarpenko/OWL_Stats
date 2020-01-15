# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 22:07:19 2019

@author: penko
"""

'''
# packages used in this function
import requests
import numpy as np
import pandas as pd
'''

# The guid's are fairly messed up within OW, with multiple guid's belonging to the
#   same map, each with different combinations of modes, including duplicates.
#   e.g. Hollywood - (Hybrid) and Hollywood - (Hybrid, Skirmish) will have different guid's
#   If we just want the list of unique maps and their type in the OWL then we can get rid of 
#   duplicates and not worry about the lost guid's.
#   But since two matches/maps in the MatchStats might use different guid's for the same map,
#   it will be important to have all the possible guid's that have been used (the redundant part)
#   so that we can get the map name etc. This is further complicated by some 'map' values
#   being gone from the matches/maps section. Therefore, I will make uniqueness an argument
def getMaps(unique = False, only_OWL_modes = False):
    maps = requests.get("https://api.overwatchleague.com/maps")
    
    if maps.status_code != 200:
        print("Error: Could not retrieve data from server. Code ", maps.status_code, sep='')
        return None
    
    m_json = maps.json()
    
    m_df = pd.DataFrame( [ {
        "guid": m['guid'],
        "id_string": m['id'],
        "name": m['name']['en_US'],
        "mode_id_name": [ (gm['Id'], gm['Name']) for gm in m['gameModes'] ]
    } for m in m_json if (m['guid'] not in ['0x08000000000006C7'] and m['id'] != "") ] )
    # -First guid above is for VPP Green Room, which is a testing map for OWL devs
    # -The second part of if stmt (id string must exist) removes "maps" like Busan Sanctuary.
    #    if this proves to be bad (e.g. a map id in the stats section needs
    #    Busan Sactuary), then you can remove the 'and' portion. Perhaps in that
    #    case, you could make the id_string = lower(name)
    
    # make a row for each game mode in the map
    m_df = m_df.explode('mode_id_name')
    m_df[['mode_id','mode_name']] = pd.DataFrame([*m_df.mode_id_name], m_df.index)
    m_df = m_df.drop(columns='mode_id_name')
    if only_OWL_modes == True:
        m_df = m_df[m_df.mode_name.isin(['Assault','Payload','Hybrid','Control'])]
    if unique == True:
        m_df.drop_duplicates(subset=['id_string','name','mode_id','mode_name'], inplace=True)
        # Gets rid of inaccurate Paris Hybrid entry. Otherwise left in for robustness
        m_df = m_df[np.logical_not(m_df.guid.isin(['0x0800000000000AF0']))]
    m_df.reset_index(drop=True, inplace=True)
    
    return m_df