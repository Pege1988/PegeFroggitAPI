# Program to retrieve data from ecowitt weather station via AppID
# Version 1.1.0

# Documentation on API: https://doc.ecowitt.net/web/#/1?page_id=11
# Device developer information: https://api.ecowitt.net/index/user/mydevice.html

from datetime import datetime
import json
import logging
import os
import sqlite3
from urllib.request import urlopen

from main import mail as ml

#==============================================================
#   PARAMETERS
#==============================================================
# Paths
main_path = os.getcwd()
if main_path.find("Dropbox") != -1:
  synology = False
else:
  synology = True
  
# Filepaths
if synology == False:
    data_path = r"C:\Users\neo_1\Dropbox\Projects\Programing\PegeFroggitAPI\Data"
    script_path = r"C:\Users\neo_1\Dropbox\Projects\Programing\PegeFroggitAPI"
else:
    data_path = "/volume1/homes/Pege_admin/Python_scripts"
    script_path = "/volume1/python_scripts/PegeFroggitAPI"

sql_file = "pege_db.sqlite"
conf_file = "confidential.txt"

sql_path = os.path.join(data_path, sql_file)
conf_path = os.path.join(script_path, conf_file)
log_file_path = os.path.join(script_path, 'log/main.log')

logger = logging.getLogger()
if synology == False:
   logger.setLevel(logging.INFO)
else:
  logger.setLevel(logging.DEBUG)
fhandler = logging.FileHandler(filename = log_file_path, mode = 'a')
formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', '%d-%m-%Y %H:%M:%S')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)

logging.info('Start of program')

#==============================================================
#   FUNCTIONS
#==============================================================

# Script to retrieve API access token
def get_token():
    print("Retrieving access token...")
    access_token_url = 'https://api.ecowitt.net/api/token?grant_type=client_credential&appid='+conf[3]+'&secret='+conf[4]
    html = urlopen(access_token_url).read()
    access_token_json = json.loads(html)
    access_token = access_token_json['access_token']
    logging.info('Access token provided successfully!')
    return(access_token)

# Script to get JSON file for real time weather data
def get_data():
    print("Retrieving json file...")
    realtime_url="https://api.ecowitt.net/api/devicedata/real_time?access_token="+get_token()+"&openid="+conf[5]+"&lang=en&call_back=all"
    realtime_datafile = urlopen(realtime_url).read().decode()
    realtime_data = json.loads(realtime_datafile)
    logging.info('Json file available!')
    if synology == False:
        save_json = open(os.path.join(data_path, "froggit.json"), "w+")
        json.dump(realtime_data, save_json)
        save_json.close()
        logging.info('PEGE_FROGGIT: JSON file stored locally')
    return(realtime_data)

def get_timestamp():
    timestamp=datetime.utcfromtimestamp(int(realtime_data['time'])).strftime('%Y-%m-%d %H:%M:%S')
    logging.info('Timestamp: ' + timestamp)
    return(timestamp)

def slice_data(l1, l2, l3='value'):
    slice = realtime_data['data'][l1][l2][l3]
    return(slice)

# Check connection Pege Froggit (loop through data categories to find outdoor data)
def check_connection():
    outdoor_data = 0
    for i in realtime_data['data']:
        if  i == "outdoor":
            outdoor_data = outdoor_data + 1
    if outdoor_data == 0:
        ml.send_mail("PEGE FROGGIT API - Alert", "Pege Froggit connection issue", conf[2])
        logging.error("Alert: Pege Froggit connection issue")

#==============================================================
#   SCRIPT
#==============================================================

# Get data from confidential file
conf = []
with open(conf_path) as f:
    for line in f:
        conf.append(line.replace("\n",""))

# Prepare JSON data
try:
    realtime_data = get_data()
    timestamp = get_timestamp()
except:
    logging.error('Pege froggit data could not be retrieved')
    ml.send_mail("PEGE FROGGIT API - Alert", "Pege froggit data could not be retrieved", conf[2])

# Store data in variables
try:
    # Indoor data
    indoor_temp_data=round((float(slice_data('indoor', 'temp'))-32)*(5/9),1)
    indoor_humidity_data=slice_data('indoor','humidity')

    # Pressure data
    rel_pressure_data=round(float(slice_data('pressure','baromrelin'))*33.86389,1)
    abs_pressure_data=round(float(slice_data('pressure','baromabsin'))*33.86389,1)

    # Outdoor data
    outdoor_temp_data=round((float(slice_data('outdoor','temp'))-32)*(5/9),1)
    outdoor_humidity_data=slice_data('outdoor','humidity')

    # Wind data
    wind_dir_data=int(slice_data('wind','winddir'))
    if slice_data('wind','windspeedmph', 'unit') == "mph":
        wind_speed_data=round(float(slice_data('wind','windspeedmph'))*1.60934,1)
        wind_gust_data=round(float(slice_data('wind','windgustmph'))*1.60934,1)
    else:
        wind_speed_data=round(float(slice_data('wind','windspeedmph')),1)
        wind_gust_data=round(float(slice_data('wind','windgustmph')),1)

    # Solar data
    if slice_data('so_uv','solarradiation', 'unit') == "W/m\u00b2":
        solar_radiation_data=round(float(slice_data('so_uv','solarradiation'))/0.0079,0)
    else:
        solar_radiation_data=round(float(slice_data('so_uv','solarradiation')),0)
    solar_uv_data=int(slice_data('so_uv','uv'))

    # Rain data
    rain_rate_data=round(float(slice_data('rain','rainratein'))*25.4,1)
    rain_event_data=round(float(slice_data('rain','eventrainin'))*25.4,1)
    rain_hourly_data=round(float(slice_data('rain','hourlyrainin'))*25.4,1)
    rain_daily_data=round(float(slice_data('rain','dailyrainin'))*25.4,1)
    rain_weekly_data=round(float(slice_data('rain','weeklyrainin'))*25.4,1)
    rain_monthly_data=round(float(slice_data('rain','monthlyrainin'))*25.4,1)

    logging.info('Data retrieval succes')
                 
except:
    ml.send_mail('PEGE FROGGIT API - Alert', 'Data could not be retrieved', conf[2])
    logging.error('Data could not be retrieved')

# Save data
try:
    conn = sqlite3.connect(sql_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO pege_froggit_weather_data (timestamp, indoor_temp_data, indoor_humidity_data, rel_pressure_data, abs_pressure_data, outdoor_temp_data, outdoor_humidity_data,wind_dir_data,wind_speed_data,wind_gust_data,solar_radiation_data,solar_uv_data,rain_rate_data,rain_event_data,rain_hourly_data,rain_daily_data,rain_weekly_data,rain_monthly_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (timestamp, indoor_temp_data, indoor_humidity_data, rel_pressure_data, abs_pressure_data, outdoor_temp_data, outdoor_humidity_data,wind_dir_data,wind_speed_data,wind_gust_data,solar_radiation_data,solar_uv_data,rain_rate_data,rain_event_data,rain_hourly_data,rain_daily_data,rain_weekly_data,rain_monthly_data))
    conn.commit()
except:
    ml.send_mail("PEGE FROGGIT API - Alarm", "Data could not be stored", conf[2])
    logging.error('Pege Froggit data could not be stored')

check_connection()