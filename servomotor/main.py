import uasyncio as asyncio
from machine import Pin, PWM
from servo import Servo
import espnow
import network
import time
import json


e = espnow.ESPNow()
e.active(True)

PEER_MAC = b'\xd4\x8a\xfc\x68\x94\x88'
e.add_peer(PEER_MAC)

motor=Servo(pin=22)

last_print = 0

async def espnow_receiver():
    global last_print
    print("Venter på ESP-NOW data...")

    while True:
        msg = e.recv(0)


        # Ingen data
        if msg is None:
            await asyncio.sleep_ms(5)
            continue

        host, data = msg

        # Tom pakke
        if data is None:           
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



        #LOGIK
        if value > 40:
            grader = int(((value-40)/50)*180)
            print("Modtaget dB:", value, "sætter til:", grader, "grader")
            motor.move(grader)
            await asyncio.sleep(0.3)
            
        if value < 40:
            print("Modtaget dB:", value, "sætter til: 0 grader")
            motor.move(0)
            await asyncio.sleep(0.3)
            

#MAIN
async def main():
    asyncio.create_task(espnow_receiver())
    while True:
        await asyncio.sleep_ms(5)

asyncio.run(main())
