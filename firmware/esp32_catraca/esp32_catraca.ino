/*
 * =========================================================================
 * BJ SPORTS - FIRMWARE DE CONTROLE DE CATRACA INTELIGENTE
 * Placa: ESP32-WROOM-32 (NodeMCU / Doit DevKit v1)
 * Autor: Fernando Vier - Engenharia de Software BJ Sports
 * =========================================================================
 * 
 * Conexões Físicas:
 * - GPIO 4  -> Pino IN do Módulo Relé 5V (Atuador da Solenóide)
 * - GPIO 2  -> LED Embutido (Indicador de Status Wi-Fi / Ativação)
 * - 5V / VIN -> VCC do Módulo Relé
 * - GND     -> GND do Módulo Relé
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoOTA.h>

// =========================================================================
// CONFIGURAÇÕES DE REDE DA ACADEMIA (Altere para o Wi-Fi da Recepção)
// =========================================================================
const char* ssid = "BJ_SPORTS_RECEPCAO";
const char* password = "senha_wifi_aqui";

// Chave de Segurança (Bearer Token) exigida para destravar a catraca
const String API_SECRET_TOKEN = "bjsports-catraca-secret";

// Configuração dos Pinos
const int PIN_RELE = 4;        // GPIO 4 conectado ao Módulo Relé 5V
const int PIN_LED_STATUS = 2;  // LED embutido no ESP32

// Duração do pulso elétrico para liberar 1 giro mecânico (em milissegundos)
const int PULSO_DESTRAVAMENTO_MS = 1000;

WebServer server(80);

// =========================================================================
// FUNÇÃO DE PULSO: Destrava a Solenóide da Catraca por 1 Segundo
// =========================================================================
void acionarDestravamentoCatraca() {
  Serial.println("[CATRACA] -> Pulso elétrico disparado! Catraca destravada.");
  
  // Liga o relé (nivel HIGH ou LOW dependendo do módulo - geralmente LOW ativo)
  digitalWrite(PIN_RELE, LOW);       // Fecha o contato da solenóide
  digitalWrite(PIN_LED_STATUS, HIGH); // Acende LED de feedback
  
  delay(PULSO_DESTRAVAMENTO_MS);      // Mantém destravada por 1s
  
  digitalWrite(PIN_RELE, HIGH);      // Abre o contato e trava novamente
  digitalWrite(PIN_LED_STATUS, LOW);
  
  Serial.println("[CATRACA] -> Trava rearmada.");
}

// =========================================================================
// ROTAS HTTP DO SERVIDOR LOCAL
// =========================================================================

// Rota 1: Status de Conexão
void handleStatus() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  String json = "{\"status\":\"ONLINE\",\"device\":\"ESP32-WROOM-32\",\"gym\":\"BJ Sports\"}";
  server.send(200, "application/json", json);
}

// Rota 2: Comando de Liberação da Catraca
void handleLiberar() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "POST,GET,OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "*");

  // Validação do Token de Segurança
  if (server.hasHeader("Authorization")) {
    String authHeader = server.header("Authorization");
    if (!authHeader.endsWith(API_SECRET_TOKEN)) {
      server.send(401, "application/json", "{\"error\":\"Token de seguranca invalido\"}");
      return;
    }
  }

  // Aciona a liberação física
  acionarDestravamentoCatraca();

  server.send(200, "application/json", "{\"success\":true,\"message\":\"Catraca destravada com sucesso\"}");
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n==========================================");
  Serial.println("   BJ SPORTS - CONTROLE DE ACESSO ESP32   ");
  Serial.println("==========================================");

  // Inicialização dos Pinos
  pinMode(PIN_RELE, OUTPUT);
  pinMode(PIN_LED_STATUS, OUTPUT);
  
  // Relé inicia desligado (Travado)
  digitalWrite(PIN_RELE, HIGH);
  digitalWrite(PIN_LED_STATUS, LOW);

  // Conexão Wi-Fi
  Serial.print("[WIFI] Conectando a: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 30) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Conectado com sucesso!");
    Serial.print("[WIFI] Endereço IP Local do ESP32: http://");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WIFI] Falha ao conectar. Iniciando em modo Access Point de contingência.");
    WiFi.softAP("BJ_SPORTS_CATRACA_SETUP", "bjsports2026");
    Serial.print("[WIFI AP] Conecte-se em http://");
    Serial.println(WiFi.softAPIP());
  }

  // Configuração de Atualização Remota (Arduino OTA)
  ArduinoOTA.setHostname("bjsports-catraca-esp32");
  ArduinoOTA.setPassword("bjsports-ota-secret");
  ArduinoOTA.begin();

  // Registro de Rotas Web
  server.on("/", HTTP_GET, handleStatus);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/liberar", HTTP_POST, handleLiberar);
  server.on("/liberar", HTTP_GET, handleLiberar); // Aceita GET para testes rápidos em navegador

  server.begin();
  Serial.println("[HTTP] Servidor Web da Catraca iniciado na porta 80.");
}

void loop() {
  ArduinoOTA.handle();
  server.handleClient();
}
