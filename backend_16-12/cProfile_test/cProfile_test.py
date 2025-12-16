# ws_server.py
import asyncio
import websockets
from postgres.Postgres_Class import PostgresClass, AutoClosePostgres
import json
import cProfile
import pstats
import time

"""
asyncio er en måde at køre kode på ved siden af, det vil sige at det f.eks. venter
her til der kommer en besked eller websocket(klient) og så kører
den efterfølgende kode.
"""

# -------------------------
# Postgres init
# -------------------------
postgres_params = {
    "user": "postgres",
    "pswd": "1234",
    "host": "127.0.0.1",
    "port": "5432",
    "db": "postgres"
}

postgres = PostgresClass(**postgres_params)
auto_postgres = AutoClosePostgres(postgres, timeout_seconds=30)

# -------------------------
# Profiler (global)
# -------------------------
profiler = cProfile.Profile()

# -------------------------
# WebSocket handler
# -------------------------
async def handler(websocket):
    print("Client connected")

    try:
        async for json_message in websocket:

            profiler.enable()  # START profilering

            t0 = time.perf_counter()

            # Parse JSON
            message = json.loads(json_message)
            if not isinstance(message, dict):
                profiler.disable()
                continue

            db_value = message["current_dBSPL"]
            print("Sensor data received:", db_value)

            # Database write
            db = auto_postgres.use()
            db.add_value(table_name="sensor1", db_value=db_value)

            t1 = time.perf_counter()

            profiler.disable()  # STOP profilering

            print(f"Behandlingstid pr. besked: {(t1 - t0)*1000:.2f} ms")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

# -------------------------
# Main
# -------------------------
async def main():
    async with websockets.serve(handler, "192.168.10.3", 8765):
        print("WebSocket server running on ip 192.168.10.3 port 8765")
        await asyncio.Future()  # kører uendeligt

# -------------------------
# Run + dump profil
# -------------------------
try:
    asyncio.run(main())
finally:
    profiler.dump_stats("ws_server.prof")
    stats = pstats.Stats("ws_server.prof")
    stats.sort_stats("cumtime").print_stats(20)

