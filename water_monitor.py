#libraries
import RPi.GPIO as GPIO
import time
import math
import pyrebase
import board
import digitalio
import busio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

config = {
	"apiKey": "AIzaSyCEyn6ZAnY2twiLo_P9vi5nlBC6rZS1G7o",
    	"authDomain": "pondmonitoringsystem.firebaseapp.com",
    	"databaseURL": "https://pondmonitoringsystem.firebaseio.com",
    	"projectId": "pondmonitoringsystem",
    	"storageBucket": "pondmonitoringsystem.appspot.com"
}

firebase = pyrebase.initialize_app(config)
print('app initialized')

auth = firebase.auth()
db = firebase.database()

user = auth.sign_in_with_email_and_password("theresacantiveros@gmail.com", "theresa13")

print('user authenticated')


#GPIO MODE (BOARD/BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
#set GPIO direction (IN/OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
refreshCycle = 1

DS18B20="/sys/bus/w1/devices/28-0417c41707ff/w1_slave"

_neutralVoltage = 1500.0
_acidVoltage = 2032.44

spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P0)

temp_values = []
dist_values = []
ph_values = []

time_elapsed = 0;

def stream_handler(message):
    global refreshCycle
    refreshCycle = int(message["data"]) 

def getPh(voltage):
    slope = (7.00 - 4.00)/((_neutralVoltage - 1500.0) / 3.0 - (_acidVoltage - 1500.0) / 3.0)
    intercept = 7.0 - slope*(_neutralVoltage - 1500.0)/3.0
    _phValue = slope*((voltage*1000)-1500.0)/3.0+intercept

    return round(_phValue,2)

def getTemperature():

    f = open(DS18B20,"r")
    data = f.read()
    f.close()

    (discard, sep, reading) = data.partition(' t=')

    t = float(reading) / 1000.0

    return t

def distance():
    #set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    #set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    #save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    #save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    #time difference between start and arrival
    TimeElapsed = StopTime - StartTime

    #multiply with the sonic speed (34300 cm/s)
    #and divide by 2, because there and back
    distance =(TimeElapsed * 34300) / 2

    return distance

if __name__ == '__main__':
    mystream = db.child("sensor/refresh").stream(stream_handler)
    try:
        
        while True:
            if (time_elapsed >= refresh_cycle):
                totalTemp = 0
                totalDist = 0
                totalPh = 0

                for temp in temp_values:
                    totalTemp += temp
                ave_temp = totalTemp / refresh_cycle
                print('ave temp', ave_temp)
                db.child("sensor/result/temperature").set(str(ave_temp), user['idToken'])


                for dist in dist_values:
                    totalDist += dist
                ave_dist = totalDist / refresh_cycle
                print('ave dist', ave_dist)
                db.child("sensor/result/ultrasonic").set(ave_dist, user['idToken'])   

                for ph in ph_values:
                    totalPh += ph
                ave_ph = totalPh / refresh_cycle
                print('ave ph', ave_ph)
                db.child("sensor/result/pH").set(str(ave_ph), user['idToken'])

                time_elapsed = 0
                del temp_values[:]
                del dist_values[:]
                del ph_values[:]

            else:
                dist = distance()
                distStr = "{:.1f}".format(dist)
                print("formatted: ", distStr)
                print("Measured Distance = %.1f cm" %dist)

                temp = getTemperature()
                print("Temperature Value = ", temp)

                ph = getPh(chan.voltage)
                print('volt: ', str(chan.voltage))
                print('PH: ', ph)
                
                time_elapsed += 1
                        
            time.sleep(refreshCycle)

        #Reset by pressing CTRL C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        mystream.close()
        GPIO.cleanup()

        

