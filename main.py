# Program to retrieve data from ecowitt weather station via AppID
# Version 2.0.0

import logging
import os
import sqlite3
from urllib.request import urlopen

from main import api
from main import confidential as cf
from main import notifier as nf

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
log_file_path = os.path.join(script_path, "log/main.log")

logger = logging.getLogger()
if synology == False:
   logger.setLevel(logging.INFO)
else:
  logger.setLevel(logging.DEBUG)
fhandler = logging.FileHandler(filename = log_file_path, mode = "a")
formatter = logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", "%d-%m-%Y %H:%M:%S")
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)

logging.info("Start of program")

subject = "PEGE FROGGIT API - Alert"

# Prepare JSON data
try:
    realtime_data = api.get_data()
    timestamp = api.get_timestamp()
except:
    error_message = "Pege froggit data could not be retrieved"
    logging.error(error_message)
    nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)

# Store data in variables
try:
    # Indoor data
    indoor_temp_data=round((float(api.slice_data("indoor", "temp"))-32)*(5/9),1)
    indoor_humidity_data=api.slice_data("indoor","humidity")

    # Pressure data
    rel_pressure_data=round(float(api.slice_data("pressure","baromrelin"))*33.86389,1)
    abs_pressure_data=round(float(api.slice_data("pressure","baromabsin"))*33.86389,1)

    # Outdoor data
    outdoor_temp_data=round((float(api.slice_data("outdoor","temp"))-32)*(5/9),1)
    outdoor_humidity_data=api.slice_data("outdoor","humidity")

    # Wind data
    wind_dir_data=int(api.slice_data("wind","winddir"))
    if api.slice_data("wind","windspeedmph", "unit") == "mph":
        wind_speed_data=round(float(api.slice_data("wind","windspeedmph"))*1.60934,1)
        wind_gust_data=round(float(api.slice_data("wind","windgustmph"))*1.60934,1)
    else:
        wind_speed_data=round(float(api.slice_data("wind","windspeedmph")),1)
        wind_gust_data=round(float(api.slice_data("wind","windgustmph")),1)

    # Solar data
    if api.slice_data("so_uv","solarradiation", "unit") == "W/m\u00b2":
        solar_radiation_data=round(float(api.slice_data("so_uv","solarradiation"))/0.0079,0)
    else:
        solar_radiation_data=round(float(api.slice_data("so_uv","solarradiation")),0)
    solar_uv_data=int(api.slice_data("so_uv","uv"))

    # Rain data
    rain_rate_data=round(float(api.slice_data("rain","rainratein"))*25.4,1)
    rain_event_data=round(float(api.slice_data("rain","eventrainin"))*25.4,1)
    rain_hourly_data=round(float(api.slice_data("rain","hourlyrainin"))*25.4,1)
    rain_daily_data=round(float(api.slice_data("rain","dailyrainin"))*25.4,1)
    rain_weekly_data=round(float(api.slice_data("rain","weeklyrainin"))*25.4,1)
    rain_monthly_data=round(float(api.slice_data("rain","monthlyrainin"))*25.4,1)

    logging.info("Data retrieval succes")
                 
except:
    error_message = "Data could not be retrieved."
    nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)
    logging.error(error_message)

# Save data
try:
    conn = sqlite3.connect(sql_path)
    cur = conn.cursor()
    query = "INSERT INTO pege_froggit_weather_data (timestamp, indoor_temp_data"\
        ", indoor_humidity_data, rel_pressure_data, abs_pressure_data, "\
        "outdoor_temp_data, outdoor_humidity_data,wind_dir_data,wind_speed_data,"\
        "wind_gust_data,solar_radiation_data,solar_uv_data,rain_rate_data,"\
        "rain_event_data,rain_hourly_data,rain_daily_data,rain_weekly_data,"\
        "rain_monthly_data) "\
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    values = (timestamp, 
                indoor_temp_data, 
                indoor_humidity_data, 
                rel_pressure_data, 
                abs_pressure_data, 
                outdoor_temp_data, 
                outdoor_humidity_data,
                wind_dir_data,
                wind_speed_data,
                wind_gust_data,
                solar_radiation_data,
                solar_uv_data,
                rain_rate_data,
                rain_event_data,
                rain_hourly_data,
                rain_daily_data,
                rain_weekly_data,
                rain_monthly_data)
    cur.execute(query, values)
    conn.commit()
except:
    error_message = "Pege Froggit data could not be stored"
    nf.send_mail(subject, error_message, cf.MAIL_TO_MAIN)
    logging.error(error_message)

api.check_connection()