# A simple clock for the Halo HD. 
# To Set the time 


from microbit import button_a
from microbit import button_b
from microbit import display
from microbit import i2c
from microbit import Image
from microbit import pin0
from microbit import pin8
from microbit import pin14
from microbit import pin19
from microbit import pin20
import time
import neopixel


# Declare constants
LEDS_ON_HALO = 60
#SOUND_LEVEL_BASE is the average voltage level of the microphone at 1.65V converted to bytes
SOUND_LEVEL_BASE = 530
# some images for a pandulum animation
PendulumLeft =   Image("00900:"
                       "09000:"
                       "99000:"
                       "99000:"
                       "00000")
PendulumRight =  Image("00900:"
                       "00090:"
                       "00099:"
                       "00099:"
                       "00000")
PendulumCentre = Image("00900:"
                       "00900:"
                       "00900:"
                       "099900:"
                       "00900")








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
        self.currentHours = (((readBuf[2] & 0x10) >> 4) * 10) + (readBuf[2] & 0x0F)
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

# a procedure to allow the user to set the time
def userSetTime():
    setHrs = 0
    setMns = 0
    AM = True
    DisplayAMPM = False
    #'Zero' the clock display so we can set it
    zip_halo_display.clear()
    zip_halo_display[5*setHrs] = (255,0,0)
    zip_halo_display.show()
    #because the ui is limited we will have to set the hours and mins seperately.
    #Pressing A increments the value, B enters it an moves on 
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
    #done hours, done mins, poke the rtc with the new values.
    rtc.setTime(rtc,setHrs, setMns, 0)


#Program Starts Here
#The ZIP LEDS
zip_halo_display = neopixel.NeoPixel(pin8, LEDS_ON_HALO)
#a class for the RTC chip on the Halo HD
rtc = KitronikRTC

while True:
    #get the values from the RTC
    rtc.readValue(rtc)
    hours = rtc.readHrs(rtc)
    minutes = rtc.readMin(rtc)
    seconds = rtc.readSec(rtc)
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
    #aminate a pendulum to fill the time, helps to stop the LEDS flickering
    display.show(PendulumLeft)
    time.sleep(0.250)
    display.show(PendulumCentre)
    time.sleep(0.250)
    display.show(PendulumRight)
    time.sleep(0.250)
    display.show(PendulumCentre)
    time.sleep(0.100)
    #watch out for a user interaction
    if button_a.was_pressed():
        userSetTime()
    