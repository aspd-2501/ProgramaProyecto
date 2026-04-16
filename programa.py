import requests
import pandas as pd
from skyfield.api import Topos, load, EarthSatellite, utc, wgs84
import datetime
from explicator import explicar_factibilidad_con_ollama

# Programa principal


def get_tles(norad_ids: list[str]) -> dict:
    """
    Obtiene TLEs de Celestrak para una lista de NORAD IDs específicos.
    :param norad_ids: Lista de NORAD IDs (e.g. ["25544", "48274"]).
    :return: Diccionario de TLEs con información detallada, indexado por id del satélite.
    """
    tles_dict = {}

    for norad_id in norad_ids:
        url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener TLE para NORAD ID {norad_id}: {e}")
            continue

        if response.status_code != 200:
            print(f"Error al obtener TLE para NORAD ID {norad_id}: HTTP {response.status_code}")
            continue

        lines = response.text.strip().splitlines()

        if len(lines) < 3:
            print(f"Advertencia: No se encontraron datos TLE válidos para NORAD ID {norad_id}.")
            continue

        name = lines[0].strip()
        tle1  = lines[1].strip()
        tle2  = lines[2].strip()

        if len(tle1) < 69 or len(tle2) < 69:
            print(f"Advertencia: Línea TLE incompleta para {name} (NORAD {norad_id}).")
            continue

        print(f"TLE obtenido para: {name}")

        # Línea 1
        number = tle1[2:7].strip()
        classification = tle1[7]
        international_designator = tle1[9:17].strip()
        epoch_time = tle1[18:32].strip()
        checksum1 = tle1[68]

        # Línea 2
        inclination = tle2[8:16].strip()
        right_ascension = tle2[17:25].strip()
        eccentricity = "0." + tle2[26:33].strip()
        argument_perigee = tle2[34:42].strip()
        mean_anomaly = tle2[43:51].strip()
        mean_motion = tle2[52:63].strip()
        revolutions = tle2[63:68].strip()
        checksum2 = tle2[68]

        tles_dict[norad_id] = {
            "NAME": name,
            "NORAD ID": norad_id,
            "TLE Line 1": tle1,
            "TLE Line 2": tle2,
            "International Designator": international_designator,
            "NORAD Catalog Number": number,
            "Classification": classification,
            "Epoch Time": epoch_time,
            "Checksum Line 1": checksum1,
            "Inclination (degrees)": inclination,
            "Right Ascension (degrees)": right_ascension,
            "Eccentricity": eccentricity,
            "Argument of Perigee (degrees)": argument_perigee,
            "Mean Anomaly (degrees)": mean_anomaly,
            "Mean Motion (rev/day)": mean_motion,
            "Revolutions": revolutions,
            "Checksum Line 2": checksum2,
            "tle1": tle1,
            "tle2": tle2
        }

    return tles_dict


# Ejemplo de uso
#norad_ids = ["25544", "48274", "43013"]   # ISS + dos satélites de ejemplo
#tles = get_tles(norad_ids)
#print(tles)


# 1. Calcular ventana de contacto 

def calculate_contact_window(norad_ids: list[str], ubicacion: tuple, grados_horizonte: float, deadline: str):
    """
    Calcula las ventanas de contacto para una lista de satélites.

    :param norad_ids: Lista de NORAD IDs.
    :param ubicacion: Tupla (latitud, longitud) del punto de contacto.
    :param grados_horizonte: Elevación mínima sobre el horizonte (grados).
    :param deadline: Fecha límite en formato 'YYYY-MM-DD'.
    :return: Diccionario con resultados por satélite.
    """
    
    # Parsear el deadline
    try:
        fecha_deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=datetime.timezone.utc
        )
    except ValueError:
        return {"error": f"Formato de fecha inválido: '{deadline}'. Use YYYY-MM-DD HH:MM:SS."}

    # Obtener TLEs
    tles = get_tles(norad_ids)
    if not tles:
        return {"error": "No se pudieron obtener TLEs para los NORAD IDs proporcionados."}

    ts = load.timescale()
    estacion = wgs84.latlon(ubicacion[0], ubicacion[1])

    # Ventana de búsqueda: desde ahora hasta el deadline (máx. 7 días)
    ahora = datetime.datetime.now(datetime.timezone.utc)
    if fecha_deadline <= ahora:
        return {"error": "El deadline ya pasó. Ingrese una fecha futura."}

    delta_dias = (fecha_deadline - ahora).total_seconds() / 86400
    delta_dias = min(delta_dias, 7.0)  # Skyfield recomienda máx ~7 días por precisión

    t0 = ts.from_datetime(ahora)
    t1 = ts.from_datetime(ahora + datetime.timedelta(days=delta_dias))

    resultados = {}

    for norad_id, tle_info in tles.items():
        nombre = tle_info["NAME"]
        tle1   = tle_info["TLE Line 1"]
        tle2   = tle_info["TLE Line 2"]

        satellite = EarthSatellite(tle1, tle2, nombre, ts)

        # tipo 0 = AOS (rise), tipo 1 = culminación, tipo 2 = LOS (set)
        try:
            tiempos, eventos = satellite.find_events(
                estacion, t0, t1, altitude_degrees=grados_horizonte
            )
        except Exception as e:
            resultados[norad_id] = {"nombre": nombre, "error": str(e)}
            continue

        # Agrupar en ventanas AOS → LOS
        ventanas = []
        aos = None
        max_elev = 0.0
        max_elev_time = None

        for t, evento in zip(tiempos, eventos):
            dt = t.utc_datetime()
            diferencia = satellite - estacion
            topocentric = diferencia.at(t)
            alt, az, distancia = topocentric.altaz()

            if evento == 0:  # AOS
                aos = dt
                max_elev = alt.degrees
                max_elev_time = dt

            elif evento == 1:  # Culminación (elevación máxima)
                max_elev = alt.degrees
                max_elev_time = dt

            elif evento == 2 and aos is not None:  # LOS
                los = dt
                duracion_seg = (los - aos).total_seconds()
                ventanas.append({
                    "AOS (UTC)":             aos.strftime("%Y-%m-%d %H:%M:%S"),
                    "LOS (UTC)":             los.strftime("%Y-%m-%d %H:%M:%S"),
                    "Duración (seg)":        round(duracion_seg),
                    "Elevación máx (°)":     round(max_elev, 2),
                    "Hora elevación máx":    max_elev_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Antes del deadline":    los <= fecha_deadline,
                })
                aos = None

        factible = any(v["Antes del deadline"] for v in ventanas)

        resultados[norad_id] = {
            "nombre":         nombre,
            "ventanas":       ventanas,
            "total_ventanas": len(ventanas),
            "factible":       factible,
        }

    return resultados

def construir_justificacion_base(resultados: dict) -> dict:
    justificaciones = {}

    for norad_id, info in resultados.items():
        if "error" in info:
            justificaciones[norad_id] = (
                f"Se presentó un error al procesar el satélite: {info['error']}"
            )
            continue

        ventanas = info.get("ventanas", [])
        factible = info.get("factible", False)

        if not ventanas:
            justificaciones[norad_id] = (
                "No se encontraron ventanas de contacto dentro del período evaluado."
            )
        elif factible:
            justificaciones[norad_id] = (
                "La misión es factible porque existe al menos una ventana de contacto "
                "que ocurre antes del deadline establecido."
            )
        else:
            justificaciones[norad_id] = (
                "La misión no es factible porque, aunque se encontraron ventanas de contacto, "
                "ninguna cumple la condición temporal definida frente al deadline."
            )

    return justificaciones

def calculate_contact_window_with_explanation(
    norad_ids: list[str],
    ubicacion: tuple,
    grados_horizonte: float,
    deadline: str,
    usar_llm: bool = True,
    model: str = "gemma2:9b",
):
    resultados = calculate_contact_window(
        norad_ids=norad_ids,
        ubicacion=ubicacion,
        grados_horizonte=grados_horizonte,
        deadline=deadline,
    )

    if not usar_llm:
        return {
            "resultados": resultados,
            "explicacion": None,
        }

    justificaciones_base = construir_justificacion_base(resultados)

    try:
        explicacion = explicar_factibilidad_con_ollama(
            resultados=resultados,
            ubicacion=ubicacion,
            grados_horizonte=grados_horizonte,
            deadline=deadline,
            justificaciones_base=justificaciones_base,
            model=model,
        )
    except Exception as e:
        explicacion = f"No se pudo generar la explicación con Ollama: {str(e)}"

    return {
        "resultados": resultados,
        "explicacion": explicacion,
        "justificaciones_base": justificaciones_base,
    }


