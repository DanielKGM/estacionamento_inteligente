#include <WiFi.h>
#include <PubSubClient.h>

#define pin_a 15
#define pin_b 2
#define pin_c 4 
#define pin_d 5 
#define TOPIC_PUBLISH "RECEBE_DADOS_ESP" 

char buf[30];
int val_a, val_b, val_c, val_d;
int lastAState, lastBState, lastCState, lastDState;

const char *ssid = "GAEL";  
const char *password = "mimita1981";  
const char *mqtt_broker = "mqtt.eclipseprojects.io"; 
const int mqtt_port = 1883;  
const char *topic = "esp32/inputs";

WiFiClient espClient;
PubSubClient client(espClient);
void getLeitura();

void setup() {
    Serial.begin(9600);
    pinMode(pin_a, INPUT);
    pinMode(pin_b, INPUT);
    pinMode(pin_c, INPUT);
    pinMode(pin_d, INPUT);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("Conectando ao WiFi...");
    }
    Serial.println("Conectado à rede Wi-Fi");
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callback);
    reconnect();
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    val_a = digitalRead(pin_a);
    val_b = digitalRead(pin_b);
    val_c = digitalRead(pin_c);
    val_d = digitalRead(pin_d);
    if (val_a != lastAState) {
        getLeitura('a', val_a);
        lastAState = val_a;
    }
    if (val_b != lastBState) {
        getLeitura('b', val_b);
        lastBState = val_b;
    }
    if (val_c != lastCState) {
        getLeitura('c', val_c);
        lastCState = val_c;
    }
    if (val_d != lastDState) {
        getLeitura('d', val_d);
        lastDState = val_d;
    }
    delay(1000);
    client.loop();
}

void getLeitura(char pino, int valor) {
    char buf[10];
    dtostrf(valor, 6, 2, buf);
    String topic_pino = topic + String('/') + String(pino);
    Serial.print("Pino ");
    Serial.print(pino);
    Serial.print(": ");
    Serial.println(buf);
    Serial.print("Payload enviado para ");
    Serial.println(topic_pino);
    client.publish(topic_pino.c_str(), buf);
}

void callback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Mensagem no tópico: ");
    Serial.println(topic);
    Serial.print("Conteúdo da mensagem: ");
    for (int i = 0; i < length; i++) {
        Serial.print((char) payload[i]);
    }
    Serial.println();
    Serial.println("-----------------------");
}

void reconnect() {
    while (!client.connected()) {
        String client_id = "esp32-client-";
        client_id += String(WiFi.macAddress());
        Serial.printf("Conectando o cliente %s ao broker MQTT\n", client_id.c_str());
        if (client.connect(client_id.c_str())) {
            Serial.println("Conectado ao broker MQTT!");
            client.subscribe(topic);
        } else {
            Serial.print("Falha na conexão: ");
            Serial.print(client.state());
            delay(2000);
        }
    }
}
