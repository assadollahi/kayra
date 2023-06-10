# bno055_test.py Simple test program for MicroPython bno055 driver

# Copyright (c) Peter Hinch 2019
# Released under the MIT licence.

import machine
import time
from bno055 import *

from plasma import WS2812
from servo import ServoCluster, servo2040

led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)
led_bar.start()

sda=machine.Pin(20) # Explorer 20 Breakout 4
scl=machine.Pin(21) # Explorer 21 Breakout 5
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)

imu = BNO055(i2c)
calibrated = False
while True:
    time.sleep(0.1)
    led_bar.set_rgb(1, 120, 120, 0) # orange on LED1
    '''
    if not calibrated:
        calibrated = imu.calibrated()
        print('Calibration required: sys {} gyro {} accel {} mag {}'.format(*imu.cal_status()))
    print('Temperature {}°C'.format(imu.temperature()))
    print('Mag       x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.mag()))
    print('Gyro      x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.gyro()))
    print('Accel     x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.accel()))
    print('Lin acc.  x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.lin_acc()))
    print('Gravity   x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.gravity()))
    '''
    print('Heading     {:4.0f} roll {:4.0f} pitch {:4.0f}'.format(*imu.euler()))
    led_bar.set_rgb(1, 0, 0, 0) # orange on LED1
    time.sleep(0.1)