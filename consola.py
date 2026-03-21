import programa

# Consola


def buscar_norad_id(norad_id: list[str]):
    tles = programa.obtener_tles(norad_id)
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

        deadline = input("Deadline (YYYY-MM-DD): ").strip()

        raw_ubic = input("Ubicación del punto de contacto (latitud, longitud): ").strip()
        try:
            ubicacion = tuple(map(float, raw_ubic.split(",")))
            assert len(ubicacion) == 2
        except (ValueError, AssertionError):
            print("Formato de ubicación inválido. Use: lat,lon  (ej: 4.71,-74.07)")
            continue

        resultados = programa.calcular_ventana_contacto(norad_ids, ubicacion, grados_horizonte, deadline)
        formatear_resultado(resultados)


if __name__ == "__main__":
    main()