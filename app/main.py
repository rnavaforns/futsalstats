from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.models import StatsTemporada, Jugador
import sqlalchemy
from typing import Optional
from matplotlib.figure import Figure
import io
import base64
import csv

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

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
    nuevo = StatsTemporada(rival=rival or "", casa=casa or False, jornada=jornada, dorsal=17)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return RedirectResponse(url=f"/partido/{nuevo.jornada}", status_code=303)

@app.get("/partido/{jornada}")
def view_partido(request: Request, jornada: int, db: Session = Depends(get_db)):
    partido = db.query(StatsTemporada).filter_by(jornada=jornada).first()

    ofensivas_keywords = ["gol_favor", "xut_fora", "xut_porta", "corner", "perdua_zona_1", "perdua_zona_2", "perdua_zona_3", "faltes_favor", "xut_favor_interceptat", "assistencia", "disputa_perduda", "disputa_guanyada", "doble_favor_marcat", "corner_marcat", "corner_no_marcat", "corner_no_finalitzat", "regat_favor"]
    defensivas_keywords = ["gol_contra", "xut_fora_contra", "xut_porta_contra", "corner_contra", "recuperacio_zona_1", "recuperacio_zona_2", "recuperacio_zona_3", "faltes_contra", "aturades", "passe_interceptat", "xut_contra_interceptat", "doble_enncaixat", "doble_aturat", "regat_contra"]

    columnas_ofensivas = []
    columnas_defensivas = []

    columnas = [c.name for c in sqlalchemy.inspect(StatsTemporada).c if c.name not in ["jornada", "rival", "casa"]]
    for col in columnas:
        if any(k in col.lower() for k in ofensivas_keywords):
           columnas_ofensivas.append(col)
        elif any(k in col.lower() for k in defensivas_keywords):
            columnas_defensivas.append(col)
        else:
            columnas_defensivas.append(col)

    dorsales = [row.dorsal for row in db.query(Jugador.dorsal).all()]
    return templates.TemplateResponse("partido.html", {
        "request": request,
        "jornada": jornada,
        "columnas_ofensivas": columnas_ofensivas,
        "columnas_defensivas": columnas_defensivas,
        "dorsales": dorsales,
        "rival": partido.rival,
        "casa": "Sí" if partido.casa else "No"
    })

@app.post("/partido/{jornada}/accion/{columna}/{dorsal}")
def sumar_accion(jornada: int, columna: str, dorsal: int, db: Session = Depends(get_db)):
    if( columna in ["gol_contra", "xut_porta_contra", "xut_fora_contra", "corner", "corner_contra", "falta_favor"] ):
        dorsal = 0

    # Find existing row
    partido = db.query(StatsTemporada).filter_by(jornada=jornada, dorsal=dorsal).first()

    # If exists, increment
    if partido and hasattr(partido, columna):
        valor = getattr(partido, columna) or 0
        setattr(partido, columna, valor + 1)
    
    elif hasattr(StatsTemporada, columna):
        nuevo = StatsTemporada(
            jornada=jornada,
            dorsal=dorsal,
            rival="",
            casa=False 
        )
        setattr(nuevo, columna, 1)
        db.add(nuevo)
        partido = nuevo

    db.commit()
    return {"ok": True}

@app.post("/stats_acumulat/{columna}/{dorsales}")
def sumar_stats_acumulat(columna: str, dorsales: str, db: Session = Depends(get_db)):
    # Convert dorsales string to a list
    dorsales_list = dorsales.split(",")

    # Create placeholders for SQLAlchemy text query
    placeholders = ",".join(f":d{i}" for i in range(len(dorsales_list)))
    params = {f"d{i}": d for i, d in enumerate(dorsales_list)}

    # Wrap query string in sqlalchemy.text()
    query = text(f"UPDATE stats_acumulat SET {columna} = {columna} + 1 WHERE dorsal IN ({placeholders})")

    try:
        db.execute(query, params)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

    return {"updated_dorsales": dorsales_list, "column": columna}

def format_column_name(col: str) -> str:
    # Reemplazar _ por espacio
    parts = col.replace("_", " ").split()
    formatted = []
    for p in parts:
        if p.isdigit():  # números tal cual
            formatted.append(p)
        else:  # texto → primeras 3 letras mayúsculas
            formatted.append(p[:3].upper())
    return " ".join(formatted)

@app.get("/statsjornada/{jornada}")
def statsjornada(request: Request, jornada: int, db: Session = Depends(get_db)):
    jugadors = db.query(StatsTemporada).filter_by(jornada=jornada).order_by(StatsTemporada.dorsal).all()

    columnas = [c.name for c in sqlalchemy.inspect(StatsTemporada).c
                if c.name not in ["jornada", "rival", "casa"]]

    jugadors_dict = []
    for j in jugadors:
        if j.dorsal == 0:
            continue  # saltar fila dorsal 0
        jugadors_dict.append({col: getattr(j, col) for col in columnas + ["dorsal"]})

    jugadors_info = jugadors[0]

    totals = {"dorsal": "Equip"}
    for col in columnas:
        if col == "dorsal":
            continue
        try:
            totals[col] = sum(j[col] for j in jugadors_dict if isinstance(j[col], (int, float)))
        except Exception:
            totals[col] = ""

    jugadors_dict.append(totals)

    columnas_formatted = [
        {"name": col, "label": format_column_name(col)} for col in columnas
    ]

    return templates.TemplateResponse("statsjornada.html", {
        "request": request,
        "jornada": jornada,
        "columnas": columnas_formatted,
        "rival": jugadors_info.rival,
        "casa": "Sí" if jugadors_info.casa else "No",
        "jugadors": jugadors_dict  # lista con todos los jugadores y stats
    })

@app.get("/statsjugador/{dorsal}")
def statsjugador(request: Request, dorsal: int, db: Session = Depends(get_db)):
    jornadas = db.query(StatsTemporada).filter_by(dorsal=dorsal).order_by(StatsTemporada.jornada).all()

    columnas = [c.name for c in sqlalchemy.inspect(StatsTemporada).c
                if c.name not in ["rival", "casa"]]

    jornadas_dict = []
    for j in jornadas:
        jornadas_dict.append({col: getattr(j, col) for col in columnas})

    # calcular promedios
    n = len(jornadas)
    promedios = {"jornada": "Media"}
    for col in columnas:
        if col == "jornada":
            continue
        try:
            total = sum(j[col] for j in jornadas_dict if isinstance(j[col], (int, float)))
            promedios[col] = round(total / n, 2) if n > 0 else 0
        except Exception:
            promedios[col] = ""

    jornadas_dict.append(promedios)

    # construir headers abreviados
    columnas_formatted = [
        {"name": col, "label": format_column_name(col)} for col in columnas
    ]

    return templates.TemplateResponse("statsjugador.html", {
        "request": request,
        "dorsal": dorsal,
        "columnas": columnas_formatted,
        "jornadas": jornadas_dict
    })


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

@app.get("/statsjornada_csv/{jornada}")
def statsjornada_csv(jornada: int, db: Session = Depends(get_db)):
    # Obtener los datos igual que antes
    jugadors = db.query(StatsTemporada).filter_by(jornada=jornada).order_by(StatsTemporada.dorsal).all()

    columnas = [c.name for c in sqlalchemy.inspect(StatsTemporada).c
                if c.name not in ["jornada", "rival", "casa"]]

    jugadors_dict = []
    for j in jugadors:
        jugadors_dict.append({col: getattr(j, col) for col in columnas + ["dorsal"]})

    # Calcular totales
    totals = {"dorsal": "Equip"}
    for col in columnas:
        if col == "dorsal":
            continue
        try:
            totals[col] = sum(j[col] for j in jugadors_dict if isinstance(j[col], (int, float)))
        except Exception:
            totals[col] = ""

    jugadors_dict.append(totals)

    # Generar CSV en memoria
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["dorsal"] + columnas)
    writer.writeheader()
    writer.writerows(jugadors_dict)

    # Crear respuesta
    response = Response(
        content=output.getvalue(),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = f"attachment; filename=stats_jornada_{jornada}.csv"

    return response

