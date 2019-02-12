#libraries
import RPi.GPIO as GPIO
import time
import math
import pyrebase


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

def stream_handler(message):
    #print(message["event"])
    #print(message["path"])
    #print(message["data"])
    global refreshCycle
    refreshCycle = int(message["data"])
    print("ref1 ", refreshCycle)

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
    mystream = db.child("refresh").stream(stream_handler)
    try:
        
        while True:
            dist = distance()
            print("Measured Distance = %.1f cm" %dist)
            data = { "value": str(dist)}
            db.child("millivolt").set(data, user['idToken'])
            #print("ref cyc", str(refreshcycle))
            print("ref ", refreshCycle)
            time.sleep(refreshCycle)

        #Reset by pressing CTRL C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        mystream.close()
        GPIO.cleanup()

        
