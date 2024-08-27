#pip install streamlit
#pip install streamlit-folium
# https://gitlab.com/interscity/interscity-platform/resource-adaptor/-/wikis/home
#https://gitlab.com/interscity/interscity-platform/data-collector/-/wikis/home
#https://gitlab.com/interscity/interscity-platform/resource-cataloguer/-/wikis/home
import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import folium
from streamlit_folium import st_folium

@st.cache_data
def read_resources(nome_arquivo):
  caminho_arquivo = os.path.join('dados', nome_arquivo)

  with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
      dados = json.load(arquivo)

  resources = dados['resources']
  
  return resources

@st.cache_data
def read_environment(nome_arquivo):
  caminho_arquivo = os.path.join('dados', nome_arquivo)

  with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
      dados = json.load(arquivo)

  monitoring = dados['environment_monitoring']
  
  return monitoring

estacionamentos = read_resources('estacionamento_ex2.json')

CENTRO_UFMA = (-2.558, -44.309246)
map = folium.Map(location=CENTRO_UFMA, zoom_start=17, width=1)
for estacionamento in estacionamentos:
   localizacao = estacionamento['lat'], estacionamento['lon']
   folium.Marker(localizacao, popup=estacionamento['description']).add_to(map)

##

st.header('Smart Parking :car:')

st_data = st_folium(map, width= 1000)

if st_data and 'last_object_clicked_popup' in st_data:
    popup_clicado = st_data['last_object_clicked_popup']
    
    estacionamento_selecionado = next((e for e in estacionamentos if e['description'] == popup_clicado), None)
    
    if estacionamento_selecionado:
        st.write(estacionamento_selecionado)
    else:
        st.write("Nenhum estacionamento correspondente encontrado.")
else:
    st.write("Clique em um marcador no mapa para ver mais informações.")