# DomoticzDirektWetter
  Import Weather Station WD2000 to Domoticz, Technoline, ALDI 

# Pre-requisit : 

  You must have installed the smartphone application DirektWetter (Android or iOS), fully setup your Weather Station WD2000, including the user registration.
  And be sure that you have information uploaded from your station in the application.
  This information are coming from cloud.technoline.info and DomoticzDirektWetter is using json API to get values.

  Note: This program is largely inspired by https://github.com/Scrat95220/DomoticzGazpar with the same approach.

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

## testing before launch

Manually launch

    chmod +x direktwetter.py
    ./direktwetter.py

Then check missing python modules and the login credential if they are ok:

    DomoticzDirektWetter.log

## Add to your cron tab (with crontab -e): (will start every hour at 5)

    5 * * * * /usr/bin/python3 /home/pi/domoticz/scripts/python/DomoticzDirektWetter/direktwetter.py >/dev/null 2>&1
