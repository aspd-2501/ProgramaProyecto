import requests
import pandas as pd
from skyfield.api import Topos, load, EarthSatellite, utc, wgs84
import datetime

def obtener_tles(url):
    """
    Función para obtener TLEs de Celestrak o Space-Track.
    :param url: URL para obtener los TLEs.
    :return: Lista de TLEs.
    """
    response = requests.get(url)
    if response.status_code == 200:
        tles = response.text.splitlines()  
        return tles
    else:
        print(f"Error al obtener TLEs: {response.status_code}")
        return []

# URL de Last 30 Days' Launches de Celestrak para obtener TLEs de satélites
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=tle"
tles = obtener_tles(url)

# Muestra los primeros 3 TLEs como ejemplo (nombre, línea 1, línea 2)
if len(tles) >= 3:
    print(tles[:3])

# Guardar TLEs en CSV (como texto plano)
df = pd.DataFrame(tles, columns=["TLE"])
df.to_csv('tles.csv', index=False)

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

# Procesar TLEs en grupos de 3 (asumiendo que están en orden: nombre, línea1, línea2)
satelites = []
for i in range(0, len(tles) - 2, 3):
    nombre = tles[i].strip()
    tle1 = tles[i+1].strip()
    tle2 = tles[i+2].strip()
    satelites.append((nombre, tle1, tle2))

# Calcular órbita para el primer satélite como ejemplo
if satelites:
    nombre, tle1, tle2 = satelites[0]
    calcular_orbita(tle1, tle2, nombre)
else:
    print("No se encontraron TLEs válidos.")



from skyfield.api import load, Topos
import datetime

# Función para obtener TLEs (simulada para el ejemplo, deberías reemplazarla por la función real)
def obtener_tles_de_norad(norad_id):
    # Aquí deberías obtener los TLEs del satélite utilizando Celestrak o Space-Track
    # Este es un ejemplo de TLE de un satélite ficticio
    tle1 = "1 25544U 98067A   23065.25111111  .00001054  00000-0  25810-4 0  9993"
    tle2 = "2 25544  51.6407  49.2953 0005611 353.3543   6.6389 15.50116238394289"
    return tle1, tle2

# Función para calcular las ventanas de visibilidad
def calcular_ventanas_visibilidad(tle1, tle2, ubicacion, grados_horizonte=10):
    satellite = EarthSatellite(tle1, tle2, 'SAT_NAME', load.timescale())
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

def calcular_ventanas_contacto(tle1, tle2, estacion_terrestre, grados_horizonte=10):
    """
    Calcula las ventanas de contacto entre el satélite y una estación terrestre.
    :param tle1: TLE de la primera línea.
    :param tle2: TLE de la segunda línea.
    :param estacion_terrestre: Ubicación de la estación terrestre (latitud, longitud).
    :param grados_horizonte: Grados sobre el horizonte para considerar el contacto.
    :return: Si el satélite tiene contacto con la estación terrestre (True) o no (False).
    """
    satellite = EarthSatellite(tle1, tle2, 'SAT_NAME', load.timescale())
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
tle1, tle2 = obtener_tles_de_norad("25544")  # Obtener TLEs para el ejemplo
estacion_terrestre = (0, 0)  # Coordenadas de la estación terrestre (latitud, longitud)

ventanas_contacto = calcular_ventanas_contacto(tle1, tle2, estacion_terrestre)
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

