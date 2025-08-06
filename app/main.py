from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import StatsTemporada
import sqlalchemy
from typing import Optional
from matplotlib.figure import Figure
import io
import base64

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
    jornada: Optional[int] = Form(None),
    rival: Optional[str] = Form(None),
    casa: Optional[bool] = Form(False),
    db: Session = Depends(get_db)
):
    if jornada:
        partido = db.query(StatsTemporada).filter_by(jornada=jornada).first()
        if partido:
            return RedirectResponse(url=f"/partido/{jornada}", status_code=303)

    # Crear nuevo partido
    nuevo = StatsTemporada(rival=rival or "", casa=casa or False, jornada=jornada, dorsal=0)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return RedirectResponse(url=f"/partido/{nuevo.jornada}", status_code=303)

@app.get("/partido/{jornada}")
def view_partido(request: Request, jornada: int, db: Session = Depends(get_db)):
    partido = db.query(StatsTemporada).filter_by(jornada=jornada).first()
    columnas = [c.name for c in sqlalchemy.inspect(StatsTemporada).c if c.name not in ["jornada", "rival", "casa"]]
    return templates.TemplateResponse("partido.html", {
        "request": request,
        "jornada": jornada,
        "columnas": columnas,
        "rival": partido.rival,
        "casa": "Sí" if partido.casa else "No"
    })

@app.post("/partido/{jornada}/accion/{columna}")
def sumar_accion(jornada: int, columna: str, db: Session = Depends(get_db)):
    partido = db.query(StatsTemporada).filter_by(jornada=jornada).first()
    if partido and hasattr(partido, columna):
        valor = getattr(partido, columna) or 0
        setattr(partido, columna, valor + 1)
        db.commit()
    return {"ok": True}

@app.get("/gols")
def goles_temporada(request: Request, db: Session = Depends(get_db)):
    partidos = db.query(StatsTemporada).order_by(StatsTemporada.id).all()
    jornadas = list(range(1, len(partidos) + 1))
    goles = [p.gol_favor for p in partidos]

    # Crear figura
    fig = Figure(figsize=(10, 4))
    ax = fig.subplots()
    ax.plot(jornadas, goles, marker='o', color='green')
    ax.set_title("Evolución de Goles a Favor")
    ax.set_xlabel("Jornada")
    ax.set_ylabel("Goles")
    ax.grid(True)

    # Guardar imagen en base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return templates.TemplateResponse("gols.html", {
        "request": request,
        "image_base64": image_base64
    })

    #hola
