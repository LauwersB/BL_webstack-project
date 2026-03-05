# lichte Python versie
FROM python:3.11-slim

# Stel de werkmap in de container in
WORKDIR /app

# Kopieer de requirements
COPY requirements.txt .

# Installeer de afhankelijkheden
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de API code
COPY . .

# Stel de poort in waar FastAPI op draait
EXPOSE 8000

# Start de applicatie met uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]