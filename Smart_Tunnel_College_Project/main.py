
import time
from machine import Pin, SPI
from mfrc522 import MFRC522
from time import sleep
from machine import Pin, I2C
from sh1106 import SH1106_I2C
import framebuf


PreviousCard = [0]
vehicles = dict()

sda = Pin(5, Pin.OUT)
rst = Pin(22, Pin.OUT)
spi = SPI(0, baudrate=100000)

button1 =  Pin(14, Pin.IN) #First touch button 
button2 = Pin(15, Pin.IN) #Second touch button

def sleep_ms(t):
        sleep(t/1000)
        
def readRFID():
    global PreviousCard
    
    reader =  MFRC522(spi, sda, rst)
    (stat, tag_type) = reader.request(reader.REQIDL)
    
    if stat == reader.OK:
        (stat, uid) = reader.anticoll()
        if uid == PreviousCard: # if we read the same card twice in a row, ignore it
            return
        if stat == reader.OK: # we got a valid card!
            idHex = hex(int.from_bytes(bytes(uid),"little",False)).upper() # convert unique ID to a 4-character string for easy account-keeping
            idString = idHex[-4:]
            PreviousCard = uid
            
            if idString in vehicles.keys(): # have we seen this vehicle before?
                vehicles[idString] += 1 # increment its bill by this many dollars
            else:
                vehicles[idString] = 1 # start a fresh bill
                
            print("Vehicle ID: {}   Trip count: {}".format(idString, vehicles[idString]))
        else:
            pass
    else:
        PreviousCard=[0]
        

def report():
    buttons = Pin(13,Pin.IN) #third touch button
    if buttons.value() ==1:
        # Trip report
        print("\n\n     Trip Report      ")
        print("-----------------------")
        print("Vehicle| Number of trips")
        for key in vehicles:
            print("{:7}| {}".format(key, vehicles[key]))
        print("\n")
        
def oledOutput1():
    global button1, button2
    leftState = button1
    rightState = button2
    i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
    oled = SH1106_I2C(128, 64, i2c)
    
    
    if rightState.value() == 1 and leftState.value() == 1:
            oled.fill(0)
            oled.text("Crash Ahead", 15,10)
            oled.text("Slow Down", 15,40)
            oled.show()
    else:
        oled.fill(0)
        oled.text("Drive Safely", 15, 10)
        if len(vehicles) > 0:
            oled.text("Trip Count: ",15,35)
            trips = vehicles.values()
            totalTrips = sum(trips)
            oled.text(str(totalTrips), 15,50)                
        oled.show()
    
        
        
while True:
    
    readRFID()
    
    report()
    
    oledOutput1()
    
    sleep_ms(50)
    
    
