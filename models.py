from pydantic import BaseModel
from typing import Optional

# lo que se manda al resto del pipelihne
class VentanaContacto(BaseModel):
    aos_utc: str
    los_utc: str
    duracion_seg: int
    elevacion_max_grados: float
    antes_del_deadline: bool

class ResultadoSatelite(BaseModel):
    norad_id: str
    nombre: str
    ventanas_los: list[VentanaContacto]
    ventanas_downlink: list[VentanaContacto] = []   # default vacío hasta implementar
    total_ventanas: int
    factible: bool
    justificacion: str

class ContextoOrbital(BaseModel):          # ← esto es lo que sale hacia PDDL
    deadline_utc: str
    ubicacion_lat: float
    ubicacion_lon: float
    grados_horizonte: float
    satelites: list[ResultadoSatelite]
    mision_factible: bool                  # true si AL MENOS UN satélite es factible
    explicacion_llm: Optional[str]