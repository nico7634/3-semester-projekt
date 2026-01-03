import uasyncio as asyncio
from machine import Pin, PWM
from servo import Servo
import espnow
import network
import time
import json

#ESP-NOW
w0 = network.WLAN(network.STA_IF)
w0.active(True)

e = espnow.ESPNow()
e.active(True)

PEER_MAC = b'\xd4\x8a\xfc\x68\x94\x88'
e.add_peer(PEER_MAC)

motor=Servo(pin=22)



async def espnow_receiver():
    global last_print
    print("Venter på ESP-NOW data...")

    while True:
        msg = e.recv(0)

        # Ingen data
        if msg is None:
            await asyncio.sleep(0.05)
            continue

        host, data = msg

        # Tom pakke
        if data is None:
            await asyncio.sleep(0.01)
            continue

        # JSON decode
        try:
            payload = json.loads(data.decode())
            value = payload.get("current_dBSPL", None)

            if value is None:
                continue

        except Exception as err:
            print("JSON-fejl:", err)
            continue

        # Print max én gang pr. sekund
        if time.time() - last_print > 1:
            print("Modtaget dB:", value)
            last_print = time.time()

        #LOGIK
        if value > 35:
            grader = int((value/85)*180)
            motor.move(grader)
            time.sleep(0.3)
            


#MAIN
async def main():
    await espnow_receiver()

time.sleep(2)

asyncio.run(main())