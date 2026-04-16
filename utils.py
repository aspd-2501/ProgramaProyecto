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
 