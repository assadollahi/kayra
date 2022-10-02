import time
from machine import Pin
from pimoroni import Analog, AnalogMux, Button
from servo import servo2040
from plasma import WS2812


# led bar
SPEED = 5           # The speed that the LEDs will cycle at
BRIGHTNESS = 0.2    # The brightness of the LEDs
UPDATES = 50        # How many times the LEDs will be updated per second

# Create the LED bar, using PIO 1 and State Machine 0
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)
# Start updating the LED bar
led_bar.start()

"""
Shows how to initialise and read the 6 external
and 2 internal sensors of Servo 2040.

Press "Boot" to exit the program.
"""

# Set up the shared analog inputs
sen_adc = Analog(servo2040.SHARED_ADC)
vol_adc = Analog(servo2040.SHARED_ADC, servo2040.VOLTAGE_GAIN)
cur_adc = Analog(servo2040.SHARED_ADC, servo2040.CURRENT_GAIN,
                 servo2040.SHUNT_RESISTOR, servo2040.CURRENT_OFFSET)

# Set up the analog multiplexer, including the pin for controlling pull-up/pull-down
mux = AnalogMux(servo2040.ADC_ADDR_0, servo2040.ADC_ADDR_1, servo2040.ADC_ADDR_2,
                muxed_pin=Pin(servo2040.SHARED_ADC))

# Set up the sensor addresses and have them pulled down by default
sensor_addrs = list(range(servo2040.SENSOR_1_ADDR, servo2040.SENSOR_6_ADDR + 1))
#for addr in sensor_addrs:
mux.configure_pull(sensor_addrs[0], Pin.PULL_DOWN)

mux.configure_pull(sensor_addrs[1], Pin.PULL_DOWN)

mux.configure_pull(sensor_addrs[2], Pin.PULL_UP)


# Create the user button
user_sw = Button(servo2040.USER_SW)


# Read sensors until the user button is pressed
while not user_sw.raw():

    # Read each sensor in turn and print its voltage
    #for i in range(len(sensor_addrs)):
    mux.select(sensor_addrs[0])
    off1 = round(sen_adc.read_voltage(), 3)
    
    mux.select(sensor_addrs[1])
    off2 = round(sen_adc.read_voltage(), 3)
    
    mux.select(sensor_addrs[2])
    off3 = round(sen_adc.read_voltage(), 3)
    
    #print("S", i + 1, " = ", round(sen_adc.read_voltage(), 3), sep="", end=", ")
        
    #for i in range(servo2040.NUM_LEDS):
        #hue = float(i) / servo2040.NUM_LEDS
    led_bar.set_hsv(0, off1/2.0, 1.0, BRIGHTNESS)
    
    led_bar.set_hsv(1, off2/2.0, 1.0, BRIGHTNESS)
    
    led_bar.set_hsv(2, off3/2.0, 1.0, BRIGHTNESS)
    
    #print(off3)
        
    '''
    # Read the voltage sense and print the value
    mux.select(servo2040.VOLTAGE_SENSE_ADDR)
    #print("Voltage =", round(vol_adc.read_voltage(), 4), end=", ")

    # Read the current sense and print the value
    mux.select(servo2040.CURRENT_SENSE_ADDR)
    #print("Current =", round(cur_adc.read_current(), 4))
    '''
    
    time.sleep(0.5)
