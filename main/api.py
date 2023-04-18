
from datetime import datetime
import json
import logging
from urllib.request import urlopen

from main import confidential as cf
from main import notifier as nf

subject = "PEGE FROGGIT API - Alert"

def get_token():
    access_token_url = "https://api.ecowitt.net/api/token?grant_type="\
        "client_credential&appid=" + cf.APP_ID + "&secret=" + cf.SECRET
    try:
        html = urlopen(access_token_url).read()
        access_token_json = json.loads(html)
        access_token = access_token_json["access_token"]
        logging.info("Access token provided successfully!")
        logging.info("Access token provided: " + access_token)
        return(access_token)
    except:
        error_message = "Access token could not be retrieved!"
        logging.error(error_message)
        logging.info(access_token_url)
        nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)

# Script to get JSON file for real time weather data
def get_data():
    realtime_url="https://api.ecowitt.net/api/devicedata/real_time?access_token="\
        +get_token()+"&openid="+cf.OPEN_ID+"&lang=en&call_back=all"
    try:
        realtime_datafile = urlopen(realtime_url).read().decode()
        realtime_data = json.loads(realtime_datafile)
        logging.info("Json file available!")
        return(realtime_data)
    except:
        error_message = "JSON file could not be retrieved!"
        logging.error(error_message)
        nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)

realtime_data = get_data()

def get_timestamp():
    timestamp=datetime.utcfromtimestamp(int(realtime_data["time"])).strftime("%Y-%m-%d %H:%M:%S")
    logging.info("Timestamp: " + timestamp)
    return(timestamp)

def slice_data(l1, l2, l3="value"):
    slice = realtime_data["data"][l1][l2][l3]
    return(slice)

# Check connection Pege Froggit (loop through data categories to find outdoor data)
def check_connection():
    outdoor_data = 0
    for i in realtime_data["data"]:
        if  i == "outdoor":
            outdoor_data = outdoor_data + 1
    if outdoor_data == 0:
        error_message = "Pege Froggit connection issue"
        nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)
        logging.error(error_message)
    else:        
        logging.info("Outdoor data available")