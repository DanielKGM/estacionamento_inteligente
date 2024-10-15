import streamlit as st
import os
import json
import folium
from streamlit_folium import st_folium
from datetime import datetime

@st.cache_data
def read_resources(nome_arquivo):
    caminho_arquivo = os.path.join('dados', nome_arquivo)
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
    return dados['resources']

@st.cache_data
def read_environment(nome_arquivo):
    caminho_arquivo = os.path.join('dados', nome_arquivo)
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
    return dados['environment_monitoring']

def calcular_tempo_passado(data_string):
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
    
st.set_page_config(page_title="Smart Parking", layout="wide")



# Carrega os dados dos estacionamentos
estacionamentos = read_resources('estacionamento_ex2.json')

# Cria o mapa
CENTRO_UFMA = (-2.558, -44.309246)
map = folium.Map(location=CENTRO_UFMA, zoom_start=17, width=1, height=0.5)
for estacionamento in estacionamentos:
    localizacao = estacionamento['lat'], estacionamento['lon']
    folium.Marker(localizacao, popup=estacionamento['description'], icon=folium.Icon(prefix='fa', icon='car')).add_to(map)

# Renderiza o mapa
st_data = st_folium(map, use_container_width=True, returned_objects=['last_object_clicked_popup'])

# Configura a sidebar
st.sidebar.header('Smart Parking :car:')

if st_data and 'last_object_clicked_popup' in st_data:
    popup_clicado = st_data['last_object_clicked_popup']
    estacionamento_selecionado = next((e for e in estacionamentos if e['description'] == popup_clicado), None)

    if estacionamento_selecionado:
        # Calcula o número de vagas ocupadas e o total de vagas
        vagas = estacionamento_selecionado['capabilities']
        total_vagas = len(vagas)
        vagas_ocupadas = sum(1 for detalhes in vagas.values() if detalhes[0]['value'] == '1')

        # Exibe o título na sidebar com a descrição e a informação das vagas
        titulo = f"{estacionamento_selecionado['description']} ({vagas_ocupadas}/{total_vagas} vagas ocupadas)"
        st.sidebar.subheader(titulo)

        # Exibe um expander na sidebar com o status detalhado de cada vaga
        with st.sidebar.expander("Detalhes", expanded=True):
            
            for vaga, detalhes in vagas.items():
                status = "ocupada" if detalhes[0]['value'] == '1' else "disponível"
                tempo_passado = calcular_tempo_passado(detalhes[0]['date'])
                st.write(f"{vaga}: {status} (há {tempo_passado})")
    else:
        st.sidebar.write("Nenhum estacionamento selecionado.")
else:
    st.sidebar.subheader("Selecione um estacionamento no mapa.")
