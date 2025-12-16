import psycopg2
import re
import time
import threading

class PostgresClass:
    """
    Initialiser informationer om den PostgreSQL man vil forbinde til.
    """
    def __init__(self, user:str, pswd:str, host:str, port:str, db:str):
        """
        Args:
            user, pswd, host, port, db: Information for at forbinde til databasen
        """
        self.user = user
        self.pswd = pswd
        self.host = host
        self.port = port
        self.db = db

    def __enter__(self:str):
        """
        Med __enter__, kan man anvende en context manager (With) så åbnes forbindelsen automatisk
        ARGS:
            Hvad klasse objektet skal hedde. 
            F.eks. With PostgresClass(user, pswd, host, port, db) as db. Så kan du lave metode kald indrykket under with. 
        """
        self.conn = psycopg2.connect(
            user = self.user,
            password = self.pswd,
            host = self.host,
            port = self.port,
            database = self.db
        )
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, type, val, tb):
        """
        __exit__ køre automaitks når With blokken er færdig, og derved lukker forbindelsen
        ARGS:
            Python sender altid automatisk 3 argumenter til metoden. Hvis der ikke opstår nogen fejl, sender den tre gange None.
            Hvis der opstår en fjel, sender den typen, fejlbeskeden og traceback.
        """
        self.cursor.close()
        self.conn.close()

    def create_sensor_table(self, table_name:str):  
        """
        Anvendes til at oprette et nyt tabel til sensorer. Metoden tjekker først, om det indtastede tabelnavn opfylder de fastsatte krav,
        og opretter derefter tabellen.
        ARGS:
            Navnet på tabellen du vil oprette.
        """
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]{0,9}$', table_name):
            raise ValueError("Navnet er ugyldigt. Læs dokumentation.")
        query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id serial NOT NULL PRIMARY KEY,
                timestamp timestamp NOT NULL,
                dB smallint NOT NULL
            );"""

        self.cursor.execute(query)
        self.conn.commit()

    def fetch_one_row(self, table_name, column_name):
        """
        Henter den første værdi fra en kolonne i en tabel.
        ARGS:
            table_name : str : Navnet på tabellen
            column_name : str : Kolonnen du vil hente værdien fra
        """
        query = f"SELECT {column_name} FROM {table_name} LIMIT 1;"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] if result else None

    def fetch_one_value(self, table_name, column_name):
        """
        Henter den nyeste værdi fra en kolonne baseret på id. Og sortede dem i så man tag den nyeste.
        ARGS:
            table_name : str : Navnet på tabellen
            column_name : str : Kolonnen du vil hente værdien fra        
        """
        query = f"""
            SELECT {column_name}
            FROM {table_name}
            ORDER BY id DESC
            LIMIT 1
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def add_value(self, table_name, db_value):
        """
        Indæstter data fra sensor i table
        ARGS:
            Navnet på table og dataen fra sensoren.
        """
        query = f"""INSERT INTO {table_name} (timestamp, db)
                    VALUES (NOW(), {db_value}); 
                """
        self.cursor.execute(query)
        self.conn.commit()

class AutoClosePostgres:
    """
    Klasse som automatisk lukker for databse forbindelsen hvis den ikke modtager data.
    ARGS:
        Den database forbindelse, som klassen skal håndtere og tidsloftet for hvornår den skal lukke.
    """
    def __init__(self, db_conn:str, timeout_seconds:int):
        self.db = db_conn
        self.timeout = timeout_seconds
        self.last_use = 0 
        self.lock = threading.Lock()
        self.active = False
        threading.Thread(target=self._watchdog, daemon=True).start()

    def _watchdog(self):
        """
        Metoden tjekker om forbindelsen skal lukkes ud fra den givende tidsloft.
        """
        while True:
            time.sleep(10)
            with self.lock:
                if self.active and (time.time() - self.last_use) > self.timeout:
                    self.db.__exit__(None, None, None)
                    self.active = False
    
    def use(self):
        """
        Hvis forbindelsen ikke er åben, åbner den og returnerer db forbindelsen.
        """
        with self.lock:
            if not self.active:
                self.db.__enter__()
                self.active = True
            self.last_use = time.time()
        return self.db