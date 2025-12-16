# ws_server.py
import asyncio
import websockets

MAX_ITEMS = 9
items = []

# Hold styr på forbindelser
sensor_ws_list = []   # Liste med sensor-forbindelser
actuator_ws = None    # Aktuator-forbindelse

async def handler(websocket):
    global items, actuator_ws, sensor_ws_list

    client_ip = websocket.remote_address[0]
    print(f"Client connected: {client_ip}")

    # Tjek om det er aktuatoren (IP 192.168.10.3)
    if client_ip == "192.168.10.3":
        actuator_ws = websocket
        print("Aktuator connected")
    else:
        sensor_ws_list.append(websocket)
        print("Sensor connected")

    try:
        async for message in websocket:
            # Hvis det er en sensor, modtag data
            if client_ip != "192.168.10.3":
                print("Sensor data received:", message)
                items.append(float(message))
                if len(items) >= MAX_ITEMS:
                    avg = sum(items) / len(items)
                    print("Average:", avg)
                    # Send til aktuatoren hvis den er connected
                    if actuator_ws:
                        try:
                            await actuator_ws.send(str(avg))
                            print("Sent to actuator:", avg)
                        except:
                            print("Fejl: ak
