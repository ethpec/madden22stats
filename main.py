# Imports
import decimal
from turtle import pos
import pandas as pd
import numpy as np
import xlrd
from decimal import *

# Your File Path
file_path = 'Files/All.xlsm'

# Season
season = 2

# Rating Tier
tier_0 = range(95,100)
tier_1 = range(90,95)
tier_2 = range(85,90)
tier_3 = range(80,85)
tier_4 = range(75,80)
tier_5 = range(70,75)
tier_6 = range(0,70)

# Team Index Dictionary
team_dict = {0:'CHI', 1:'CIN', 2:'BUF', 3:'DEN', 4:'CLE', 5:'TB', 6:'ARI', 7:'LAC', 8:'KC', 9:'IND', 
10:'DAL', 11:'MIA', 12:'PHI', 13:'ATL', 14:'SF', 15:'NYG', 16:'JAX', 17:'NYJ', 18:'DET', 19:'GB', 
20:'CAR', 21:'NE', 22:'LV', 23:'LAR', 24:'BAL', 25:'WAS', 26:'NO', 27:'SEA', 28:'PIT', 29:'TEN', 
30:'MIN', 31:'HOU', 32:'FA'}

# Functions

def find_rating_tier(rating):
    if rating in tier_0:
        return 'tier_0'
    elif rating in tier_1:
        return 'tier_1'
    elif rating in tier_2:
        return 'tier_2'
    elif rating in tier_3:
        return 'tier_3'
    elif rating in tier_4:
        return 'tier_4'
    elif rating in tier_5:
        return 'tier_5'
    elif rating in tier_6:
        return 'tier_6'

def make_range(range_string):
    if '.' in range_string:
        return np.round(np.arange(float(range_string.split('-')[0]), float(range_string.split('-')[1]),.01),2).tolist()
    else:
        return np.round(np.arange(int(range_string.split('-')[0]), int(range_string.split('-')[1]),1)).tolist()

# def make_tier_dict(logic_dataframe):

# Excel Sheet Dataframes (Player Data)
df_players = pd.read_excel(file_path, sheet_name='124 Stuff')
df_players['TeamName'] = df_players['TeamIndex'].apply(lambda x: team_dict[x]) # Create column with lambda
df_players['RatingTier'] = df_players['OverallRating'].apply(find_rating_tier)
df_players.to_csv('Files/PlayerTest.csv', sep=',',index=False)

# Excel Sheets Dataframe (Logic)
df_logic = pd.read_excel('Files/Progression Regression Logic.xlsx', sheet_name='Columnar')
df_logic['StatRange'] = df_logic['StatValue'].apply(make_range)
df_logic.to_csv('Files/LogicTest.csv', sep=',',index=False)

# Excel Sheet Dataframes (Stats) and JOINS
df_offensiveStats = pd.read_excel(file_path, sheet_name='Offensive Stats').merge(df_players, how='left', left_on=['FullName', 'Position', 'TeamPrefixName'], right_on=['FullName','Position','TeamName'])
df_defensiveStats = pd.read_excel(file_path, sheet_name='Defensive Stats').merge(df_players, how='left', left_on=['FullName', 'Position','TeamPrefixName'], right_on=['FullName','Position','TeamName'])
df_olineStats = pd.read_excel(file_path, sheet_name='OLine Stats').merge(df_players, how='left', left_on=['FullName', 'Position','TeamPrefixName'], right_on=['FullName','Position','TeamName'])
df_kickingStats = pd.read_excel(file_path, sheet_name='Kicking Stats').merge(df_players, how='left', left_on=['FullName', 'Position','TeamPrefixName'], right_on=['FullName','Position','TeamName'])

# Filter Dataframes
df_offensiveStats = df_offensiveStats[(df_offensiveStats['SEAS_YEAR'] == season) 
& (df_offensiveStats['ContractStatus'] == 'Signed') & (df_offensiveStats['GAMESPLAYED'] >= 10)]
df_defensiveStats = df_defensiveStats[(df_defensiveStats['SEAS_YEAR'] == season) 
& (df_defensiveStats['ContractStatus'] == 'Signed') & (df_defensiveStats['GAMESPLAYED'] >= 10) & (df_defensiveStats['DOWNSPLAYED'] >= 250)]
df_olineStats = df_olineStats[(df_olineStats['SEAS_YEAR'] == season) 
& (df_olineStats['ContractStatus'] == 'Signed') & (df_olineStats['GAMESPLAYED'] >= 10) & (df_olineStats['DOWNSPLAYED'] >= 250)]

# Add new DataFrame columns for Offense
df_offensiveStats['ScrimmmageYardsPerGame'] = round((df_offensiveStats['RUSHYARDS'] + df_offensiveStats['RECEIVEYARDS']) / df_offensiveStats['GAMESPLAYED'])
df_offensiveStats['ScrimmmageTDsPerGame'] = round((df_offensiveStats['RUSHTDS'] + df_offensiveStats['RECEIVETDS']) / df_offensiveStats['GAMESPLAYED'],2)

# Add new DataFrame columns for OLine
df_olineStats['SacksPer1000Snaps'] = (df_olineStats['OLINESACKSALLOWED'] / df_olineStats['DOWNSPLAYED']) * 1000

# Add new DataFrame columns for Kicking
df_kickingStats['FGPercentage'] = df_kickingStats['KICKFGMADE'] / df_kickingStats['KICKFGATTEMPTS']
df_kickingStats['EPPercentage'] = df_kickingStats['KICKEPMADE'] / df_kickingStats['KICKEPATTEMPTS']
df_kickingStats['Over40YardPercentage'] = (df_kickingStats['KICKFGMADE40TO49'] + df_kickingStats['KICKFGMADE50ORMORE']) / (df_kickingStats['KICKFGATTEMPTS40TO49'] + df_kickingStats['KICKFGATTEMPTS50ORMORE'])
df_kickingStats['PuntTBPerIn20'] = df_kickingStats['PUNTTOUCHBACKS'] / df_kickingStats['PUNTIN20']
df_kickingStats['YardsPerPunt'] = df_kickingStats['PUNTYARDS'] / df_kickingStats['PUNTATTEMPTS']
df_kickingStats['NetYardsToPuntYards'] = df_kickingStats['PUNTNETYARDS'] / df_kickingStats['PUNTYARDS']

# Add new DataFrame columns for Defense
df_defensiveStats['DLSacksAndTFLPerGame'] = (df_defensiveStats['DLINESACKS'] + df_defensiveStats['DEFTACKLESFORLOSS']) / df_defensiveStats['GAMESPLAYED']
df_defensiveStats['TotalTurnovers'] = df_defensiveStats['DLINEFUMBLERECOVERIES'] + df_defensiveStats['DLINESAFETIES'] + df_defensiveStats['DSECINTS'] + df_defensiveStats['DSECINTTDS'] + df_defensiveStats['DLINEBLOCKS'] + df_defensiveStats['DLINEFORCEDFUMBLES'] + df_defensiveStats['DLINEFUMBLETDS']
df_defensiveStats['LBSacksTFLPassDeflPerGame'] = (df_defensiveStats['DLINESACKS'] + df_defensiveStats['DEFTACKLESFORLOSS'] + df_defensiveStats['DEFPASSDEFLECTIONS']) / df_defensiveStats['GAMESPLAYED']
df_defensiveStats['TacklesPerGame'] = (df_defensiveStats['ASSDEFTACKLES'] + df_defensiveStats['DEFTACKLES']) / df_defensiveStats['GAMESPLAYED']
df_defensiveStats['CBPassDeflPerGame'] = df_defensiveStats['DEFPASSDEFLECTIONS'] / df_defensiveStats['GAMESPLAYED']
df_defensiveStats['CBCatchAllowPer100Snaps'] = (df_defensiveStats['CTHALLOWED'] / df_defensiveStats['DOWNSPLAYED']) *100
df_defensiveStats['SafetiesCatchAllowMinusPDPerGame'] = (df_defensiveStats['CTHALLOWED'] - df_defensiveStats['DEFPASSDEFLECTIONS']) / df_defensiveStats['GAMESPLAYED']


# Offensive Stats/Progression
print('Running Offensive Progression')
def offensive_progression(df_offensiveStats, df_logic):
    for idx, row in df_offensiveStats.iterrows():
    # Running Backs
        if  df_offensiveStats.loc[idx,'Position'] == 'HB':
            # Tier 0
            if df_offensiveStats.loc[idx,'OverallRating'] in tier_0:
                df_offensiveStats.loc[idx,'SkillPoints'] += 1

# Join worksheet DataFrames to player DataFrame

# Export our new sheet to a file
df_offensiveStats.to_csv('Files/OffTest.csv', sep=',',index=False)
df_defensiveStats.to_csv('Files/DefTest.csv', sep=',',index=False)
df_olineStats.to_csv('Files/OLTest.csv', sep=',',index=False)
df_kickingStats.to_csv('Files/KickingTest.csv', sep=',',index=False)
print('Test Files created')