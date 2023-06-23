from machine import UART
import os
os.dupterm(None, 1)

uart = UART(0, 115200)                         # init with given baudrate
#uart.init(9600, bits=8, parity=None, stop=1)

while True:
    if uart.any() > 0:
        inText = uart.read()
        if inText == "q":
            break
        else:
            print(b"received " + inText)
        
        
os.dupterm(uart, 1)        