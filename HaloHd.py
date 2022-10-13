# microbit-module: KitronikHaloHd@1.0.0
# Copyright (c) Kitronik Ltd 2022. 
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from microbit import button_a
from microbit import button_b
from microbit import display
from microbit import i2c
from microbit import pin0 #mic input
from microbit import pin8 #ZIP LEDs
from microbit import pin14 #buzzer
from microbit import pin19 #I2C
from microbit import pin20 #I2C
from neopixel import NeoPixel
from time import sleep
from music import play,stop,BA_DING
import gc
# Declare constants
LEDS_ON_HALO = 60
#SOUND_LEVEL_BASE is the average voltage level of the microphone at 1.65V converted to bytes
SOUND_LEVEL_BASE = 530
#globals for the alarm function
alarmHour =0
alarmMinute = 0
setAlarm = False

#A Class to handle the complexities of the I2C connected RTC chip
class KitronikRTC:
    CHIP_ADDRESS = 0x6F
    RTC_SECONDS_REG = 0x00
    RTC_MINUTES_REG = 0x01
    RTC_HOURS_REG = 0x02
    RTC_WEEKDAY_REG = 0x03
    RTC_DAY_REG = 0x04
    RTC_MONTH_REG = 0x05
    RTC_YEAR_REG = 0x06
    RTC_CONTROL_REG = 0x07
    RTC_OSCILLATOR_REG = 0x08
    RTC_PWR_UP_MINUTE_REG = 0x1C
    START_RTC = 0x80
    STOP_RTC = 0x00
    ENABLE_BATTERY_BACKUP = 0x08
    currentSeconds = 0
    currentMinutes = 0
    currentHours = 0
    # There is some initialisation to do on creation
    def __init__(self):
        i2c.init(freq=100000, sda=pin20, scl=pin19)
        writeBuf = bytearray(2)
        readBuf = bytearray(1)
        readCurrentSeconds = 0
        readWeekDayReg = 0
        writeBuf[0] = self.RTC_SECONDS_REG
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 1, False)
        readCurrentSeconds = readBuf[0]
        writeBuf[0] = self.RTC_CONTROL_REG
        writeBuf[1] = 0x43
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_WEEKDAY_REG
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 1, False)
        readWeekDayReg = readBuf[0]
        writeBuf[0] = self.RTC_WEEKDAY_REG
        writeBuf[1] = self.ENABLE_BATTERY_BACKUP | readWeekDayReg
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC | readCurrentSeconds
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)

    #reads the RTC chip. THE numbers come back as BCD, 
    #so this function converts them as they come in and places them into the class members
    def readValue(self):
        writeBuf = bytearray(1)
        readBuf = bytearray(7)
        self.readCurrentSeconds = 0
        writeBuf[0] = self.RTC_SECONDS_REG
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 7, False)
        self.currentSeconds = (((readBuf[0] & 0x70) >> 4) * 10) + (readBuf[0] & 0x0F)
        self.currentMinutes = (((readBuf[1] & 0x70) >> 4) * 10) + (readBuf[1] & 0x0F)
        self.currentHours = (((readBuf[2] & 0x30) >> 4) * 10) + (readBuf[2] & 0x0F)
        self.currentWeekDay = readBuf[3]
        self.currentDay = (((readBuf[4] & 0x30) >> 4) * 10) + (readBuf[4] & 0x0F)
        self.currentMonth =(((readBuf[5] & 0x10) >> 4) * 10) + (readBuf[5] & 0x0F) 
        self.currentYear = (((readBuf[6] & 0xF0) >> 4) * 10) + (readBuf[6] & 0x0F)

    #This actually pokes the time values into the RTC chip.
    #It converts the decimal values to BCD for the RTC chip
    def setTime(self, setHours, setMinutes, setSeconds):
        writeBuf = bytearray(2)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.STOP_RTC
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_HOURS_REG
        writeBuf[1] = (int(setHours / 10) << 4) | int(setHours % 10)
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_MINUTES_REG
        writeBuf[1] =  (int(setMinutes / 10) << 4) | int(setMinutes % 10)
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC |  (int(setSeconds / 10) << 4) | int(setSeconds % 10) 
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
    
    # These read functions only return the last read values.
    # use readValue() to update the stored numbers 
    def readSec(self):
       return self.currentSeconds

    def readMin(self):
        return self.currentMinutes

    def readHrs(self):
        return self.currentHours
#end of class KitronikRTC

#Because of space constraints due to micro python a common interface for the setting of a time
def timeSetInterface():
    setHrs = 0
    setMns = 0
    AM = True
    DisplayAMPM = False
    #'Zero' the clock display so we can set it
    zip_halo_display.clear()
    zip_halo_display[5*setHrs] = (255,0,0)
    zip_halo_display.show()
    #because the ui is limited we will have to set the hours and mins seperately.
    #Pressing A increments the value, B enters it and moves on 
    # set the time in Hours, Minutes, and then AM/PM
    display.scroll("A to Adjust, B to Enter")
    while (not (button_b.was_pressed())):
        display.show("H")
        if button_a.was_pressed():
            setHrs += 1
            if(setHrs >11):
                setHrs =0
            zip_halo_display.clear()
            zip_halo_display[5*setHrs] = (255,0,0)
        zip_halo_display.show()
    while (not (button_b.was_pressed())):
        display.show("M")
        if button_a.was_pressed():
            setMns += 1
            if(setMns >59):
                setMns = 0
            zip_halo_display.clear()
            zip_halo_display[5*setHrs] = (255,0,0)
            zip_halo_display[setMns] = (0,255,0)
            zip_halo_display.show()
    display.scroll("AM")
    while (not (button_b.was_pressed())):
        if button_a.was_pressed():
            if(AM):
                AM = False
            else:
                AM = True
            DisplayAMPM = True
        if(DisplayAMPM):
            if(AM ==True):
                display.scroll("AM")
            else:
                display.scroll("PM")
            DisplayAMPM = False
            
    if(AM == False):
        setHrs += 12
    return (setHrs,setMns)

# a procedure to allow the user to set the time
def userSetTime():
    requestedTime = timeSetInterface()
    #done hours, done mins, poke the rtc with the new values.
    rtc.setTime(requestedTime[0], requestedTime[1], 0)

# a procedure to allow the user to set an alarm
def userSetAlarm():
    global alarmHour
    global alarmMinute
    global setAlarm
    requestedTime = timeSetInterface()
    alarmHour = requestedTime[0]
    alarmMinute = requestedTime[1]
    setAlarm = True
    #done - The main loop checks the time to see if we should alarm

#Program Starts Here
#The ZIP LEDS
zip_halo_display = NeoPixel(pin8, LEDS_ON_HALO)
#a class for the RTC chip on the Halo HD
rtc = KitronikRTC()
gc.collect #cleanup the memory so we can actually run
while True:
    #get the values from the RTC
    rtc.readValue()
    hours = rtc.readHrs()
    minutes = rtc.readMin()
    seconds = rtc.readSec()
    #we can only display 12 hours, so if the 24hr clock reports PM then convert
    if hours > 11:
        zipHours = hours - 12
    else:
        zipHours = hours
    #the hour 'slots' are every 5 LEDS
    zipHours *= 5

    zip_halo_display.clear()
    zip_halo_display[zipHours] = (255, 0, 0)
    zip_halo_display[minutes] = (0, 255, 0)
    zip_halo_display[seconds] = (0, 0, 255)
    zip_halo_display.show()
    

    #watch out for a user interaction
    if button_a.was_pressed():
        userSetTime()
    if button_b.was_pressed():
        userSetAlarm()
    if setAlarm == True:
        display.show("A") #indicate to the user there is an alarm set
        if alarmHour == hours:
            if alarmMinute == minutes:
                soundlevel = 0
                while soundlevel < (SOUND_LEVEL_BASE + 5):
                    soundlevel = pin0.read_analog()
                    play(BA_DING, pin14, True, False)
                setAlarm = False
                display.clear()
                stop(pin14) #the music
#end of program
