# ws_server.py
import asyncio
import websockets
from postgres.Postgres_Class import PostgresClass, AutoClosePostgres
import pytest
import json

"""
asyncio er en måde at køre kode på ved siden af, det vil sige at det f.eks. venter her til der kommer en besked eller websocket(klient) og så kører
den det efterfølgende kode.
"""
# Postgress Innit med automatisk nedlukning
postgres_params = {
                    "user":"postgres",
                    "pswd":"1234",
                    "host":"127.0.0.1",
                    "port":"5432",
                    "db":"postgres"
}
postgres = PostgresClass(**postgres_params)
auto_postgres = AutoClosePostgres(postgres, timeout_seconds=30)

async def handler(websocket):
    print("Client connected")
    try:
        async for json_message in websocket:
            message = json.loads(json_message)
            if not isinstance(message, dict):
                continue
            db_value = message["current_dBSPL"]
            print("Sensor data received:", db_value)
            db =auto_postgres.use()
            db.add_value(table_name="sensor1", db_value=db_value)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    # Start WebSocket server for sensorer
    async with websockets.serve(handler, "192.168.10.3", 8765):
        print("WebSocket server running on ip 192.168.10.3 port 8765")
        await asyncio.Future()

asyncio.run(main())