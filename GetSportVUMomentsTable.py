# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 17:01:54 2017

@author: DanLo1108
"""



import numpy as np
import pandas as pd
import json
import os
import zipfile
import gzip

import matplotlib.pyplot as plt
#%pylab inline
import seaborn as sns; sns.set(style=None, color_codes=True)

from IPython.display import IFrame

from matplotlib import pyplot as plt
from matplotlib import animation
from os import walk



#List filepath for game
filepath='/Users/DanLo1108/Documents/SportVU/2014-10-28/0021400001/'
gameID_num='0021400001'
#Open files
#with gzip.open(filepath+moments_file, 'rb') as f:
#    d = json.loads(f.read().decode("ascii"))    
    

#Function to find player closest to ball 
def get_closest(l1,l2):
    min_dist=1000
    for xy in l2:
        dist=np.sqrt((l1[0]-xy[0])**2+(l1[1]-xy[1])**2)
        if dist < min_dist:
            min_dist=dist
            min_player=xy[2]
            
    return min_player,min_dist

def get_player_name(x,d):
    #return d[x.ClosestPlayerID][2]+' '+d[x.ClosestPlayerID][0]
    try:
        return d[x.ClosestPlayerID][0]
    except:
        return 'No Player Match'

def get_player_pos(x,d):
    try:
        return d[x.ClosestPlayerID][3]
    except:
        return 'No Player Match'
    
def get_player_team(x,d1,d2):
    try:
        return d2[d1[x.ClosestPlayerID][-1]]['name']
    except:
        return 'No Player Match'
    
    
def get_player_homeaway(x,d):
    try:
        return d[x.ClosestPlayerID][-1].upper()
    except:
        return 'No Player Match'
    

def get_player_info(x,d1,d2):
    try:
        return d1[x.ClosestPlayerID][0],d1[x.ClosestPlayerID][3],d2[d1[x.ClosestPlayerID][-1]]['name'],d1[x.ClosestPlayerID][-1].upper()
    except:
        return 'No Player Match'


def get_EventTime(x):
    return int(x.PCTIMESTRING[:-3])*60+int(x.PCTIMESTRING[-2:])
    


play_files = []
for (dirpath, dirnames, filenames) in walk(filepath):
    play_files.extend(filenames)
    #print filenames
    break

try:
    play_files.remove('.DS_Store')
except:
    play_files=play_files
    


play_names=[]
play_dicts=[]
for fil in play_files[:-1]:
    with gzip.open(filepath+fil, 'rb') as json_data:
        #Read in json as new play
        new_play=json.loads(json_data.read().decode("ascii"))
        
        #Make sure there are moments in this play:
        if len(new_play['moments']) > 0:
        
            #If first play, append to list + set old play to play:
            if len(play_dicts) == 0:
                play_names.append(int(fil[21:24]))
                play_dicts.append(new_play)
                old_play = new_play
                json_data.close()
                
            #Else, check to see if new play is a duplicate of previously appended play.
            #Check length, quarter and first game time:
            else:
                if len(new_play['moments']) == len(old_play['moments']) and \
                   new_play['moments'][0][0] == old_play['moments'][0][0] and \
                   new_play['moments'][0][2] == old_play['moments'][0][2]:
                       
                       json_data.close()
                       
                else:
                    play_names.append(int(fil[21:24]))
                    play_dicts.append(new_play)
                    old_play = new_play
                    json_data.close()

        
with gzip.open(filepath+'/game_'+gameID_num+'-playbyplay.json.gz', 'rb') as f:
    pbp = json.loads(f.read().decode("ascii"))
    
  
#Define home and visiting teams
hometeam = play_dicts[1]['home']['name']
homeid = play_dicts[1]['home']['teamid']
visteam = play_dicts[0]['visitor']['name']
visid = play_dicts[0]['visitor']['teamid']

lastnames=[player['lastname'] for player in play_dicts[0]['home']['players']]+\
          [player['lastname'] for player in play_dicts[0]['visitor']['players']]

#Define 'moments' and time coordinates
#get all moments into 1 list:
moments=[]
play_nums=[]
for i in range(len(play_dicts)):
    play=play_dicts[i]
    moments+=[moment for moment in play['moments'] if len(moment[5])==11]
    play_nums+=[play_names[i]]*len(play['moments'])
    
    
time=[moments[i][3] for i in range(len(moments))]


#Get info from moments
game_id=play_dicts[0]['gameid']
quarter=[moments[i][0] for i in range(len(moments))]
time=[moments[i][2] for i in range(len(moments))]
shotclock=[moments[i][3] for i in range(len(moments))]
team_poss=moments

#duration=max(time)/60.

#Get ball coordinates
ball_pos_x=[moments[i][5][0][2] for i in range(len(moments))]
ball_pos_y=[moments[i][5][0][3] for i in range(len(moments))]
ball_pos_z=[moments[i][5][0][4] for i in range(len(moments))]


#Get home player coordinates
x_pos={}
y_pos={}
for i in range(1,6):
    x_pos[i]=[moments[j][5][i][2] for j in range(len(moments))]
    y_pos[i]=[moments[j][5][i][3] for j in range(len(moments))]

#Get away player coordinates
for i in range(1,6):
    x_pos[i+5]=[moments[j][5][i+5][2] for j in range(len(moments))]
    y_pos[i+5]=[moments[j][5][i+5][3] for j in range(len(moments))]

    

    
    

#Create cleaned moments dataframe
#with ball coordinates and closest player
moment_values=[]
for i in range(len(time)):
    pn=play_nums[i]
    q=quarter[i]
    t=time[i]
    sc=shotclock[i]
    ball_pos=(ball_pos_x[i],ball_pos_y[i])
    ball_height=ball_pos_z[i]
    player_pos=[(moments[i][5][j][2],moments[i][5][j][3],moments[i][5][j][1]) for j in range(1,len(moments[i][5]))]
    closest_player=get_closest(ball_pos,player_pos)[0]
    closest_player_dist=get_closest(ball_pos,player_pos)[1]

    moment_values.append((game_id,pn,q,t,sc,ball_pos,ball_height,closest_player,closest_player_dist,\
   (x_pos[1][i],y_pos[1][i]),(x_pos[2][i],y_pos[2][i]),(x_pos[3][i],y_pos[3][i]),(x_pos[4][i],y_pos[4][i]),(x_pos[5][i],y_pos[5][i]),\
   (x_pos[6][i],y_pos[6][i]),(x_pos[7][i],y_pos[7][i]),(x_pos[8][i],y_pos[8][i]),(x_pos[9][i],y_pos[9][i]),(x_pos[10][i],y_pos[10][i])))
    
moments_df=pd.DataFrame(moment_values,columns=['GameID','PlayNum','Quarter','GameTime','ShotClock','BallPosition',\
                                               'BallHeight','ClosestPlayerID','ClosestPlayerDistance','HOME player 1', \
                                               'HOME player 2','HOME player 3','HOME player 4','HOME player 5', \
                                               'VISITOR player 1','VISITOR player 2','VISITOR player 3','VISITOR player 4','VISITOR player 5'])

#Map playerID to player
players_dic={val['playerid']:[val[key] for key in val if key != 'playerid']+['home'] for val in play_dicts[0]['home']['players']}
players_dic.update({val['playerid']:[val[key] for key in val if key != 'playerid']+['visitor'] for val in play_dicts[0]['visitor']['players']})


#Functions to get player name, position and team

moments_df['ClosestPlayerName']=moments_df.apply(lambda x: get_player_name(x,players_dic),axis=1)
moments_df['ClosestPlayerPosition']=moments_df.apply(lambda x: get_player_pos(x,players_dic),axis=1)
moments_df['ClosestPlayerTeam']=moments_df.apply(lambda x: get_player_team(x,players_dic,play_dicts[0]),axis=1)
moments_df['ClosestPlayerHomeAway']=moments_df.apply(lambda x: get_player_homeaway(x,players_dic),axis=1)
















