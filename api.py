from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import programa
from utils import parse_iso8601
from models import ContextoOrbital

app = FastAPI(title="Agente de Contexto Orbital")


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
        if parse_iso8601(v) is None:
            raise ValueError(f"Formato de fecha inválido: '{v}'. Use ISO 8601.")
        return v


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tle/{norad_id}")
def obtener_tle(norad_id: str):
    tles = programa.get_tles([norad_id])
    if norad_id not in tles:
        raise HTTPException(status_code=404, detail=f"NORAD ID {norad_id} no encontrado.")
    return tles[norad_id]


@app.post("/contacto", response_model=ContextoOrbital)
async def calcular_contacto(req: ContactRequest):
    resultado = programa.calculate_contact_window_with_explanation(
        norad_ids=req.norad_ids,
        ubicacion=req.ubicacion,
        grados_horizonte=req.grados_horizonte,
        deadline=req.deadline,
        usar_llm=req.usar_llm,
        model=req.modelo_llm,
    )
    return resultado