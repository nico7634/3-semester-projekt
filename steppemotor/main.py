import uasyncio as asyncio
from machine import Pin
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

#MOTOR
IN1 = Pin(26, Pin.OUT)
IN2 = Pin(25, Pin.OUT)
IN3 = Pin(33, Pin.OUT)
IN4 = Pin(32, Pin.OUT)
pins = [IN1, IN2, IN3, IN4]

sequence = [
    [1,0,0,0],
    [0,1,0,0],
    [0,0,1,0],
    [0,0,0,1]
]

async def step_forward(steps, delay=0.002):
    for _ in range(steps):
        for s in sequence:
            for i in range(4):
                pins[i].value(s[i])
            await asyncio.sleep(delay)

async def step_backward(steps, delay=0.002):
    for _ in range(steps):
        for s in reversed(sequence):
            for i in range(4):
                pins[i].value(s[i])
            await asyncio.sleep(delay)

motor_position = "tilbage"
below_timer_start = None
last_print = 0

#ESP-NOW RECEIVER
async def espnow_receiver():
    global motor_position, below_timer_start, last_print
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
        if value > 70:
            below_timer_start = None
            if motor_position != "fremme":
                motor_position = "fremme"
                await step_forward(600)

        else:
            if below_timer_start is None:
                below_timer_start = time.time()
            elif time.time() - below_timer_start > 120:
                if motor_position != "tilbage":
                    motor_position = "tilbage"
                    await step_backward(600)

        await asyncio.sleep(0)

#MAIN
async def main():
    await espnow_receiver()

time.sleep(2)

asyncio.run(main())