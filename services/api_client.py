import requests
from models.estacionamento import Estacionamento

def fetch_data(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_estacionamento(uuid: str):
    url = f"https://cidadesinteligentes.lsdi.ufma.br/interscity_lh/catalog/resources/{uuid}"
    response = requests.get(url)
    response.raise_for_status()
    estacionamento_data = response.json()

    # Obtenção de vagas associadas a partir do recurso original
    vagas = estacionamento_data.get('data', {}).get('capabilities', [])
    return Estacionamento.from_api_data(estacionamento_data, vagas=vagas)