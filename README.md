# micropython-microbit-kitronik-halohd
Example micro python (for BBC micro:bit) code for the Kitronik :VIEW Halo HD ( www.kitronik.co.uk/5672 )
This code implements a simple clock, with an alarm using the buzzer which is cancelled by clapping detected by the microphone.

## MEMS Mic:
Example code for the microphone. The microphone is an analog input connected to P0.
```blocks

soundlevel =  pin0.read_analog()

```

## RTC:
The example code uses the onboard Real Time Clock (RTC) IC.  
This sits in the I2C bus, and is accessed through a class.
Due to space constraints the class is not as readable as the makecode equivalent, but functionally is similar.
The class stores the last time the RTC was read internally. To update this time  before using it call readValue()
```blocks

rtc = KitronikRTC
rtc.readValue(rtc)

```
To access the time elements call the appropriate fucntion:
```blocks

rtc = KitronikRTC
hours = rtc.readHrs(rtc)
minutes = rtc.readMin(rtc)
seconds = rtc.readSec(rtc)

```
To set the RTC time (to 1:15pm in this instance)
```blocks

rtc = KitronikRTC
rtc.setTime(rtc,13, 15, 0)

```

## Buzzer:
The Halo HD has a buzzer on the board linked to pin 14.  The standard music feature can be used to drive it
```blocks

import music
music.play(music.BA_DING, pin14, True, False)

```

## ZIP LEDs
The Halo HD has 60 Zip LED's, these are compatible with the standard neopixel package.
```blocks

import neopixel
zip_halo_display = neopixel.NeoPixel(pin8, LEDS_ON_HALO)
zip_halo_display[1]=(255,0,0)
zip_halo_display.show()

```
