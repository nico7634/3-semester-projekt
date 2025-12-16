import network
import time

w0 = network.WLAN(network.STA_IF)
w0.active(True)

print("Boot: WiFi klar")
time.sleep(0.2)