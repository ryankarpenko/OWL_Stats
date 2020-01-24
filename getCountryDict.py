# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 10:53:38 2019

@author: penko

Useful dictionary for converting country abbreviations to full names

"""

'''
# packages used in this function
import requests
'''

# Key = Country Abbreviation  ...   Value = Country Full Name
def getCountryDict():
    countries = requests.get('https://api.overwatchleague.com/data/countries')
    
    if countries.status_code != 200:
        print("Error: Could not retrieve data from server. Code ", countries.status_code, sep='')
        return None
    
    c_dict = {c['value']:c['label'] for c in countries.json()['countries']}
    
    return c_dict
        