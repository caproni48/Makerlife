import http.client, urllib
import threading
from time import time, sleep, strftime
from gpiozero import DigitalInputDevice
from w1thermsensor import W1ThermSensor
import math
import datetime
import time

sleep = 60 # how many seconds to sleep between posts to the channel
key = 'PUT_YOUR_API_READ_KEY_HERE'  # Thingspeak channel to update

rainfall = 0
wind_count = 0
bucket_count = 0
radius_cm = 9.0
interval = 5
ADJUSTMENT = 1.18
CM_IN_A_KM = 100000.0
CM_IN_A_M = 100.0
SECS_IN_AN_HOUR = 3600
BUCKET_SIZE = 0.2794
now = datetime.datetime.now()

sensor = W1ThermSensor()
wind_speed_sensor = DigitalInputDevice(17, pull_up=True)
rain_sensor = DigitalInputDevice(27, pull_up=True)


def wind(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0
    wind_count = 0

    dist_m = (circumference_cm * rotations) / CM_IN_A_M

    m_per_sec = dist_m / time_sec
    #m_per_hour = m_per_sec * SECS_IN_AN_HOUR

    return m_per_sec * ADJUSTMENT

def spin():
    global wind_count
    wind_count = wind_count + 1
 
def rain():
    global rainfall 
    global bucket_count
    bucket_count = bucket_count + 1
    rainfall = (bucket_count * BUCKET_SIZE - BUCKET_SIZE)

def temperature():
    while True:
        print (datetime.datetime.now().time()) 
        temp = sensor.get_temperature()
        time.sleep(1)

windspeed = threading.Thread(name='wind', target=wind(interval))
raindata = threading.Thread(name='rain', target=rain)
tempdata = threading.Thread(name='temperature', target=temperature)

windspeed.start()
raindata.start()
tempdata.start()

wind_speed_sensor.when_activated = spin
rain_sensor.when_activated = rain

def weather():
    while True:
        temp = sensor.get_temperature()
        wind_speed_sensor.when_activated = spin
        params = urllib.parse.urlencode({'field1': temp, 'field2': rainfall, 'field3': wind(interval),'key':key })
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = http.client.HTTPConnection("api.thingspeak.com:80")
        try:
            conn.request("POST", "/update", params, headers)
            response = conn.getresponse()
            print (temp)
            print (wind(interval))
            print(rainfall)
            print (response.status, response.reason)
            data = response.read()
            conn.close()
        except:
            print ("Connection failed")
            
        break
if __name__ == "__main__":
        while True:
            weather()
            time.sleep(sleep)
                
                

