import network
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect("YourSSID","YourWiFiPassword")
print("is connected: " + str(station.isconnected()))
print("IP details: " + str(station.ifconfig()))
