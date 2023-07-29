#import network
import socket

#wlan_sta = network.WLAN(network.STA_IF)
#if wlan_sta.isconnected():
#    print("wifi is connected")

# Create STREAM TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sockaddr = socket.getaddrinfo('192.168.0.101', 8000)[0][-1]
print("connecting to:", sockaddr)

s.connect(sockaddr)

def sendText(textToSend):
   s.send(textToSend.encode()) 
   '''
   data = ''
   data = s.recv(1024).decode()
   print ("received: " + data)
   '''

while True:
   enteredText = input('enter: ')
   sendText(enteredText)

   if(enteredText == "exit"):
        break

s.close ()
