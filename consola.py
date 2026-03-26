import datetime

import programa

import re

# Console

def parse_iso8601(dt_str: str) -> datetime.datetime:
    ISO_FULL    = re.compile( r"^(\d{4})-(\d{2})-(\d{2})"          # fecha obligatoria
                                r"(?:[T ](\d{2}):(\d{2})(?::(\d{2})" # hora:min(:seg opcionales)
                                r"(?:\.(\d{1,3}))?)?)?"              # .milisegundos opcionales
                                r"(Z|[+-]\d{2}:?\d{2})?$"            # zona horaria opcional
                            )
    
    dt_str = dt_str.strip()

    m = ISO_FULL.match(dt_str)
    if not m:
        raise ValueError(
            f"Formato no reconocido: '{dt_str}'.\n"
            "Use ISO 8601, por ejemplo: 2025-06-15  ó  2025-06-15T14:30:00Z"
        )

    anio, mes, dia = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hora   = int(m.group(4))  if m.group(4) else 0
    minuto = int(m.group(5))  if m.group(5) else 0
    seg    = int(m.group(6))  if m.group(6) else 0
    ms     = int(m.group(7).ljust(3, "0")) * 1000 if m.group(7) else 0  # ms → µs
    zona_str = m.group(8)

    # Determinar tz-info
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
    return dt.astimezone(datetime.timezone.utc)   # siempre devuelve UTC
    

def buscar_norad_id(norad_id: list[str]):
    tles = programa.get_tles(norad_id)
    if norad_id in tles:
        return tles[norad_id]
    else:
        return "norad IDs no encontrado."

def formatear_resultado(resultados: dict):
    """Imprime los resultados de forma legible."""
    if "error" in resultados:
        print(f"\nError: {resultados['error']}")
        return

    for norad_id, info in resultados.items():
        print(f"\n{'═'*55}")
        print(f"  Satélite : {info.get('nombre', '?')}  (NORAD {norad_id})")
        print(f"{'═'*55}")

        if "error" in info:
            print(f"Error: {info['error']}")
            continue

        if not info["ventanas"]:
            print("  ⚠  Sin ventanas de contacto en el período indicado.")
        else:
            for i, v in enumerate(info["ventanas"], 1):
                estado = "Yes" if v["Antes del deadline"] else "No"
                print(f"\n  Ventana {i}  {estado}")
                print(f"    AOS              : {v['AOS (UTC)']}")
                print(f"    LOS              : {v['LOS (UTC)']}")
                print(f"    Duración         : {v['Duración (seg)']} seg")
                print(f"    Elev. máxima     : {v['Elevación máx (°)']}°")
                print(f"    Hora elev. máx.  : {v['Hora elevación máx']}")

        estado_mision = "FACTIBLE" if info["factible"] else " NO FACTIBLE"
        print(f"\n  Misión → {estado_mision}")


def main():
    print("=== Sistema de validación de ventanas de contacto ===")
    while True:
        print()
        raw = input("Ingrese NORAD ID(s) separados por coma (o 'salir'): ").strip().upper()
        if raw == "SALIR":
            print("¡Hasta luego!")
            break

        norad_ids = [x.strip() for x in raw.split(",")]

        try:
            grados_horizonte = float(input("Grados sobre el horizonte: ").strip())
        except ValueError:
            print("Valor inválido para grados. Intente de nuevo.")
            continue

        while True:
            raw_deadline = input("Deadline ISO 8601 (ej: 2025-06-15 ó 2025-06-15T14:30:00-05:00): ").strip()
            try:
                deadline_dt = parse_iso8601(raw_deadline)
                print(f"  ✔ Deadline interpretado como: {deadline_dt.strftime('%Y-%m-%dT%H:%M:%SZ')} (UTC)")
                break
            except ValueError as e:
                print(f"  ✘ {e}")

        # Deadline como string UTC para calculate_contact_window
        deadline_str = deadline_dt.strftime("%Y-%m-%d %H:%M:%S")


        raw_ubic = input("Ubicación del punto de contacto (latitud, longitud): ").strip()

        try:
            ubicacion = tuple(map(float, raw_ubic.split(",")))
            assert len(ubicacion) == 2
        except (ValueError, AssertionError):
            print("Formato de ubicación inválido. Use: lat,lon  (ej: 4.71,-74.07)")
            continue

        resultados = programa.calculate_contact_window(norad_ids, ubicacion, grados_horizonte, deadline_str)
        formatear_resultado(resultados)


if __name__ == "__main__":
    main()