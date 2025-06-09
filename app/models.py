from sqlalchemy import Column, Integer, String, Date, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

Base = declarative_base()

class StatsTemporada(Base):
    __tablename__ = "stats_temporada"

    id = Column(Integer, primary_key=True, index=True)
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