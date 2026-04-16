import json
import requests
from typing import Any

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma2:9b"   # o mistral, qwen2.5, phi3, etc.


def construir_prompt(resultados: dict[str, Any], ubicacion: tuple[float, float], grados_horizonte: float, deadline: str) -> str:
    return f"""
Eres un asistente técnico de contexto orbital.

Tu tarea es explicar, en español claro y preciso, si una misión satelital es factible o no,
usando ÚNICAMENTE la información entregada en el JSON.
No inventes datos, no supongas ventanas inexistentes y no cambies horas.

Debes:
1. Explicar por qué cada satélite es factible o no factible.
2. Mencionar la cantidad de ventanas encontradas.
3. Si existe al menos una ventana antes del deadline, indicar que la misión es factible.
4. Si no existe ninguna ventana antes del deadline, indicar que la misión no es factible.
5. Si no hay ventanas, decirlo explícitamente.
6. Redactar en tono técnico, breve y entendible.

Contexto:
- Ubicación objetivo: lat={ubicacion[0]}, lon={ubicacion[1]}
- Grados sobre horizonte: {grados_horizonte}
- Deadline UTC: {deadline}

JSON de entrada:
{json.dumps(resultados, ensure_ascii=False, indent=2)}

Devuelve la respuesta en este formato:

Resumen general:
...

Detalle por satélite:
- Satélite X:
  ...

No incluyas nada fuera de esa estructura.
""".strip()


def explicar_factibilidad_con_ollama(
    resultados: dict[str, Any],
    ubicacion: tuple[float, float],
    grados_horizonte: float,
    deadline: str,
    model: str = OLLAMA_MODEL,
) -> str:
    prompt = construir_prompt(resultados, ubicacion, grados_horizonte, deadline)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()