import uasyncio as asyncio
import espnow
import network
import json
from machine import Pin
from Konfiguration.websokcet import AsyncWebsocketClient
from Konfiguration.INMP441_dB_JSON import dbspl_json 





e = espnow.ESPNow()
e.active(True)

peer_step = b'\xc8.\x18\x16\xac\xc0'
peer_servo = b'\xd4\x8a\xfch\xa0\xac'
e.add_peer(peer_step)
e.add_peer(peer_servo)


async def send_via_espnow():
    while True:
        json_payload = await dbspl_json()
        if json_payload:
            try:
                e.send(peer_step, json_payload.encode())
                e.send(peer_servo, json_payload.encode())
                print("Sent ESP-NOW:", json_payload)
            except Exception as ex:
                print("ESP-NOW send failed:", ex)

        await asyncio.sleep(0.5)


async def send_via_websocket():
    ws_server = None

    while True:
        # reconnect hvis serveren ikke er forbundet
        if ws_server is None:
            try:
                ws_server = AsyncWebsocketClient()
                await ws_server.handshake("ws://192.168.10.3:8765")
                print("WebSocket connected")
            except:
                ws_server = None
                await asyncio.sleep(2)
                continue

        json_payload = await dbspl_json()
        if json_payload:
            try:
                await ws_server.send(json_payload)
                print("Sent WebSocket:", json_payload)
            except:
                print("WebSocket send failed")
                ws_server = None
        await asyncio.sleep(0.5)


async def main():
    asyncio.create_task(send_via_websocket()) #prøv at kald espnow først
    asyncio.create_task(send_via_espnow())



    while True:
        await asyncio.sleep(0.5)


asyncio.run(main())


