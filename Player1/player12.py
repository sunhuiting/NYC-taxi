# coding: utf-8

# In[66]:


import sys
import json
from datetime import timedelta, datetime
import dateutil.parser
import random
import numpy as np
import pandas as pd
import math


# In[67]:


lookup_cluster = pd.read_csv('lookup.csv')

# In[68]:


def trace_weekday(weekday_num):
    weekday_lst = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    filename = 'lookup_' + weekday_lst[weekday_num] + '.csv'
    return filename


# In[69]:

previous_cell = ['', '', '', '']

def play_turn(current_datetime, currentCell, neighbours):
    
    global previous_cell
    current_hour = current_datetime.hour
    current_day = current_datetime.weekday()
    
    # overnight shift
    overnight_day = [3,4,5,6]
    overnight_hour = [0,1,2]
    if ((current_day in overnight_day) & (current_hour in overnight_hour)):
        current_day = current_day-1

    # current weekday lookup table
    db = trace_weekday(current_day)
    lookup_table = pd.read_csv(db)
    end_of_shift = int(list(lookup_table.columns)[-1].split('_')[0][1:])

    if (current_hour > end_of_shift):
        next_shift(current_datetime)
    
    
    # find the cluster of current cell
    current_cluster = int(lookup_cluster[lookup_cluster['cell'] == currentCell]['cluster'])
    
    cluster_density = 'h' + str(current_hour) + '_density'
    trip_rate = 'h' + str(current_hour) + '_trip_rate'
    cell = 'h' + str(current_hour) + '_top_cell'

    top_cell = list(lookup_table[lookup_table[cluster_density]=='high'][cell])  
             
    current_col = int(currentCell.split(':')[0])
    current_row = int(currentCell.split(':')[-1])

    distance = 100000
    destination = currentCell
    
    for i in range(len(top_cell)):
        if (top_cell[i] is not np.nan):
            destination_col = int(str(top_cell[i]).split(':')[0])
            destination_row = int(str(top_cell[i]).split(':')[-1])

            temp = math.sqrt((current_col-destination_col)**2 + (current_row-destination_row)**2)
            if (temp < distance):
                distance = temp
                destination = top_cell[i]
       

    if ((destination == "41:50") & ("41:50" not in neighbours) & (current_cluster == 10)):
        top_cell.remove("41:50")

        distance = 100000 
        for i in range(len(top_cell)):
            if (top_cell[i] is not np.nan):
                destination_col = int(str(top_cell[i]).split(':')[0])
                destination_row = int(str(top_cell[i]).split(':')[-1])

                temp = math.sqrt((current_col-destination_col)**2 + (current_row-destination_row)**2)
                if (temp < distance):
                    distance = temp
                    destination = top_cell[i]

    destination_col = int(destination.split(':')[0])
    destination_row = int(destination.split(':')[-1])

    if (destination == currentCell):
        print("NextMove:"+destination)
        return {"state":"FORHIRE","action":"STAY","moveTo":destination}
        

    distance = 100000
    next_move = currentCell
        
    for cell in neighbours:
        if (cluster_density == 'high'):
            nei_col = int(cell.split(':')[0])
            nei_row = int(cell.split(':')[-1])
            temp = math.sqrt((nei_col-destination_col)**2 + (nei_row-destination_row)**2)

            if (temp < distance):
                distance = temp
                next_move = cell

        else:

            if ((cell != previous_cell[-1]) & (cell != previous_cell[-2]) & (cell != previous_cell[-3])
                &  (cell != previous_cell[-4])):
            
            
                nei_col = int(cell.split(':')[0])
                nei_row = int(cell.split(':')[-1])
                temp = math.sqrt((nei_col-destination_col)**2 + (nei_row-destination_row)**2)

                if (temp < distance):
                    distance = temp
                    next_move = cell


    previous_cell.append(currentCell)
    print("NextMove:"+next_move, "Destination:"+destination)
    return {"state":"FORHIRE","action":"MOVE","moveTo":next_move}


# In[70]:


def first_move(start_datetime):
    
    # our taxi driver is not working on Tuesday
    if (start_datetime.weekday() == 1):
        start_datetime = start_datetime.replace(days=2, hour=13, minute=0)
    
    # current weekday lookup table
    db = trace_weekday(start_datetime.weekday())
    clusterdensity = pd.read_csv(db)
    col_name = list(clusterdensity.columns)
    
    start_hour = start_datetime.hour
    shift_start = int(col_name[1].split('_')[0][1:])
    
    if (start_hour < shift_start):
        start_datetime = start_datetime.replace(hour=shift_start, minute=0)
        start_hour = shift_start
    
    trip_rate = 'h' + str(start_hour) + '_trip_rate'
    cell = 'h' + str(start_hour) + '_top_cell'

    index = clusterdensity.index[(clusterdensity[trip_rate] == max(clusterdensity[trip_rate]))]
    next_move = clusterdensity[cell][index].tolist()[0]
    
    return {"defer":start_datetime,"moveTo":next_move}




def next_shift(current_time):

    start_datetime = current_time
    # find the day of the next shift
    if (current_time.weekday() == 1):
        start_datetime = current_time + timedelta(days=1)
        start_datetime = start_datetime.replace(hour=13, minute=0)

    elif ((current_time.weekday() == 0) & (current_time.hour >= 22)):
        start_datetime = current_time + timedelta(days=2)
        start_datetime = start_datetime.replace(hour=13, minute=0)
        
    elif (((current_time.weekday() == 0) & (current_time.hour < 22)) | ((current_time.weekday() == 6) & (current_time.hour >= 21))):
        if (current_time.weekday() == 6):
            start_datetime = start_datetime + timedelta(days = 1)
        start_datetime = start_datetime.replace(hour=12, minute=0)
        
    elif (((current_time.weekday() == 2) & (current_time.hour >= 23)) | ((current_time.weekday() == 3) & (current_time.hour < 23))):
        diff = 3 - current_time.weekday()
        start_datetime = start_datetime + timedelta(days=diff)
        start_datetime = start_datetime.replace(hour=13, minute=0)
        

    elif (((current_time.weekday() == 3) & (current_time.hour >= 23)) | (current_time.weekday() == 4)):
        diff = 4 - current_time.weekday()
        start_datetime = start_datetime + timedelta(days=diff)
        start_datetime = start_datetime.replace(hour=15, minute=0)
        

    elif (current_time.weekday() == 5):
        start_datetime = start_datetime.replace(hour=14, minute=0)

    elif ((current_time.weekday() == 6) & (current_time.hour < 21)):
        start_datetime = start_datetime.replace(hour=11, minute=0)
    
    # lookup table of the next shift
    db = trace_weekday(start_datetime.weekday()) 
    clusterdensity = pd.read_csv(db)
    start_hour = start_datetime.hour
    
    trip_rate = 'h' + str(start_hour) + '_trip_rate'
    top_cell = 'h' + str(start_hour) + '_top_cell'
    
    max_trip_rate = max(clusterdensity[trip_rate])
    index = clusterdensity.index[(clusterdensity[trip_rate] == max(clusterdensity[trip_rate]))]
    next_move = clusterdensity[top_cell][index].tolist()[0]
        
    return {"defer":start_datetime,"moveTo":next_move}



while(1) :
    req = json.loads(sys.stdin.readline())
    reqtype = req['type']
    current_datetime = dateutil.parser.parse(req['time'])
    if(reqtype=="FIRSTMOVE"):
        action = first_move(current_datetime)
        #Create response named list that will be converted to JSON
        resp = {}
        resp["defer"]=action['defer'].strftime("%Y-%m-%dT%H:%M")
        resp["nextMove"]="REPOSITION"
        resp["moveTo"]=action['moveTo']
        print("MAST30034:" + json.dumps(resp))
        sys.stdout.flush()
    elif(reqtype=="PLAYTURN"):
        current_cell = req['currentCell']
        neighbours = req['neighbours']
        action=play_turn(current_datetime, current_cell, neighbours)
        print("MAST30034:" + json.dumps(action))
        sys.stdout.flush()
    elif(reqtype=="NEXTSHIFT"):
        action=next_shift(current_datetime)
        #Create response named list that will be converted to JSON
        resp = {}
        resp["defer"]=action['defer'].strftime("%Y-%m-%dT%H:%M")
        resp["nextMove"]="REPOSITION"
        resp["moveTo"]=action['moveTo']
        print("MAST30034:" + json.dumps(resp))
        sys.stdout.flush()

