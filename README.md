# DomoticzDirektWetter
  Import Weather Station WD2000 to Domoticz, Technoline, ALDI 

  Dev still on going, missing Temperature_Calendar (lot of work to get min, avg and max value / day since all values are hourly)  and number of days to import (take all history)
  
  To save batteries, the station WD2000 connects to the Wifi only once per hour (if not connected with the USB cable to power supply). 
  The values are updated every 57 secondes with the USB power supply, the Wifi stays always on in that situation.

# Pre-requisit : 

  You must have installed the smartphone application DirektWetter (Android or iOS), fully setup your Weather Station WD2000, including the user registration.
  And be sure that you have information uploaded from your station in the application.
  This information are coming from cloud.technoline.info and DomoticzDirektWetter is using json API to get values.

  Note: This script is largely inspired by https://github.com/Scrat95220/DomoticzGazpar with the same approach.

# create devices in Domoticz
- In Domoticz, go to Setup/hardware, add or reuse a Dummy Hardware (Does nothing, use for virtual switches only)
  then create a virtual sensor "Temp+Hum+Baro" for the Station.
  then create another virtual sensor "Temp+Hum" for the external temp/hum sensor.
  
- Then in Setup/Devices, add them to the devices. Mark down the idx to setup in the cfg file.

## modules to install - linux

    sudo apt-get install python3 python3-dateutil python3-requests
    cd /home/pi/domoticz/scripts/python
    git clone https://github.com/ProfBoc75/DomoticzDirektWetter.git

### rename configuration file, change settings

    cp _domoticz_direktwetter.cfg domoticz_direktwetter.cfg
    nano domoticz_direktwetter.cfg

and change:
```
   [DIREKTWETTER]
   # Username and password that you used to register your DirektWetter Application from Android or iOS
   USERNAME=youremailaddress@domain.com
   PASSWORD=mypassword
   NB_DAYS_IMPORTED=10

   [DOMOTICZ]
   # Domoticz index at least station and sensor1, leave blank others if not yet created
   devicerowidstation=domoticz_idx_number_for_station_temp_hum_barometer
   devicerowidsensor1=idx_number
   devicerowidsensor2=idx_number
   devicerowidsensor3=idx_number

   [SETTINGS]
   # Path to your domoticz.db file
   DB_PATH=/home/pi/domoticz
```   
NB_DAYS_IMPORTED is not yet implemented, here for future updates.

Configuration file will not be deleted in future updates.

## testing launch

Manually launch

    cd /home/pi/domoticz/scripts/python/DomoticzDirektWetter
    chmod +x direktwetter.py
    ./direktwetter.py

Then check missing python modules and the login credential if they are ok:

    DomoticzDirektWetter.log

Go to to your Domoticz web site and check that the both Temperature Devices are updated.

## To get all History

    Uncomment the 2 lines at the end of the script (to be improved later with NB_DAY_IMPORTED)
        #getHistory(token)
        #logging.info("getHistory values successfully!")

## Add to your cron tab (with crontab -e): 

Will start every hour at 2 , not before to let the station updates hourly values in the Cloud (under batteries)

    2 * * * * /usr/bin/python3 /home/pi/domoticz/scripts/python/DomoticzDirektWetter/direktwetter.py >/dev/null 2>&1

Will start every minute (with USB Power Supply)

    * * * * * /usr/bin/python3 /home/pi/domoticz/scripts/python/DomoticzDirektWetter/direktwetter.py >/dev/null 2>&1

## Known Issues:

In Domoticz, the virtual sensors are selves updated every 5 mn by Domoticz to add Dewpoint but unfortunatly this may add wrong values like sawtooth. I will try to update sensors with the Domoticz json/AP (hope soon) to see if any improvement here.
