#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) 2022 02 28 ProfBoc75
"""Generates weather JSON files from DirektWetter data
collected via their  website cloud.technoline.info (API).
"""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import configparser
import sqlite3
import os
import requests
from datetime import datetime  
from datetime import timedelta
from time import time
import logging
import sys
import json
import hashlib
import dateutil.parser
from dateutil.relativedelta import relativedelta

#Extract from direktwetter apk android app "com.dis.direktwetter.net/Constant"
BASE_URL = 'https://cloud.technoline.info:8443/V1.0/'
API_ADD_MEMBER = "weather/setUser";
API_ALARM_GET = "weather/getAlarm";
API_ALARM_SETTING = "weather/setAlarm";
API_BIND = "weather/bind";
API_DELETE = "account/removeUser";
API_DEVICE = "weather/getBindedDevice";
API_HISTORY = "weather/devData/getRecord";
API_HOME = "weather/devData/getRealtime";
API_LOCATION_GET = "weather/getLocation";
API_LOCATION_SETTING = "weather/setLocation";
API_LOGIN = "account/login";
API_MEMBER = "weather/getUser";
API_MODE = "weather/setMode";
API_NEARBYS_LOCATION = "weather/devData/getNearby";
API_REG = "account/reg";
API_REMOVE_MEMBER = "weather/removeUser";
API_RESET = "account/resetPwd";
API_UNDBIND = "weather/unbind";
API_UNIT_GET = "weather/getUnit";
API_UNIT_SETTING = "weather/setUnit";
API_UPDATE = "account/update";
API_UPDATE_FCM_TOKEN = "weather/updateFcmToken";
API_YAHOO = "weather/netData/getForecast";

tempUnit = 0   #means Farenheit temp value can be get from cloud not yet implemented

# from com.dis.direktwetter.base/BasePresenter
md5key = "emax@pwd123"

userName = ""
password = ""
devicerowidstation = ""     #Domoticz type Temp, Hum, Baro
devicerowidsensor1 = ""     #Domoticz type Temp, Hum
devicerowidsensor2 = ""     #Domoticz type Temp, Hum
devicerowidsensor3 = ""     #Domoticz type Temp, Hum

#Type 1 = Temp F (curVal, highVal, lowVal)
#Type 2 = Hum % (curVal, highVal, lowVal)
#Type 3 = devWindVal (Wind)
#Type 4 = devRainfullVals (Rain)
#Type 5 = devNoiseVals (Noise)
#Type 6 = devLighVals (Lux)
#Type 7 = curVal ( = Baro) Channel 99 only
#Channel 0 = Station
#Channel 1 = Sensor 1
#Channel 2 = Sensor 2
#Channel 3 = Sensor 3
#Channel 99 = Nothing except Baro for type 7

nbDaysImported = 30
dbPath = ""

script_dir=os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class DirektWetterServiceException(Exception):
    """Thrown when the webservice threw an exception."""
    pass

def login():
    """Logs the user into the cloud technoline API.
    """
    global emaxToken
    session = requests.Session()
    #Password is md5 encrypted with userpassword + md5key value
    str2hash = password+md5key
    result = hashlib.md5(str2hash.encode())
    pwd = result.hexdigest().upper()
    payload = {
               "email": userName,
               "pwd": pwd
               }
    headers = {
                'Content-Type': 'application/json; charset=utf-8',
              }
    json_payload = json.dumps(payload) 
    resp_Login = session.post(BASE_URL+API_LOGIN, data=json_payload, headers=headers, verify=False)
    if resp_Login.status_code != requests.codes.ok:
        print("Login call - error status :"+resp_Login.status_code+'\n');

    resp_Login_dict = json.loads(resp_Login.text)
    content_dict = resp_Login_dict["content"]
    emaxToken = content_dict["token"]
    openid = content_dict["openid"]

    return session

def getRealtime(session):

    headers = {
                'emaxToken': emaxToken
              }

    global req_date
		  
    resp_Realtime = session.get(BASE_URL+API_HOME, headers=headers)
    if resp_Realtime.status_code != requests.codes.ok:
        print("getRealtime - error status :",resp_Realtime.status_code,'\n');
    resp_Realtime_dict = json.loads(resp_Realtime.text)
    #print(resp_Realtime_dict)
    content_dict = resp_Realtime_dict["content"]
    sensorDatas_dict = content_dict["sensorDatas"]
    req_date = dateutil.parser.isoparse(content_dict["updateTime"]) + timedelta(hours=1)
    req_date = req_date.strftime('%Y-%m-%d %H:%M:%S')

    getData(sensorDatas_dict)

def getHistory(session):
    headers = {
                'emaxToken': emaxToken
              }
    global req_date
    # First pass to get 50 first id , then depends on the date ... end if last page reached = 1
    # First Get /V1.0/weather/devData/getRecord?sortDirection=ASC&size=50&startTime=0&page=0&endTime=1645980991  (=today int(timestamp))
    
    """
    Temperature_Calendar not yet implemented for history, it needs to add min avg max daily values --> May be another approach to get history day by day instead of all days by 50 metric pages.
    nbDaysImported not yet implemented
    """
    
    start = 0
    getAll = 'False'
    timestamp_now = int(time())
    print(timestamp_now)
    
    while ( getAll == 'False' ):
    
        resp_History = session.get(BASE_URL+API_HISTORY+"?sortDirection=ASC&size=50&startTime="+str(start)+"&page=0&endTime="+str(timestamp_now), headers=headers)
        if resp_History.status_code != requests.codes.ok:
            print("getHistory - error status :",resp_History.status_code,'\n');
        resp_History_dict = json.loads(resp_History.text)
        content_dict = resp_History_dict["content"]
        data_list = content_dict["data"]
        for data in range(len(data_list)):
            data_dict = data_list[data]
            sensorDatas_list = data_dict["sensorDatas"]
            req_date = dateutil.parser.isoparse(data_dict["updateTime"]) + timedelta(hours=1)
            req_date = req_date.strftime('%Y-%m-%d %H:%M:%S')
            #print(req_date)
            #print(sensorDatas_list)
            getData(sensorDatas_list)
        start = int(datetime.timestamp(datetime.fromisoformat(req_date)))
        if ( content_dict['page']['totalPages'] == 1):
            getAll = 'True'
                    
        
def getData(sensorDatas):
    #Type 1 = Temp , type 2 = % Hum, type 7 = Baro
    #channel = 0 = Station
    
    haveSensor1 = 'False'
    haveSensor2 = 'False'
    haveSensor3 = 'False'
    
    for data in range(len(sensorDatas)):
        sensorDatas_dict = sensorDatas[data]
        #Station
        if (sensorDatas_dict['type'] == 1 and sensorDatas_dict['channel'] == 0):
            station_temp = sensorDatas_dict['curVal']
        if (sensorDatas_dict['type'] == 2 and sensorDatas_dict['channel'] == 0):
            station_hum = sensorDatas_dict['curVal']
        if (sensorDatas_dict['type'] == 7 and sensorDatas_dict['channel'] == 99):
            station_baro = sensorDatas_dict['curVal']
        #Sensor 1
        if (sensorDatas_dict['type'] == 1 and sensorDatas_dict['channel'] == 1):
            sensor1_temp = sensorDatas_dict['curVal']
        if (sensorDatas_dict['type'] == 2 and sensorDatas_dict['channel'] == 1):
            sensor1_hum = sensorDatas_dict['curVal']
            
        #Sensor 2
        if (sensorDatas_dict['type'] == 1 and sensorDatas_dict['channel'] == 2):
            sensor2_temp = sensorDatas_dict['curVal']
        if (sensorDatas_dict['type'] == 2 and sensorDatas_dict['channel'] == 2):
            sensor2_hum = sensorDatas_dict['curVal']
        #Sensor 3
        if (sensorDatas_dict['type'] == 1 and sensorDatas_dict['channel'] == 3):
            sensor3_temp = sensorDatas_dict['curVal']
        if (sensorDatas_dict['type'] == 2 and sensorDatas_dict['channel'] == 3):
            sensor3_hum = sensorDatas_dict['curVal']

    # if temp = 65535.0 and hum = 255.0 then sensor does not exist
    if (sensor1_temp+sensor1_hum != 65790):
        haveSensor1 = 'True'
    if (sensor2_temp+sensor2_hum != 65790):
        haveSensor2 = 'True'
    if (sensor3_temp+sensor3_hum != 65790):
        haveSensor3 = 'True'

    # if tempUnit = 0 needs to convert into Celcius
    if (tempUnit == 0):
        station_temp = (station_temp - 32 ) * 5 / 9
        sensor1_temp = (sensor1_temp - 32 ) * 5 / 9
        sensor2_temp = (sensor2_temp - 32 ) * 5 / 9
        sensor3_temp = (sensor3_temp - 32 ) * 5 / 9

    channel = 0
    setDomoticz(devicerowidstation,channel,station_temp,station_hum,station_baro)
        
    if haveSensor1 == 'True':
        channel = 1
        setDomoticz(devicerowidsensor1,channel,sensor1_temp,sensor1_hum)

    if haveSensor2 == 'True':
        channel = 2
        setDomoticz(devicerowidsensor2,channel,sensor2_temp,sensor2_hum)
    
    if haveSensor3 == 'True':
        channel = 3
        setDomoticz(devicerowidsensor3,channel,sensor3_temp,sensor3_hum)
 
def setDomoticz(idx,channel,temp,hum,baro=True):
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Temperature format : DeviceRowID,Temperature,Chill,Humidity,Barometer,DewPoint,SetPoint,Date
    if channel == 0:
        sql ='DELETE FROM \'Temperature\' WHERE devicerowid='+str(idx)+' and date = \''+req_date+'\';INSERT INTO \'Temperature\' (DeviceRowID,Temperature,Chill,Humidity,Barometer,DewPoint,SetPoint,Date) VALUES ('+str(idx)+', \''+str("{:0.1f}".format(temp))+'\', \''+str(0)+'\', \''+str("{:0.1f}".format(hum))+'\', \''+str("{:0.0f}".format(baro))+'\', \''+str(0)+'\', \''+str(0)+'\', \''+req_date+'\');\n'
        sqlUpdate(sql)
        sql ='UPDATE DeviceStatus SET lastupdate = \''+today+'\', sValue = \''+str("{:0.1f}".format(temp))+';'+str("{:0.1f}".format(hum))+';1;'+str("{:0.0f}".format(baro))+';1\' WHERE id = '+str(idx)+';'
        sqlUpdate(sql)
        
    if channel in range(1,3):
        sql ='DELETE FROM \'Temperature\' WHERE devicerowid='+str(idx)+' and date = \''+req_date+'\';INSERT INTO \'Temperature\' (DeviceRowID,Temperature,Chill,Humidity,Barometer,DewPoint,SetPoint,Date) VALUES ('+str(idx)+', \''+str("{:0.1f}".format(temp))+'\', \''+str(0)+'\', \''+str("{:0.1f}".format(hum))+'\', \''+str(0)+'\', \''+str(0)+'\', \''+str(0)+'\', \''+req_date+'\');\n'
        sqlUpdate(sql)
        sql ='UPDATE DeviceStatus SET lastupdate = \''+today+'\', sValue = \''+str("{:0.1f}".format(temp))+';'+str("{:0.1f}".format(hum))+';1\' WHERE id = '+str(idx)+';'
        sqlUpdate(sql)
        
def sqlUpdate(sql):
    con = sqlite3.connect(dbPath+'/domoticz.db')
    cur = con.cursor()
    #print(sql)
    cur.executescript(sql)
    con.commit()
    cur.close()
    con.close()
 
def get_config():
    configuration_file = script_dir + '/domoticz_direktwetter.cfg'
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(configuration_file)
    global userName
    global password
    global devicerowidstation
    global devicerowidsensor1
    global devicerowidsensor2
    global devicerowidsensor3
    global nbDaysImported         #not yet implemented for future update
    global dbPath
    
    userName = config['DIREKTWETTER']['USERNAME']
    password = config['DIREKTWETTER']['PASSWORD']
    devicerowidstation = config['DOMOTICZ']['devicerowidstation']
    devicerowidsensor1 = config['DOMOTICZ']['devicerowidsensor1']
    devicerowidsensor2 = config['DOMOTICZ']['devicerowidsensor2']
    devicerowidsensor3 = config['DOMOTICZ']['devicerowidsensor2']
    nbDaysImported = config['DIREKTWETTER']['NB_DAYS_IMPORTED']
    dbPath = config['SETTINGS']['DB_PATH']
    
    #print("config : " + userName + "," + password + "," + devicerowidstation + "," + devicerowidsensor1 + "," + nbDaysImported + "," +dbPath )

# Main script 
def main():
    logging.basicConfig(filename=script_dir + '/DomoticzDirektWetter.log', format='%(asctime)s %(message)s', level=logging.INFO)

    try:
        logging.info("Get configuration")
        get_config()
        
        logging.info("logging in as %s...", userName)
        token = login()
        logging.info("logged in successfully!")
        getRealtime(token)
        logging.info("getRealtime values successfully!")

        """ Uncomment following 2 lines the fist time to get all history
        """
        #getHistory(token)
        #logging.info("getHistory values successfully!")
        
    except DirektWetterServiceException as exc:
        logging.error(exc)
        sys.exit(1)

if __name__ == "__main__":
    main()
