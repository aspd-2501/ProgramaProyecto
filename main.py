import requests
import pandas as pd
from skyfield.api import Topos, load, EarthSatellite, utc, wgs84
import datetime

import requests

# DONE
def obtener_tles(norad_ids: list[str]) -> dict:
    """
    Obtiene TLEs de Celestrak para una lista de NORAD IDs específicos.
    :param norad_ids: Lista de NORAD IDs (e.g. ["25544", "48274"]).
    :return: Diccionario de TLEs con información detallada, indexado por id del satélite.
    """
    tles_dict = {}

    for norad_id in norad_ids:
        url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"
        response = requests.get(url)

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
norad_ids = ["25544", "48274", "43013"]   # ISS + dos satélites de ejemplo
tles = obtener_tles(norad_ids)
print(tles)











# Guardar TLEs en CSV (como texto plano)
def guardar_tles_en_csv(tles, filename):
    """
    Guarda los TLEs en un archivo CSV.
    :param tles: Lista de TLEs.
    :param filename: Nombre del archivo CSV.
    """
    df = pd.DataFrame(tles, columns=["TLE"])
    df.to_csv(filename, index=False)

def calcular_orbita(tle1, tle2, nombre):
    """
    Propaga la órbita a partir de dos líneas de TLE.
    :param tle1: Primera línea de TLE.
    :param tle2: Segunda línea de TLE.
    :param nombre: Nombre del satélite.
    :return: Posición del satélite en un momento dado.
    """
    satellite = EarthSatellite(tle1, tle2, nombre, load.timescale())  # Carga los TLEs
    
    ts = load.timescale()
    t = ts.now()  # Tiempo UTC actual
    
    # Propaga la órbita del satélite
    position = satellite.at(t)
    print(f"Posición de {nombre}: {position}")
    return position


# Función para calcular las ventanas de visibilidad
def calcular_ventanas_visibilidad(tle: dict, ubicacion, grados_horizonte=10):
    satellite = EarthSatellite(tle1, 'SAT_NAME', load.timescale())
    ts = load.timescale()
    tiempo_actual = ts.now()
    
    # Ubicación del objetivo (latitud y longitud)
    objetivo = wgs84.latlon(ubicacion[0], ubicacion[1])
    
    # Calcular la elevación sobre el horizonte
    try:
        astrometric = objetivo.at(tiempo_actual).observe(satellite)
        alt, az, d = astrometric.apparent().altaz()
        
        # Verificar si la elevación es mayor que el umbral de visibilidad
        if alt.degrees > grados_horizonte:
            return True  # Ventana de visibilidad disponible
        else:
            return False  # No hay ventana de visibilidad
    except Exception as e:
        print(f"Error en calcular_ventanas_visibilidad: {e}")
        return True  # Retornar True por defecto si hay error

def calcular_ventanas_contacto(tle1: dict, estacion_terrestre, grados_horizonte=10):
    """
    Calcula las ventanas de contacto entre el satélite y una estación terrestre.
    :param tle1: TLE de la primera línea.
    :param tle2: TLE de la segunda línea.
    :param estacion_terrestre: Ubicación de la estación terrestre (latitud, longitud).
    :param grados_horizonte: Grados sobre el horizonte para considerar el contacto.
    :return: Si el satélite tiene contacto con la estación terrestre (True) o no (False).
    """
    satellite = EarthSatellite(tle1, 'SAT_NAME', load.timescale())
    ts = load.timescale()
    
    # Tiempo actual (UTC)
    tiempo_actual = ts.now()
    
    # Ubicación de la estación terrestre
    estacion = wgs84.latlon(estacion_terrestre[0], estacion_terrestre[1])
    
    # Calcular la elevación sobre el horizonte para la estación terrestre
    try:
        astrometric = estacion.at(tiempo_actual).observe(satellite)
        alt, az, d = astrometric.apparent().altaz()
        
        # Comparar la elevación con el umbral para contacto
        if alt.degrees > grados_horizonte:
            return True  # El satélite tiene contacto con la estación
        else:
            return False  # El satélite no tiene contacto con la estación
    except Exception as e:
        print(f"Error en calcular_ventanas_contacto: {e}")
        return True  # Retornar True por defecto si hay error

# Ejemplo de uso con TLEs y estación terrestre
tle1 = obtener_tles("25544")  # Obtener TLEs para el ejemplo
estacion_terrestre = (0, 0)  # Coordenadas de la estación terrestre (latitud, longitud)

ventanas_contacto = calcular_ventanas_contacto(tle1, estacion_terrestre)
print("Contacto con estación terrestre:", "Sí" if ventanas_contacto else "No")

# Función principal para validar la misión
def validar_mision(norad_id, fecha_objetivo, ubicacion, grados_horizonte):
    """
    Valida si la misión satelital es factible según las ventanas de visibilidad y contacto.
    :param norad_id: Identificador del satélite.
    :param fecha_objetivo: Fecha objetivo para la misión.
    :param ubicacion: Ubicación del objetivo (latitud, longitud).
    :param grados_horizonte: Grados sobre el horizonte.
    :return: Si la misión es factible o no.
    """
    # Obtener los TLEs del satélite
    tle1, tle2 = obtener_tles_de_norad(norad_id)
    
    # Calcular las ventanas de visibilidad
    ventanas_visibilidad = calcular_ventanas_visibilidad(tle1, tle2, ubicacion)
    if not ventanas_visibilidad:
        return "Misión no factible: Sin ventana de visibilidad."
    
    # Calcular las ventanas de contacto con estaciones terrestres
    ventanas_contacto = calcular_ventanas_contacto(tle1, tle2, ubicacion)
    if not ventanas_contacto:
        return "Misión no factible: Sin ventana de contacto con estaciones terrestres."
    
    # Si ambas ventanas están disponibles, la misión es factible
    return "Misión factible."

# Ejemplo de uso de la función
norad_id = "25544"  # NORAD ID de un satélite
fecha_objetivo = "2023-06-01"  # Fecha de la misión
ubicacion = (0, 0)  # Coordenadas del objetivo (latitud, longitud)
grados_horizonte = 10  # Grados sobre el horizonte

resultado = validar_mision(norad_id, fecha_objetivo, ubicacion, grados_horizonte)
print(resultado)



#########################################
#TODO: - Mejorar la función de validación para considerar múltiples estaciones terrestres y diferentes umbrales de visibilidad.
#      - Verificación de las ventanas de visibilidad: verificar las condiciones para vas ventanas de visibilidad.

