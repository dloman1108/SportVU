
import numpy as np
import pandas as pd
import json
import os
import zipfile
import gzip

import matplotlib
import matplotlib.pyplot as plt

#%pylab inline
import seaborn as sns; sns.set(style=None, color_codes=True)
sns.set_style("white")

from IPython.display import IFrame

from matplotlib import pyplot as plt
from matplotlib import animation
#import framework



### ONE GAME ###    


#root_path='/Users/DanLo1108/Documents/SportVU/'
#game_files=[]
#for (dirpath, dirnames, filenames) in walk(root_path):
#    if len(dirpath)==56:
#        game_files.append(dirpath)
               
#pd.DataFrame({'GameFiles':game_files}).to_csv('/Users/DanLo1108/Documents/Projects/SportVU_files/game_files.csv',index=False)
 

filepath="Path to SportVU game file"
    
#Specify play number + colors
play_num=20
home_color='gold'
away_color='darkblue'

#Walk through filepath to get names of all play files
from os import walk
play_files = []
for (dirpath, dirnames, filenames) in walk(filepath):
    play_files.extend(filenames)
    #print filenames
    break

try:
    play_files.remove('.DS_Store')
except:
    play_files=play_files
    


#Get a list of play dictionaries
play_dicts=[]
play_names=[]
for fil in play_files[:-1]:
    with gzip.open(filepath+fil) as json_data:
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


with gzip.open(filepath+'game_'+gameID_num+'-playbyplay.json.gz', 'rb') as f:
    pbp = json.loads(f.read().decode("ascii"))

p_help=pbp['resultSets'][0]['headers']
plays=pbp['resultSets'][0]['rowSet']

plays_df=pd.DataFrame(plays,columns=p_help)
        

#Define home and visiting teams
hometeam = play_dicts[1]['home']['name']
homeid = play_dicts[1]['home']['teamid']
visteam = play_dicts[0]['visitor']['name']
visid = play_dicts[0]['visitor']['teamid']

 
#96,97,101
 #196,197

#def animate(play):
#    global play_dicts
    
play=play_dicts[play_names.index(play_num)]
moments=[moment for moment in play['moments'] if len(moment[5])==11]


players_dic={val['playerid']:[val[key] for key in val if key != 'playerid']+['home'] for val in play_dicts[0]['home']['players']}
players_dic.update({val['playerid']:[val[key] for key in val if key != 'playerid']+['visitor'] for val in play_dicts[0]['visitor']['players']})




x_pos={}
y_pos={}
time=[moments[i][2] for i in range(len(moments))]
shotclock=[moments[i][3] for i in range(len(moments))]
quarter=moments[0][0]


#duration=max(time)/60.

x_pos['ball']=[moments[i][5][0][2] for i in range(len(moments))]
y_pos['ball']=[moments[i][5][0][3] for i in range(len(moments))]
ball_z=[moments[i][5][0][4] for i in range(len(moments))]
player_names={}
player_nums={}

for i in range(1,11):
    x_pos[i]=[moments[j][5][i][2] for j in range(len(moments))]
    y_pos[i]=[moments[j][5][i][3] for j in range(len(moments))]
    #x[moments[0][5][i][1]]=[moments[j][5][i][2] for j in range(len(moments))]
    #y[moments[0][5][i][1]]=[moments[j][5][i][3] for j in range(len(moments))]
    player_names[i]=players_dic[moments[0][5][i][1]][2][0]+ '. '+players_dic[moments[0][5][i][1]][0]
    player_nums[i]=players_dic[moments[0][5][i][1]][1]


#Set duration of animation
#duration=len(time)
duration=len(time)

#Join play descriptions and time
def convert_time(x):
    mins=int(x/60.)
    secs=("%.2f" % round((x/60.-mins)*.6,2))[-2:] 
    if int(secs)==60:
        return str(mins+1)+':00'
    else:
        return str(mins)+':'+secs  
        
time_plays=pd.DataFrame({'PERIOD':[quarter]*len(time),
              'PCTIMESTRING':map(lambda x: convert_time(x),time)})
              
time_plays=time_plays.merge(plays_df[['PERIOD','PCTIMESTRING','HOMEDESCRIPTION']].dropna(),
                 on=['PERIOD','PCTIMESTRING'],how='left')           
time_plays=time_plays.merge(plays_df[['PERIOD','PCTIMESTRING','VISITORDESCRIPTION']].dropna(),
                 on=['PERIOD','PCTIMESTRING'],how='left')                 

time_plays=time_plays.replace(np.nan,' ', regex=True)


#Get Team 1 coordinates
team1_x=[[x_pos[i][j] for i in range(1,6)] for j in range(duration)]
team1_y=[[y_pos[i][j] for i in range(1,6)] for j in range(duration)]

#Get Team 2 coordinates
team2_x=[[x_pos[i][j] for i in range(6,11)] for j in range(duration)]
team2_y=[[y_pos[i][j] for i in range(6,11)] for j in range(duration)]


#Get Team 1 players/nums
team1_names=[[player_names[i] for i in range(1,6)] for j in range(duration)]
team1_nums=[[player_nums[i] for i in range(1,6)] for j in range(duration)]

#Get Team 2 players/nums
team2_names=[[player_names[i] for i in range(6,11)] for j in range(duration)]
team2_nums=[[player_nums[i] for i in range(6,11)] for j in range(duration)]



fig = plt.figure(1,figsize=(15, 11.5))
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=(0, 94), ylim=(50, 0))
court = plt.imread('/Users/DanLo1108/Documents/Voodoo Sports/SportVU/fullcourt.png')
plt.imshow(court, zorder=0, extent=[0,94,50,0])

#Plot ball and players:
ball,=ax.plot([],[],'o',ms=10, zorder=1,color='darkorange')
home_team,=ax.plot([],[],'o',ms=20,zorder=1,color=home_color)   
vis_team,=ax.plot([],[],'o',ms=20,zorder=1,color=away_color)

#Add player names:
hp1=ax.text(0,0,'')
hp2=ax.text(0,0,'')
hp3=ax.text(0,0,'')
hp4=ax.text(0,0,'')
hp5=ax.text(0,0,'')

#Add player names:
vp1=ax.text(0,0,'')
vp2=ax.text(0,0,'')
vp3=ax.text(0,0,'')
vp4=ax.text(0,0,'')
vp5=ax.text(0,0,'')

home_players=[hp1,hp2,hp3,hp4,hp5]
visiting_players=[vp1,vp2,vp3,vp4,vp5]

#Add lines:
#hpline1,=ax.plot([],[],'-',color='black',alpha=.6)
#hpline2,=ax.plot([],[],'-',color='black',alpha=.6)
#hpline3,=ax.plot([],[],'-',color='black',alpha=.6)
#hpline4,=ax.plot([],[],'-',color='black',alpha=.6)
#hpline5,=ax.plot([],[],'-',color='black',alpha=.6)
#
#vpline1,=ax.plot([],[],'-',color='black',alpha=.6)
#vpline2,=ax.plot([],[],'-',color='black',alpha=.6)
#vpline3,=ax.plot([],[],'-',color='black',alpha=.6)
#vpline4,=ax.plot([],[],'-',color='black',alpha=.6)
#vpline5,=ax.plot([],[],'-',color='black',alpha=.6)
#
#home_lines=[hpline1,hpline2,hpline3,hpline4,hpline5]
#visiting_lines=[vpline1,vpline2,vpline3,vpline4,vpline5]

#Add play descriptions and home/away identifiers:
home_desc=ax.text(0,0,'')
vis_desc=ax.text(0,0,'')
home_identifier=ax.text(0,-6,'HOME')
visitor_identifier=ax.text(47,-6,'VISITOR')

#Animate time:
gameclock_text=ax.text(39,-1,'')
shotclock_text=ax.text(53,-1,'')
quarter_text=ax.text(30.2,-1,'Quarter: '+str(quarter))


def init():
    global x_pos,y_pos,team1_x,team1_y,team2_x,team2_y
    ball.set_data([],[])
    home_team.set_data([],[])
    vis_team.set_data([],[])
    hp1.set_text('')
    gameclock_text.set_text('')
    shotclock_text.set_text('')
    home_desc.set_text('')
    vis_desc.set_text('')
    #hp1.xytest=(20,20)
    #hp1.set_text('Nikola Vucevic')
    return ball,home_team,vis_team,hp1,gameclock_text,shotclock_text,\
           home_desc,vis_desc
  

def animate(t):
    global x_pos,y_pos,team1_x,team1_y,team2_x,team2_y,ball_z
    ball.set_data(x_pos['ball'][t],y_pos['ball'][t])
    ball.set_markersize(8+.8*ball_z[t])
    home_team.set_data(team1_x[t],team1_y[t])   
    vis_team.set_data(team2_x[t],team2_y[t])
    
    for i in range(5):
        home_players[i].set_text(team1_names[t][i])
        home_players[i].set_position((team1_x[t][i]+1,team1_y[t][i]-1))
        
        visiting_players[i].set_text(team2_names[t][i])
        visiting_players[i].set_position((team2_x[t][i]+1,team2_y[t][i]-1))
        
        #home_lines[i].set_data([team1_x[t][i]+.1,team1_x[t][i]+1],[team1_y[t][i]-.1,team1_y[t][i]-1])
        #visiting_lines[i].set_data([team2_x[t][i]+.1,team2_x[t][i]+1],[team2_y[t][i]-.1,team2_y[t][i]-1])
    
    gameclock_text.set_text('Game Clock: '+convert_time(time[t]))
    gameclock_text.set_position((39.2,-1))
    
    shotclock_text.set_text('Shot Clock: '+"%.1f" % shotclock[t])
    shotclock_text.set_position((53.2,-1))
    
    home_desc.set_text(hometeam+': '+str(time_plays.HOMEDESCRIPTION.tolist()[t] or ''))
    home_desc.set_position((0,-4.1))
    
    vis_desc.set_text(visteam+': '+str(time_plays.VISITORDESCRIPTION.tolist()[t] or ''))
    vis_desc.set_position((47,-4.1))
    
    return ball,home_team,vis_team,hp1,gameclock_text,shotclock_text,home_desc,vis_desc#,\
           #hpline1,hpline2,hpline3,hpline4,hpline5,vpline1,vpline2,vpline3,vpline4,vpline5

ani=animation.FuncAnimation(fig,animate,frames=duration,
                            interval=max(time)-min(time),init_func=init,blit=False)
   
   
plt.show()
