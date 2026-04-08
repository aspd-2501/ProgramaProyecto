from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import datetime
import re
import programa

app = FastAPI(title="Agente de Ventanas de Contacto")

# ── Modelos de entrada/salida ────────────────────────────────────────────────

class ContactRequest(BaseModel):
    norad_ids: list[str]
    ubicacion: tuple[float, float]        # (latitud, longitud)
    grados_horizonte: float
    deadline: str                          # ISO 8601

    @field_validator("deadline")
    @classmethod
    def validar_deadline(cls, v):
        parse_iso8601(v)                   # lanza ValueError si es inválido
        return v

# ── Reutilizas tu parser ISO 8601 ───────────────────────────────────────────

ISO_FULL = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})"
    r"(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,3}))?)?)?"
    r"(Z|[+-]\d{2}:?\d{2})?$"
)

def parse_iso8601(dt_str: str) -> datetime.datetime:
    m = ISO_FULL.match(dt_str.strip())
    if not m:
        raise ValueError(f"Formato no reconocido: '{dt_str}'. Use ISO 8601.")
    anio, mes, dia = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hora   = int(m.group(4)) if m.group(4) else 0
    minuto = int(m.group(5)) if m.group(5) else 0
    seg    = int(m.group(6)) if m.group(6) else 0
    ms     = int(m.group(7).ljust(3, "0")) * 1000 if m.group(7) else 0
    zona_str = m.group(8)
    if zona_str is None or zona_str == "Z":
        tzinfo = datetime.timezone.utc
    else:
        signo = 1 if zona_str[0] == "+" else -1
        partes = zona_str[1:].replace(":", "")
        offset_h, offset_m = int(partes[:2]), int(partes[2:])
        tzinfo = datetime.timezone(
            datetime.timedelta(hours=signo * offset_h, minutes=signo * offset_m)
        )
    dt = datetime.datetime(anio, mes, dia, hora, minuto, seg, ms, tzinfo=tzinfo)
    return dt.astimezone(datetime.timezone.utc)

# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """El sistema que te consume puede verificar que el agente está vivo."""
    return {"status": "ok"}


@app.post("/ventanas")
def calcular_ventanas(req: ContactRequest):
    """
    Recibe los parámetros y devuelve las ventanas de contacto en JSON.
    """
    try:
        deadline_dt  = parse_iso8601(req.deadline)
        deadline_str = deadline_dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    resultados = programa.calculate_contact_window(
        req.norad_ids,
        req.ubicacion,
        req.grados_horizonte,
        deadline_str,
    )

    if "error" in resultados:
        raise HTTPException(status_code=400, detail=resultados["error"])

    return resultados


@app.get("/tle/{norad_id}")
def obtener_tle(norad_id: str):
    """Devuelve el TLE de un satélite por su NORAD ID."""
    tles = programa.get_tles([norad_id])
    if norad_id not in tles:
        raise HTTPException(status_code=404, detail=f"NORAD ID {norad_id} no encontrado.")
    return tles[norad_id]