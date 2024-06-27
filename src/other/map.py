from interactions import (
    Extension,
    slash_command, 
    slash_option, 
    SlashContext,
    OptionType,
    Embed
)
import src.db.db as db
from src.db.db import get_tournament_db_id

import requests
from dotenv import find_dotenv, load_dotenv, get_key
from math import floor

map_record_url = "https://prod.trackmania.core.nadeo.online/mapRecords/"
map_info_url = "https://prod.trackmania.core.nadeo.online/maps/?mapUidList="

# Get map records for a list of accounts and a list of map ids
def get_map_records(account_ids, map_ids, token):

    # Load variables from .env
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    token = get_key(dotenv_path, ("NADEO_ACCESS_TOKEN"))
    user_agent = get_key(dotenv_path, ("USER_AGENT"))

    # Build url
    account_id_str = ','.join(account_ids)
    map_id_str = ','.join(map_ids)

    complete_url = map_record_url + \
                    "?accountIdList=" + account_id_str + \
                    "&mapIdList=" + map_id_str
    
    # Send get request

    headers = {
        'Authorization': "nadeo_v1 t=" + token,
        'User-Agent': user_agent
    }

    res = requests.get(complete_url, headers=headers)
    res = res.json()

    # Return relevant data

    # Record format: time, accountId, mapId
    records = [[elem["recordScore"]["time"],
                    elem["accountId"],
                    elem["mapId"]] 
                for elem in res]
    
    return records

# Converts a record time of format "42690" to "42.690", or "62690" to "01:02.690"
#   mins: Bool, if there should be minutes in formatting or not. Default: True
def format_map_record(record, mins=True):

    #Check if time is formatted with minutes (ex. 01:01.110)
    #   If so, format as seconds
    record_string = str(record)
    minutes = record_string.split(":")[0]
    if(minutes != record_string):
        seconds = float(record_string.split(":")[1])
        minutes = int(minutes)
        record_string = str(seconds + 60 * minutes)
        record = int(record_string)

    else:
        record = int(record)

    if(mins):

        minutes = floor(record / 60000)
        seconds = record - (minutes * 60000)

        if(minutes == 0):
            minutes = ""
        elif(minutes < 10):
            minutes = "0" + str(minutes) + ":"
        else:
            minutes = str(minutes) + ":"

        
        if(seconds < 100):
            seconds = str(seconds)
            # Adding an extra '0' in front if the seconds are only 2 digits
            seconds = "00" + ".0" + seconds[-3:]
        elif(seconds < 1000):
            seconds = str(seconds)
            seconds = "00" + "." + seconds[-3:]
        elif(seconds < 10000):
            seconds = str(seconds)
            seconds = "0" + seconds[:-3] + "." + seconds[-3:]
        else:
            seconds = str(seconds)
            seconds = seconds[:-3] + "." + seconds[-3:]

        res = minutes + str(seconds)

        return res
    
    seconds = record
    if(seconds < 100):
        seconds = str(seconds)
        # Adding an extra '0' in front if the seconds are only 2 digits
        seconds = "00" + ".0" + seconds[-3:]
    elif(seconds < 1000):
        seconds = str(seconds)
        seconds = "00" + "." + seconds[-3:]
    elif(seconds < 10000):
        seconds = str(seconds)
        seconds = "0" + seconds[:-3] + "." + seconds[-3:]
    else:
        seconds = str(seconds)
        seconds = seconds[:-3] + "." + seconds[-3:]

    return seconds




# Get map information from a map uid
def get_map_data(map_uids):

    # Load variables from .env
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    token = get_key(dotenv_path, ("NADEO_ACCESS_TOKEN"))
    user_agent = get_key(dotenv_path, ("USER_AGENT"))

    # Build url
    uid_str = ','.join(map_uids)
    complete_url = map_info_url + uid_str

    # Send get request

    headers = {
        'Authorization': "nadeo_v1 t=" + token,
        'User-Agent': user_agent
    }

    res = requests.get(complete_url, headers=headers)
    res = res.json()
    
    # Return the relevant data
    map_data = [[elem["mapId"],
                    elem["mapUid"],
                    elem["name"]]
                for elem in res]

    return map_data


def get_map_uid_from_db(conn, map_name):

    return db.retrieve_data(conn, (db.get_map_uid, [map_name]))[0][0]



