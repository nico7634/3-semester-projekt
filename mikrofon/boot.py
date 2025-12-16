from network import WLAN, STA_IF
from time import sleep
from Konfiguration import secrets, wifi_conf


wifi = WLAN(STA_IF) # Opretter objekt i station mode(Alm. wifi klient)
wifi.active(True)
sleep(1)
wifi.ifconfig((wifi_conf.ip, wifi_conf.subnet, wifi_conf.gateway, wifi_conf.dns))

wifi.connect(secrets.SSID, secrets.PASSWORD)

max_wait = 10
while max_wait > 0:
    if wifi.isconnected():
        break
    print('Connecting to Wi-Fi...')
    sleep(1)
    max_wait -= 1

# Check if connected
if wifi.isconnected():
    print('Connected!')
    print('Network config:', wifi.ifconfig())
    
else:
    print('Failed to connect')
    
