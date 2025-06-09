from sqlalchemy.orm import Session
from app.models import StatsTemporada
from sqlalchemy import text

def incrementar_accion(db: Session, partido_id: str, campo: str):
    stmt = text(f"""
        UPDATE stats_temporada
        SET {campo} = {campo} + 1
        WHERE partido_id = :partido_id
        RETURNING *;
    """)
    return db.execute(stmt, {"partido_id": partido_id}).fetchone()
