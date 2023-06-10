#from machine import UART, Pin
#import machine
from plasma import WS2812
from servo import ServoCluster, servo2040
import time

#uart1 = machine.UART(0, 115200)
#uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)
led_bar.start()


while True:
    time.sleep(1)
    led_bar.set_rgb(1, 120, 120, 0) # orange on LED1
    #uart1.write('hello')  # write 5 bytes
    print("hello\n")
    time.sleep(1)
    led_bar.set_rgb(1, 0, 0, 0) # orange on LED1    
    
#uart1.read(5)         # read up to 5 bytes