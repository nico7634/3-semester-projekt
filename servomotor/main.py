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