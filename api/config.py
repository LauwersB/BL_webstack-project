import os
from pathlib import Path
from dotenv import load_dotenv

# Vind de .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

# DB instellingen
# We halen de db_credentials uit de .env en slaan ze op als variabelen
db_host = os.getenv("WEBSTACK_DB_HOST", "host")
db_name = os.getenv("WEBSTACK_DB_NAME", "dbname")
username = os.getenv("WEBSTACK_DB_USER", "username")
password = os.getenv("WEBSTACK_DB_PASSWORD", "password")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8080")