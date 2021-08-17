'''

Assetto Corsa Python 3.3 script for physical light simulating F1 rear light.

The USB relay (SMAKN LCUS-1) required a CH340 serial driver into Win10.  I didn't scan
the COM ports so COM4 maybe different for you.  This USB relay is use to activate the light when required.

The serial library is verion 3.5 from pySerial from https://pyserial.readthedocs.io/

The light I'm using is same as 2021 F1 car.  More precisely a McLaren Rainlight-3.
I already confure that light via his CAN BUS including flashing rate or brigness.
Any other light can be used.  This will be up to you making it flash or not.

SymInfo library is mandatory for share memory usage with Assetto Corsa.

LeGuyTremblay@gmail.com
August 13, 2021

'''

import os
import sys
import math
import time
import ac
import acsys

import platform
if platform.architecture()[0] == "64bit":
  sysdir='apps/python/backLight/third_party/stdlib64'
else:
  sysdir='apps/python/backLight/third_party/stdlib'
sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."
sys.path.insert(len(sys.path), 'apps/python/backLight/third_party')
from sim_info import info

sys.path.insert(len(sys.path), 'apps/python/backLight/third_party/serial')
import serial

appWindows = 0
refreshCounter = 0 #Refresh delay counter

lightStatus = "OFF"
l_lightStatus = 0

chargeLevel = info.physics.kersCharge
l_chargeStatus = 0

l_pitLimiterStatus = 0

serialCon = serial.Serial(port = 'COM4', baudrate = 9600, timeout = 0)
maxRefreshCounter = 0

def acMain(ac_version):
    try:
        global appWindow, l_lightStatus, l_chargeStatus, l_pitLimiterStatus
        ac.log("called Backlight acMain()")

        appWindow=ac.newApp("BackLight")
        ac.setSize(appWindow,200,200)
        ac.drawBorder(appWindow,0)
        ac.setBackgroundOpacity(appWindow,0)

        l_lightStatus = ac.addLabel( appWindow, "Back Light : ")
        ac.setPosition(l_lightStatus, 3, 30)

        l_chargeStatus = ac.addLabel(appWindow, "Charge : ")
        ac.setPosition(l_chargeStatus, 3, 45)

        l_pitLimiterStatus = ac.addLabel(appWindow, "Pit Limiter : ")
        ac.setPosition(l_pitLimiterStatus, 3, 60)

        return "BackLight"

    except Exception as e:
        ac.console("BackLight: Error in function acMain(): %s" % e)
        ac.log("BackLight: Error in function acMain(): %s" % e)


def acUpdate(deltaT):
    try:
        global ac, acsys, refreshCounter, info, lightStatus, chargeLevel, maxRefreshCounter

        # Must check kersCharge
        latestChargeLevel = info.physics.kersCharge

        if refreshCounter >= maxRefreshCounter:
            refreshCounter = 0

#       Old FIA rule 22.12 specify cars with intermediate or rain tires must have the rear light activated.
#       Unfortunatly today info.graphics.tyreCompound does't offer those kind of compound with all F1 cars.
#       This if why I'm using ac.ext_rainParams() instead to simulate it.
#       No needs to pit to see that change.

            RainParams = ac.ext_rainParams()  # get current rain/wipers state from patch

            if RainParams[0] > 0:
            # Rain on the track.
#            ac.console("rain rain rain")
                blPutLightON()
                maxRefreshCounter = 55
            elif ( latestChargeLevel > chargeLevel):
                #KERS charging
#            ac.console("KERS Recharging")
                blPutLightON()
                chargeLevel = latestChargeLevel
                maxRefreshCounter = 15
            elif (info.graphics.isInPit == 1):
#            ac.console("******** PIT *******")
                blPutLightON()
                maxRefreshCounter = 5
            elif (info.physics.pitLimiterOn == 1):
#            ac.console("-------- Pit Limiter --------")
                blPutLightON()
                maxRefreshCounter = 5
            elif (info.physics.speedKmh > 80):
                blPutLightOFF()
#           ac.console("OFF")
        else:
            refreshCounter = refreshCounter + 1

        chargeLevel = latestChargeLevel
        ac.setText(l_lightStatus, "Back Light : " + str( lightStatus ) )
        ac.setText(l_chargeStatus, "Charge :" + str( round (chargeLevel * 100, 1 ) ) + '%' )
        ac.setText(l_pitLimiterStatus, "Pit Limiter : " + str( info.physics.pitLimiterOn ) )

    except Exception as e:
        ac.console("BackLight: Error in function acUpdate(): %s" % e)
        ac.log("BackLight: Error in function acUpdate(): %s" % e)

def blPutLightOFF():
    try:
        global lightStatus, serialCon
        if lightStatus != "OFF":
            lightStatus = "OFF"
            serialCon.write(bytearray.fromhex("A0 01 01 A2"))   # USB Relay ON

    except Exception as e:
        ac.console("BackLight: Error in function blPutLightOFF(): %s" % e)
        ac.log("BackLight: Error in function blPutLightOFF(): %s" % e)

def blPutLightON():
    try:
        global lightStatus, serialCon
        if lightStatus != "ON":
            lightStatus = "ON"
            serialCon.write(bytearray.fromhex("A0 01 00 A1"))   # USB Relay OFF

    except Exception as e:
        ac.console("BackLight: Error in function blPutLightON(): %s" % e)
        ac.log("BackLight: Error in function blPutLightON(): %s" % e)

def acShutdown():
    try:
        ac.log("called Backlight acShutdown()")
        blPutLightOFF()
        serialCon.close()

    except Exception as e:
        ac.console("BackLight: Error in function acShutdown(): %s" % e)
        ac.log("BackLight: Error in function acShutdown(): %s" % e)