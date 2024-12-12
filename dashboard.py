import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

#@st.cache_data
def fetch_resources(url):
    response = requests.get(url)
    response.raise_for_status()  # Levanta uma exceção se o status for um código de erro
    dados = response.json()
    return dados['resources']

#@st.cache_data
def fetch_coordinates(uuid):
    url = f"https://cidadesinteligentes.lsdi.ufma.br/interscity_lh/catalog/resources/{uuid}"
    response = requests.get(url)
    response.raise_for_status()  # Levanta uma exceção se o status for um código de erro
    dados = response.json()
    # Corrige a chave de acesso às coordenadas
    if 'data' in dados and 'lat' in dados['data'] and 'lon' in dados['data']:
        return dados['data']['lat'], dados['data']['lon'], dados['data']['description']
    else:
        st.warning(f"Coordenadas não encontradas para UUID {uuid}. Dados retornados: {dados}")
        return None  # Retorna None se não encontrar as coordenadas

def calcular_tempo_passado(data_string):
    data_status = datetime.strptime(data_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    tempo_passado = datetime.now() - data_status
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

st.set_page_config(page_title="Smart Parking", layout="wide")

# URL do endpoint para obter os dados
URL = "https://cidadesinteligentes.lsdi.ufma.br/interscity_lh/collector/resources/data/last"

# Carrega os dados dos estacionamentos
try:
    estacionamentos = fetch_resources(URL)
except requests.RequestException as e:
    st.error(f"Erro ao carregar os dados: {e}")
    estacionamentos = []

# Cria o mapa
CENTRO_UFMA = (-2.558, -44.309246)
map = folium.Map(location=CENTRO_UFMA, zoom_start=17, width=1, height=0.5)

for estacionamento in estacionamentos:
    uuid = estacionamento['uuid']

    try:
        dados = fetch_coordinates(uuid)
        if dados:
            lat, lon, descricao = dados  # A descrição é extraída junto com as coordenadas
    except requests.RequestException as e:
        st.warning(f"Erro ao obter coordenadas para UUID {uuid}: {e}")
        continue  # Continuar com o próximo estacionamento em caso de erro

    if dados:
        # Extrai as vagas e seus status
        vagas = estacionamento['capabilities']['environment_monitoring']
        vagas_status = {}
        for vaga_info in vagas:
            for vaga, status in vaga_info.items():
                if vaga != "date":  # Ignorar o campo "date"
                    vagas_status[vaga] = {"status": status, "date": vaga_info["date"]}

        # Cria um popup com informações detalhadas
        popup_info = f"<b>Descrição:</b> {descricao}<br><br>"  # Exibe a descrição ao invés do UUID
        for vaga, detalhes in vagas_status.items():
            status_str = "❌" if detalhes["status"] == 1.0 else "✔️"
            tempo = calcular_tempo_passado(detalhes["date"])
            popup_info += f"{vaga}: {status_str} (há {tempo})<br>"

        folium.Marker(
            [lat, lon],  # Usa as coordenadas para a localização
            popup=popup_info,
            icon=folium.Icon(prefix='fa', icon='car')
        ).add_to(map)

# Renderiza o mapa
st_data = st_folium(map, use_container_width=True, returned_objects=['last_object_clicked_popup'])

# Configura a sidebar
st.sidebar.header('Smart Parking :car:')

if st_data and 'last_object_clicked_popup' in st_data:
    popup_clicado = st_data['last_object_clicked_popup']
    st.sidebar.write(popup_clicado)
else:
    st.sidebar.subheader("Selecione um estacionamento no mapa.")
