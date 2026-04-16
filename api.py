from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import datetime
import re
import programa
from utils import parse_iso8601

app = FastAPI(title="Agente de Contexto orbital")

# ── Modelos de entrada/salida ────────────────────────────────────────────────

class ContactRequest(BaseModel):
    norad_ids: list[str]
    ubicacion: tuple[float, float]
    grados_horizonte: float
    deadline: str
    usar_llm: bool = True
    modelo_llm: str = "gemma2:9b"

    @field_validator("deadline")
    @classmethod
    def validar_deadline(cls, v):
        parse_iso8601(v)
        return v




# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """El sistema que te consume puede verificar que el agente está vivo."""
    return {"status": "ok"}


@app.post("/ventanas")
def calcular_ventanas(req: ContactRequest):
    try:
        deadline_dt  = parse_iso8601(req.deadline)
        deadline_str = deadline_dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    salida = programa.calculate_contact_window_with_explanation(
        req.norad_ids,
        req.ubicacion,
        req.grados_horizonte,
        deadline_str,
        usar_llm=req.usar_llm,
        model=req.modelo_llm,
    )

    resultados = salida["resultados"]
    if "error" in resultados:
        raise HTTPException(status_code=400, detail=resultados["error"])

    return salida

@app.get("/tle/{norad_id}")
def obtener_tle(norad_id: str):
    """Devuelve el TLE de un satélite por su NORAD ID."""
    tles = programa.get_tles([norad_id])
    if norad_id not in tles:
        raise HTTPException(status_code=404, detail=f"NORAD ID {norad_id} no encontrado.")
    return tles[norad_id]