import time


DS18B20="/sys/bus/w1/devices/28-0417c41707ff/w1_slave"

r = 0

while True:

   r += 1

   f = open(DS18B20,"r")
   data = f.read()
   f.close()

   (discard, sep, reading) = data.partition(' t=')

   t = float(reading) / 1000.0

   print("{} {:.1f}".format(r, t))

   time.sleep(3.0)

   

