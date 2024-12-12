# FEITO PARA SER UTILIZADO EM GOOGLE COLAB
#from google.colab import drive
#drive.mount('/content/drive')
# pip install
#!pip install paho-mqtt pandas google-colab
#!pip install "paho-mqtt<2.0.0
#!pip install requests
#!pip install numpy

# imports
import time
from paho.mqtt import client as mqtt_client
import pandas as pd
from google.colab import drive
from datetime import datetime
import pytz
import numpy as np
import requests
import json
import os

# Configurações de conexão ao Broker MQTT
broker = 'mqtt.eclipseprojects.io'
port = 1883
topic_subscribe = "esp32/inputs/#"
client_id = 'BROKER_PC_SUB'

# Fuso horário desejado ('America/Sao_Paulo')
desired_timezone = 'America/Sao_Paulo'

# Cria um objeto de fuso horário
local_timezone = pytz.timezone(desired_timezone)

# Endereço para a API InterSCity
api = 'http://cidadesinteligentes.lsdi.ufma.br'

# Endereço do CSV que será salvo no Google Drive
csv_path = '/content/drive/My Drive/exemplo_mqtt.csv'

topicos_capacidades = {
  "esp32/inputs/a": "vagaA_test3e2",
  "esp32/inputs/b": "vagaB_3teste2",
  "esp32/inputs/c": "vaga3C_teste2",
  "esp32/inputs/d": "vagaD_test3e2"
}

# Realiza conexão ao Broker MQTT
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao Broker MQTT")
            client.subscribe(topic_subscribe)
        else:
            print(f"Falha ao conectar, código de retorno {rc}")
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# Callback para processar as mensagens recebidas
def on_message(client, userdata, msg):
    print(f"Recebido o dado `{msg.payload.decode()}` do tópico `{msg.topic}`")

    # Verifica se o tópico está mapeado no dicionário
    if msg.topic in topicos_capacidades:
        # Adiciona os dados ao DataFrame
        timestamp = datetime.now(pytz.utc).astimezone(local_timezone)
        datetime_str = timestamp.strftime('%m-%d-%Y %H:%M:%S')
        payload = msg.payload.decode()
        df.loc[len(df.index)] = [datetime_str, msg.topic, payload, topicos_capacidades[msg.topic]]

        # Salva os dados no CSV no Google Drive
        save_to_drive()
    else:
        print(f"O tópico `{msg.topic}` não está mapeado no dicionário de capacidades.")

# Função para salvar os dados no CSV no Google Drive
def save_to_drive():
    # Verifica se o arquivo CSV já existe
    if not os.path.isfile(csv_path):
        # Se não existir, cria o arquivo CSV e escreve o cabeçalho com a última linha do df
        df.tail(1).to_csv(csv_path, mode='w', index=False)
    else:
        # Se existir, adiciona a última linha do df ao arquivo CSV
        df.tail(1).to_csv(csv_path, mode='a', header=False, index=False)

def show_capacidades():
    r = requests.get(api+'/catalog/capabilities')

    # Retorno da API
    if(r.status_code == 200):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
    else:
      print('Status code: '+str(r.status_code))

def show_resources():
    r = requests.get(api+'/catalog/resources')

    # Retorno da API
    if(r.status_code == 200):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
    else:
      print('Status code: '+str(r.status_code))

# Função para criar uma capacidade na API
def create_capability(nome, tipo, descricao):
    capability_json = {
      "name": nome,
      "description": descricao,
      "capability_type": tipo
    }

    #Faz uma request para a API e salvar a capacidade
    r = requests.post(api+'/catalog/capabilities/', json=capability_json)

    # Retorna se a capacidade foi "postada" com sucesso ou não
    if(r.status_code == 201):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
      return True
    else:
      print('Status code: '+str(r.status_code))
      return False

def create_resource(descricao, latitude, longitude, capacidades):
    # Cria o recurso do estacionamento
    resource_json = {
      "data": {
        "description": descricao,
        "capabilities": capacidades,
        "status": "active",
        "city": "SLZ",
        "country": "BR",
        "state":"MA",
        "lat": latitude,
        "lon": longitude
      }
    }

    # "Post" do recurso na API
    r = requests.post(api+'/catalog/resources/', json=resource_json)

    # Retorna sucesso ou fracasso da "postagem" do recurso de estacionamento, também salva seu UUID.
    uuid = ''
    if(r.status_code == 201):
      resource = json.loads(r.text)
      uuid = resource['data']['uuid']
      print(json.dumps(resource, indent=2))
    else:
      print('Status code: '+str(r.status_code))
    return uuid

def prepare_API():
    # Lista de topicos únicos do DATAFRAME
    capacidades_list = np.array(df.Capacidade.tolist())
    capacidades_unique = np.unique(capacidades_list).tolist()

    print("Preparando a API...")
    time.sleep(1)
    print("Lista de tópicos da esp32:")
    print(capacidades_unique)
    time.sleep(1)

    # Armazena se a capacidade foi criada ou não
    capabilidade_criada = False

    # Criação das capacidades na API
    for nomeCapacidade in capacidades_unique:
      print("="*20)
      print("Criando a capacidade para '"+nomeCapacidade+"' na API "+api+"...")
      time.sleep(1)
      capabilidade_criada = create_capability(nomeCapacidade,"sensor", "Vaga disponível ou ocupada")
      time.sleep(1)
      if capabilidade_criada == False:
        return ""

    # Criação do recurso na API
    print("Criando recurso 'Estacionamento_Inteligente' na API "+api+"...")
    time.sleep(1)
    uuid_resource = create_resource("Estacionamento_InddteligentdeAA", -2.55972052497871, -44.31196495361665, capacidades_unique)
    time.sleep(1)
    return uuid_resource

def addData_API(uuid_resource):
    # Lê o CSV do Google Drive
    df = pd.read_csv(csv_path)

    # Salva as colunas do CSV em listas
    dates = df.Datetime.tolist()
    capacidades_ = df.Capacidade.tolist()
    payloads = df.Payload.tolist()

    # Converte os dados das capacidades em JSON
    capability_data_json = {
      "data": [{capacidade: value, 'timestamp': date} for capacidade, value, date in zip(capacidades_, payloads, dates)]
    }

    print("Exibindo dados das capacidades salvos no dataframe...")
    time.sleep(1)
    print(capability_data_json);
    time.sleep(1)

    print("Adicionando dados das capacidades ao recurso 'Estacionamento_A' da API "+api+"...")
    time.sleep(1)
    # Adiciona dados das 'capabilities' ao 'resource'
    r = requests.post(api+'/adaptor/resources/'+uuid_resource+'/data/environment_monitoring', json=capability_data_json)
    if(r.status_code == 201):
      print('OK!')
    else:
      print('Status code: '+str(r.status_code))
      return False

    print("Exibindo dados do recurso 'Estacionamento_A'...")
    time.sleep(1)
    # Exibe dados do 'resource'
    r = requests.post(api+'/collector/resources/'+uuid_resource+'/data')
    if(r.status_code == 200):
      content = json.loads(r.text)
      print(json.dumps(content, indent=2, sort_keys=True))
    else:
      print('Status code: '+str(r.status_code))

    return True

def run():
    client = connect_mqtt()
    client.on_message = on_message
    client.loop_start()
    time.sleep(30)  # Executa por 60 segundos, ajuste conforme necessário
    client.loop_stop()

    # Pergunta se quer prosseguir para o consumo dos dados pela API Interscity
    resposta = input("Deseja prosseguir para o consumo dos dados pela API Interscity? (Digite 'sim' para prosseguir): ")

    if resposta.lower() == 'sim':
        uuid_resource = prepare_API()
        addData_API(uuid_resource)
    else:
        print("Operação cancelada pelo usuário.")

if __name__ == '__main__':
    # Inicializa o DataFrame para armazenar os dados
    global data
    data = {'Datetime': [], 'Topic': [], 'Payload': [], 'Capacidade': []}
    global df
    df = pd.DataFrame(data)
    run()