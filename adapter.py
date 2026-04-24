from models import VentanaContacto, ResultadoSatelite, ContextoOrbital


def adaptar_resultado(
    raw: dict,
    deadline: str,
    ubicacion: tuple,
    grados_horizonte: float,
) -> ContextoOrbital:
    """
    Transforma el output de calculate_contact_window_with_explanation()
    al schema estandarizado ContextoOrbital.
    """
    resultados_raw = raw.get("resultados", {})
    explicacion = raw.get("explicacion", None)
    justificaciones = raw.get("justificaciones_base", {})

    satelites: list[ResultadoSatelite] = []

    for norad_id, info in resultados_raw.items():

        # Si hubo error en este satélite, igual lo incluimos con factible=False
        if "error" in info:
            satelites.append(ResultadoSatelite(
                norad_id=norad_id,
                nombre=info.get("nombre", norad_id),
                ventanas_los=[],
                total_ventanas=0,
                factible=False,
                justificacion=justificaciones.get(
                    norad_id,
                    f"Error al procesar: {info['error']}"
                ),
            ))
            continue

        ventanas_los = [
            VentanaContacto(
                aos_utc=v["AOS (UTC)"],
                los_utc=v["LOS (UTC)"],
                duracion_seg=v["Duración (seg)"],
                elevacion_max_grados=v["Elevación máx (°)"],
                antes_del_deadline=v["Antes del deadline"],
            )
            for v in info.get("ventanas", [])
        ]

        satelites.append(ResultadoSatelite(
            norad_id=norad_id,
            nombre=info["nombre"],
            ventanas_los=ventanas_los,
            total_ventanas=info["total_ventanas"],
            factible=info["factible"],
            justificacion=justificaciones.get(norad_id, ""),
        ))

    # Opción A: factible si al menos un satélite es factible
    mision_factible = any(s.factible for s in satelites)

    return ContextoOrbital(
        deadline_utc=deadline,
        ubicacion_lat=ubicacion[0],
        ubicacion_lon=ubicacion[1],
        grados_horizonte=grados_horizonte,
        satelites=satelites,
        mision_factible=mision_factible,
        explicacion_llm=explicacion,
    )