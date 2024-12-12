from datetime import datetime

def calcular_tempo_passado(data_string: str) -> str:
    data_status = datetime.strptime(data_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    tempo_passado = datetime.utcnow() - data_status
    dias = tempo_passado.days
    horas, segundos = divmod(tempo_passado.seconds, 3600)
    minutos, _ = divmod(segundos, 60)

    if dias > 0:
        return f"{dias} dias"
    elif horas > 0:
        return f"{horas} horas"
    elif minutos > 0:
        return f"{minutos} minutos"
    else:
        return "menos de 1 minuto"
