from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import StatsTemporada
import sqlalchemy
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/select-partido")
def select_partido(
    request: Request,
    partido_id: Optional[int] = Form(None),
    rival: Optional[str] = Form(None),
    casa: Optional[bool] = Form(False),
    db: Session = Depends(get_db)
):
    if partido_id:
        partido = db.query(StatsTemporada).filter_by(id=partido_id).first()
        if partido:
            return RedirectResponse(url=f"/partido/{partido_id}", status_code=303)

    # Crear nuevo partido
    nuevo = StatsTemporada(rival=rival or "", casa=casa or False)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return RedirectResponse(url=f"/partido/{nuevo.id}", status_code=303)

@app.get("/partido/{partido_id}")
def view_partido(request: Request, partido_id: int, db: Session = Depends(get_db)):
    partido = db.query(StatsTemporada).filter_by(id=partido_id).first()
    columnas = [c.name for c in sqlalchemy.inspect(StatsTemporada).c if c.name not in ["id", "rival", "casa"]]
    return templates.TemplateResponse("partido.html", {
        "request": request,
        "partido_id": partido_id,
        "columnas": columnas,
        "rival": partido.rival,
        "casa": "Sí" if partido.casa else "No"
    })

@app.post("/partido/{partido_id}/accion/{columna}")
def sumar_accion(partido_id: int, columna: str, db: Session = Depends(get_db)):
    partido = db.query(StatsTemporada).filter_by(id=partido_id).first()
    if partido and hasattr(partido, columna):
        valor = getattr(partido, columna) or 0
        setattr(partido, columna, valor + 1)
        db.commit()
    return {"ok": True}
