import time
from machine import Pin
from pimoroni import Analog, AnalogMux, Button
from servo import Servo, servo2040
from plasma import WS2812


# led bar
SPEED = 5           # The speed that the LEDs will cycle at
BRIGHTNESS = 0.2    # The brightness of the LEDs
UPDATES = 50        # How many times the LEDs will be updated per second

# Create the LED bar, using PIO 1 and State Machine 0
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)
# Start updating the LED bar
led_bar.start()

# Create a list of servos for pins 0 to 3. Up to 16 servos can be created
START_PIN = servo2040.SERVO_1
END_PIN = servo2040.SERVO_4
servos = [Servo(i) for i in range(START_PIN, END_PIN + 1)]

# Enable all servos (this puts them at the middle)
for s in servos:
    s.enable()
time.sleep(2)


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

servoNumber = 0
servoValues = [0.0] * 4


mux.select(sensor_addrs[1])
floor2 = round(sen_adc.read_voltage(), 3)

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
    
    servoValues[servoNumber] += floor2 - off2
    
    servos[servoNumber].value(servoValues[servoNumber])
    #print("servo " + str(servoNumber) + " changed to " + str(servoValues[servoNumber]))
    
    if (off3 < 0.5):
        servoNumber += 1
        
        if (servoNumber > 3):
            servoNumber = 0
       
    time.sleep(0.3)

# Turn off the LED bar
led_bar.clear()