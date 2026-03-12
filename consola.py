import programa

def buscar_norad_id(norad_id:list[str]):
    
    tles = programa.obtener_tles(norad_id)
    if norad_id in tles:
        return tles[norad_id]
    else:
        return "norad IDs no encontrado."

def main():
    # Le debe entrar los NORAD IDs, los grados sobre el horizonte, y la fecha objetivo para validar la misión y la ubicación del punto de contacto
    # Debe retornar la ventana de contacto con estaciones terrestres, la ventana de visibilidad, y si la misión es factible o no.
    print("=== Sistema de búsqueda por norad ID ===")
    while True:
        norad_id = input("\nIngrese el norad ID (o 'salir' para terminar): ").strip().upper()

        
        if norad_id == "SALIR":
            print("¡Hasta luego!")
            break
        
        resultado = buscar_norad_id(norad_id)
        print(f"\nResultado para {norad_id}:")
        print(resultado)

if __name__ == "__main__":
    main()
