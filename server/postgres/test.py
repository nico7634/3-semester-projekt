from Postgres_Class import PostgresClass
import random
from time import sleep
import time

with PostgresClass(user="postgres",
                        pswd="1234",
                        host="127.0.0.1",
                        port="5432",
                        db="postgres"
                        ) as db:
            
            db.create_sensor_table("Sensor1")