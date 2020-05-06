# OUTDATED README. Update pending. Use with caution
# micropython-microbit-kitronik-halohd
Example micro python (for BBC micro:bit) code for the Kitronik :VIEW Halo HD ( www.kitronik.co.uk/5672 )

## MEMS Mic:

Example code for the microphone feature.  The microphone is stored within a class.  The sound level reads analog P0.
```blocks
mic = KitronikMic
soundlevel = mic.readMicrophoneLevel(mic)

class KitronikMic:
	def readMicrophoneLevel(self):
        	soundlevel = pin0.read_analog()
        	return soundlevel
```

## RTC:

The example code uses the Real Time Clock (RTC) feature.  The readTime def is stored within a class and need to read from the RTC chip (which is additional subroutines within the class)
```blocks
hours = rtc.readTime(rtc, "hours")

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
```

## Buzzer:

The Halo HD has a buzzer on the board linked to pin 14.  For use of this feature uses the standard music import.
```blocks
music.play(music.BA_DING, pin14, True, False)
```

## ZIP LED's

The Halo HD has 60 Zip LED's, these are compatible with the standard neopixel package.

```blocks
zip_halo_display = neopixel.NeoPixel(pin8, LEDS_ON_HALO)
```
