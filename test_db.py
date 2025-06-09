from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Cargar las variables del .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Crear engine
engine = create_engine(DATABASE_URL)

# Test: conexión y lectura de la tabla
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM stats_temporada LIMIT 5"))
        for row in result:
            print(row)
    print("✅ Conexión exitosa y datos leídos")
except Exception as e:
    print("❌ Error de conexión:", e)
