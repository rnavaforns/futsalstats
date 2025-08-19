from sqlalchemy import Column, Integer, String, Boolean, CHAR, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Jugador(Base):
    __tablename__ = "jugador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dorsal = Column(Integer, unique=True, default=0)
    nom = Column(String, default="0")
    cama_dominant = Column(CHAR, default="0")


class StatsTemporada(Base):
    __tablename__ = "stats_temporada"

    dorsal = Column(Integer, ForeignKey("jugador.dorsal"), primary_key=True)
    jornada = Column(Integer, primary_key=True)
    gol_favor = Column(Integer, default=0)
    gol_contra = Column(Integer, default=0)
    xut_fora = Column(Integer, default=0)
    xut_porta = Column(Integer, default=0)
    xut_fora_contra = Column(Integer, default=0)
    xut_porta_contra = Column(Integer, default=0)
    corner = Column(Integer, default=0)
    corner_contra = Column(Integer, default=0)
    perdua_zona_1 = Column(Integer, default=0)
    perdua_zona_2 = Column(Integer, default=0)
    perdua_zona_3 = Column(Integer, default=0)
    recuperacio_zona_1 = Column(Integer, default=0)
    recuperacio_zona_2 = Column(Integer, default=0)
    recuperacio_zona_3 = Column(Integer, default=0)
    faltes_favor = Column(Integer, default=0)
    faltes_contra = Column(Integer, default=0)
    rival = Column(String, default="")
    casa = Column(Boolean, default=False)


class StatsAcumulat(Base):
    __tablename__ = "stats_acumulat"

    dorsal = Column(Integer, ForeignKey("jugador.dorsal"), primary_key=True)
    gol_favor = Column(Integer, default=0)
    gol_contra = Column(Integer, default=0)
    xut_fora = Column(Integer, default=0)
    xut_porta = Column(Integer, default=0)
    xut_fora_contra = Column(Integer, default=0)
    xut_porta_contra = Column(Integer, default=0)
    corner = Column(Integer, default=0)
    corner_contra = Column(Integer, default=0)
    perdua_zona_1 = Column(Integer, default=0)
    perdua_zona_2 = Column(Integer, default=0)
    perdua_zona_3 = Column(Integer, default=0)
    recuperacio_zona_1 = Column(Integer, default=0)
    recuperacio_zona_2 = Column(Integer, default=0)
    recuperacio_zona_3 = Column(Integer, default=0)
    faltes_favor = Column(Integer, default=0)
    faltes_contra = Column(Integer, default=0)
