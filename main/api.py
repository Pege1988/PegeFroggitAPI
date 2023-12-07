
from datetime import datetime
import json
import logging
from urllib.request import urlopen

from main import confidential as cf
from main import notifier as nf

subject = "PEGE FROGGIT API - Alert"

def read_json(url):
    json_url = urlopen(url).read()
    return(json_url)

def get_token(json_file):
    try:
        access_token_json = json.loads(json_file)
        access_token = access_token_json["access_token"]
        logging.info("Access token retrieved successfully!")
        logging.info("Access token provided: " + access_token)
        return(access_token)
    except:
        error_message = "Access token could not be retrieved!"
        logging.error(error_message)
        nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)

# Script to get JSON file for real time weather data
def get_data(json_file):
    try:
        realtime_data = json.loads(json_file)
        logging.info("Json file available!")
        return(realtime_data)
    except:
        error_message = "JSON file could not be retrieved!"
        logging.error(error_message)
        nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)

def get_timestamp(realtime_data):
    timestamp=datetime.utcfromtimestamp(int(realtime_data["time"])).strftime("%Y-%m-%d %H:%M:%S")
    logging.info("Timestamp: " + timestamp)
    return(timestamp)

def slice_data(realtime_data, l1, l2, l3="value"):
    slice = realtime_data["data"][l1][l2][l3]
    return(slice)

# Check connection Pege Froggit (loop through data categories to find outdoor data)
def check_connection(realtime_data):
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