from flask import Flask, render_template, jsonify, request
import random
import threading
import time
from postgres.Postgres_Class import PostgresClass, AutoClosePostgres

app = Flask(__name__)

#MIDLOERTIDIG "FAKE DATABASE"
state = {
    "servo_active": False,
    "stepper_active": False,
    "latest_db": 42.7,
    "latest_hz": 440
}

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

# --- HELPER FUNKTION TIL AUTO OFF ---
def auto_off(key):
    time.sleep(10)
    state[key] = False
    print(f"{key} deaktiveret automatisk")

# --- ROUTES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sensor")
def get_sensor_data():
    db = auto_postgres.use()
    value_2 = random.randint(20,40)
    value_1 =db.fetch_one_value(table_name="sensor1", column_name="db")
    state["latest_db_1"] = value_1
    state["latest_db_2"] = value_2
 
    return jsonify({
        "db_1": state["latest_db_1"],
        "db_2": state["latest_db_2"]
    })

if __name__ == "__main__":
    app.run(debug=True)
