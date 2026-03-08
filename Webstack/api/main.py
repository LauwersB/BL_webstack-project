from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
import mysql.connector
import os
import socket
import time
from pydantic import BaseModel
from config import db_host, db_name, username, password, cors_origins

app = FastAPI()

# Splits de string uit de config naar een echte lijst
origins = cors_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/user")
def get_user():
    container_id = socket.gethostname()
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    try:
        conn = mysql.connector.connect(
            host=db_host, user=username, password=password, 
            database=db_name, connect_timeout=5
        )
        # Update metric met de werkelijke latency
        db_latency.set(time.time() - start_time)
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM users LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return {
            "name": result["name"] if result else "Geen gebruiker gevonden",
            "container_id": container_id
        }
    except Exception as e:
        db_latency.set(-1) # Foutwaarde voor monitoring
        return {"error": "Database onbereikbaar", "details": str(e), "container_id": container_id}


# Dit model definieert wat Postman moet sturen
class UserUpdate(BaseModel):
    name: str


@app.post("/user/update")
def update_user(user_data: UserUpdate):
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=username,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()

        # We updaten de naam van de eerste gebruiker (ID 1)
        sql = "UPDATE users SET name = %s WHERE id = 1"
        cursor.execute(sql, (user_data.name,))

        conn.commit()  # Belangrijk: commit de wijziging naar de DB!

        cursor.close()
        conn.close()

        return {"status": "success", "updated_to": user_data.name}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/health")
async def health_check():
    return {"status": "ok"}

db_latency = Gauge('db_connection_latency_seconds', 'Tijd in seconden voor DB connectie')
REQUEST_COUNT = Counter('api_requests_total', 'Totaal aantal verzoeken naar de API')

@app.get("/metrics")
def get_metrics():
    # Dit endpoint wordt door Prometheus opgeroepen
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)