import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///data.db"
)

SECRET_KEY = "noget_meget_hemmeligt"

"""import os

DB_URI = os.getenv(
    "DATABASE_URL",
    "postgresql://brugernavn:password@localhost/stoejdb" 
)
# Husk at ændre brugernavn, password og database navn efter behov"""