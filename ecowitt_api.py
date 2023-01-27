# Program to retrieve data from ecowitt weather station via AppID
# Version 1.0.0

# Documentation on API: https://doc.ecowitt.net/web/#/1?page_id=11
# Device developer information: https://api.ecowitt.net/index/user/mydevice.html

import json
from urllib.request import urlopen
import sqlite3
from datetime import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#==============================================================
#   PARAMETERS
#==============================================================

# Test parameter (if test local, else synology)
test = False

# Filepaths
if test == True:
    data_path = r"C:\Users\neo_1\Dropbox\Projects\Programing\PegeFroggitAPI\Data"
    script_path = r"C:\Users\neo_1\Dropbox\Projects\Programing\PegeFroggitAPI"
else:
    data_path = "/volume1/homes/Pege_admin/Python_scripts"
    script_path = "/volume1/python_scripts/PegeFroggitAPI"

sql_file = "pege_db.sqlite"
conf_file = "confidential.txt"

sql_path = os.path.join(data_path, sql_file)
conf_path = os.path.join(script_path, conf_file)

#==============================================================
#   FUNCTIONS
#==============================================================

# Script to retrieve API access token
def get_token():
    print("Retrieving access token...")
    access_token_url = 'https://api.ecowitt.net/api/token?grant_type=client_credential&appid='+AppID+'&secret='+AppSecret
    html = urlopen(access_token_url).read()
    access_token_json = json.loads(html)
    access_token = access_token_json['access_token']
    print("Access token provided successfully!")
    return(access_token)

# Script to get JSON file for real time weather data
def get_data():
    print("Retrieving json file...")
    realtime_url="https://api.ecowitt.net/api/devicedata/real_time?access_token="+access_token+"&openid="+OpenID+"&lang=en&call_back=all"
    realtime_datafile = urlopen(realtime_url).read().decode()
    realtime_data = json.loads(realtime_datafile)
    print("Json file available!")
    if test == True:
        save_json = open(os.path.join(data_path, "froggit.json"), "w+")
        json.dump(realtime_data, save_json)
        save_json.close()
        send_alarm("PEGE_FROGGIT: JSON file stored locally", recipient)
    return(realtime_data)

def get_timestamp():
    timestamp=datetime.utcfromtimestamp(int(realtime_data['time'])).strftime('%Y-%m-%d %H:%M:%S')
    return(timestamp)

def slice_data(l1, l2, l3='value'):
    slice = realtime_data['data'][l1][l2][l3]
    return(slice)

# Check connection Pege Froggit (loop thorugh data categories to find outdoor data)
def check_connection():
    outdoor_data=0
    for i in realtime_data['data']:
        if  i == "outdoor":
            outdoor_data=outdoor_data+1
    if outdoor_data == 0:
        send_alarm("Alert: Pege Froggit connection issue", recipient)

# Send Mail
def send_alarm(subject, recipient):
    host = "smtp-mail.outlook.com"
    port = 587
    password = confidential[1]
    sender = confidential[0]
    email_conn = smtplib.SMTP(host,port)
    email_conn.ehlo()
    email_conn.starttls()
    email_conn.login(sender, password)
    the_msg = MIMEMultipart("alternative")
    the_msg['Subject'] = subject 
    the_msg["From"] = sender
    the_msg["To"] = recipient
    # Create the body of the message
    message = """<html>
                    <head>
                        <title></title>
                    </head>
                    <body></body>
                </html>"""
    part = MIMEText(message, "html")
    # Attach parts into message container.
    the_msg.attach(part)
    email_conn.sendmail(sender, recipient, the_msg.as_string())
    email_conn.quit()

#==============================================================
#   SCRIPT
#==============================================================

# Get data from confidential file
confidential = []
with open(conf_path) as f:
    for line in f:
        confidential.append(line.replace("\n",""))

recipient = confidential[2]
AppID = confidential[3]
AppSecret = confidential[4]
OpenID = confidential[5]

# Prepare JSON data
try:
    access_token = get_token()
    realtime_data = get_data()
    timestamp = get_timestamp()
except:
    print("Pege froggit data could not be retrieved")
    send_alarm("ALERT: Pege froggit data could not be retrieved", recipient)

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

    print("Data retrieval succes")
except:
    send_alarm("Data could not be retrieved", recipient)
    print("ALERT: Pege Froggit data could not be retrieved")

# Save data
try:
    conn = sqlite3.connect(sql_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO pege_froggit_weather_data (timestamp, indoor_temp_data, indoor_humidity_data, rel_pressure_data, abs_pressure_data, outdoor_temp_data, outdoor_humidity_data,wind_dir_data,wind_speed_data,wind_gust_data,solar_radiation_data,solar_uv_data,rain_rate_data,rain_event_data,rain_hourly_data,rain_daily_data,rain_weekly_data,rain_monthly_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (timestamp, indoor_temp_data, indoor_humidity_data, rel_pressure_data, abs_pressure_data, outdoor_temp_data, outdoor_humidity_data,wind_dir_data,wind_speed_data,wind_gust_data,solar_radiation_data,solar_uv_data,rain_rate_data,rain_event_data,rain_hourly_data,rain_daily_data,rain_weekly_data,rain_monthly_data))
    conn.commit()
except:
    send_alarm("Data could not be stored", recipient)
    print("ALERT: Pege Froggit data could not be stored")

check_connection()