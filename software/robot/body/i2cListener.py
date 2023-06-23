### main.py
import utime
import time
from machine import mem32,Pin
#import led
from plasma import WS2812
from servo import servo2040
from i2cSlave import i2c_slave

### --- check pico power on --- ###
print("led on")
#led.led_power_on()
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)
led_bar.start()
led_bar.set_rgb(1, 60, 60, 60) # light grey on LED1
time.sleep(1)

print("start i2c slave")
### --- pico connect i2c as slave --- ###
s_i2c = i2c_slave(0,sda=20,scl=21,slaveAddress=0x41)

print("entering loop")
try:
    while True:
        led_bar.set_rgb(1, 0, 120, 0) # green on LED1
        
        data = s_i2c.get()
        print(data)

        data_int = int(data)
        for i in range(data_int):
            #led.led_on()
            led_bar.set_rgb(1, 120, 0, 0) # red on LED1
            time.sleep(0.5)
            #led.led_off()
            led_bar.set_rgb(1, 0, 0, 120) # blue on LED1
            time.sleep(0.5)

except KeyboardInterrupt:
    pass