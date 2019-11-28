from microbit import button_a
from microbit import display
from microbit import i2c
from microbit import pin0
from microbit import pin8
from microbit import pin14
from microbit import pin19
from microbit import pin20
import music
import neopixel

# Declare constants
LEDS_ON_HALO = 60
#SOUND_LEVEL_BASE is the average voltage level of the microphone at 1.65V converted to bytes
SOUND_LEVEL_BASE = 530
init = False

class KitronikRTC:
    initalised = False
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
    decSeconds = 0
    decMinutes = 0
    decHours = 0

    def init(self):
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
        self.initalised = True

    def decToBcd(self, decNumber):
        tens = 0
        units = 0
        bcdNumber = 0
        tens = int(decNumber / 10)
        units = int(decNumber % 10)
        bcdNumber = (tens << 4) | units
        return bcdNumber

    def bcdToDec(self, bcdNumber, readReg):
        mask = 0
        shiftedTens = 0
        units = 0
        tens = 0
        decNumber = 0
        if readReg == self.RTC_SECONDS_REG:
            mask = 0x70
        elif readReg is self.RTC_MINUTES_REG:
            mask = 0x70
        elif readReg is self.RTC_DAY_REG:
            mask = 0x30
        elif readReg is self.RTC_HOURS_REG:
            mask = 0x10
        elif readReg is self.RTC_MONTH_REG:
            mask = 0x10
        elif readReg is self.RTC_YEAR_REG:
            mask = 0xF0
        units = bcdNumber & 0x0F
        tens = bcdNumber & mask
        shiftedTens = tens >> 4
        decNumber = (shiftedTens * 10) + units
        return decNumber

    def readValue(self):
        if self.initalised is False:
            self.init(self)
        writeBuf = bytearray(1)
        readBuf = bytearray(7)
        self.readCurrentSeconds = 0
        writeBuf[0] = self.RTC_SECONDS_REG
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        readBuf = i2c.read(self.CHIP_ADDRESS, 7, False)
        self.currentSeconds = readBuf[0]
        self.currentMinutes = readBuf[1]
        self.currentHours = readBuf[2]
        self.currentWeekDay = readBuf[3]
        self.currentDay = readBuf[4]
        self.currentMonth = readBuf[5]
        self.currentYear = readBuf[6]

    def setTime(self, setHours, setMinutes, setSeconds):
        if self.initalised is False:
            self.init(self)	
        bcdHours = self.decToBcd(self, setHours)
        bcdMinutes = self.decToBcd(self, setMinutes)
        bcdSeconds = self.decToBcd(self, setSeconds)
        writeBuf = bytearray(2)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.STOP_RTC
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_HOURS_REG
        writeBuf[1] = bcdHours	
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_MINUTES_REG
        writeBuf[1] = bcdMinutes
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC | bcdSeconds
        i2c.write(self.CHIP_ADDRESS, writeBuf, False)

    def readTime(self, parameter):
        if self.initalised is False:
            self.init(self)
        self.readValue(self)
        if parameter == "seconds":
            decSeconds = self.bcdToDec(self, self.currentSeconds, self.RTC_SECONDS_REG)
            return decSeconds
        elif parameter == "minutes":
            decMinutes = self.bcdToDec(self, self.currentMinutes, self.RTC_MINUTES_REG)
            return decMinutes
        elif parameter == "hours":
            decHours = self.bcdToDec(self, self.currentHours, self.RTC_HOURS_REG)
            return decHours

class KitronikMic:
    def readMicrophoneLevel(self):
        soundlevel = pin0.read_analog()
        return soundlevel

    def readAverageMicrophoneLevel(self):
        i = 0
        for i in range (0, 4):
            soundlevel = pin0.read_analog()
            averageSoundLevel = int((averageSoundLevel + soundlevel)/2)
            sleep(200)
        return averageSoundLevel

zip_halo_display = neopixel.NeoPixel(pin8, LEDS_ON_HALO)

while True:
    if init is False:
        mic = KitronikMic
        rtc = KitronikRTC
        rtc.setTime(rtc, 11, 25, 50)
        alarmHour = 11
        alarmMinute = 26
        zipHours = 0
        setAlarm = False
        init = True

    hours = rtc.readTime(rtc, "hours")
    minutes = rtc.readTime(rtc, "minutes")
    seconds = rtc.readTime(rtc, "seconds")
    if hours > 13:
        zipHours = hours - 12
    zipHours = zipHours * 5

    zip_halo_display.clear()
    zip_halo_display[zipHours] = (255, 0, 0)
    zip_halo_display[minutes] = (0, 255, 0)
    zip_halo_display[seconds] = (0, 0, 255)
    zip_halo_display.show()

    if button_a.is_pressed():
        setAlarm = True
        display.scroll("Alarm Set")

    if alarmHour == hours:
        if alarmMinute == minutes:
            if setAlarm == True:
                soundlevel = 0
                while soundlevel < (SOUND_LEVEL_BASE + 5):
                    soundlevel = mic.readMicrophoneLevel(mic)
                    music.play(music.BA_DING, pin14, True, False)
                setAlarm = False
            else:
                music.stop(pin14)