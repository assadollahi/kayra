we have currently three binaries to flash the ESP32 Cam board
- plain Micropython, see [here](https://micropython.org/download/esp32spiram/) also for flashing instructions  
- Micropython including camera support for streaming to the host, see [github repo](https://github.com/shariltumin/esp32-cam-micropython-2022), WiFi TLS version
- Micropython including the ST7789 display driver, [here](https://github.com/russhughes/st7789_mpy/tree/master/firmware/GENERIC_SPIRAM-7789)

flashing a binary:
- generally, the flashing procedure is done using the esptool.py, you can get it via sudo pip install esptool
- then you connect GND and IOO to put the ESP32 Cam to flash mode
- erase the flash: esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
- and then flash with one of the binaries, e.g. esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20190125-v1.10.bin 
- disconnect GND and IOO, reset the board 
- enter Thonny and connect using Run/Select Interpreter -> MicroPyton(ESP32) and the right USB port
