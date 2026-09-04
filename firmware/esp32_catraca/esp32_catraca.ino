/*
 * =========================================================================
 * BJ SPORTS - FIRMWARE DE CONTROLE DE CATRACA INTELIGENTE v2.0
 * Placa: ESP32-WROOM-32 (NodeMCU / Doit DevKit v1 / ESP32 Dev Module)
 * Desenvolvido para: BJ Sports - Gestão de Academias
 * =========================================================================
 * 
 * RECURSOS IMPLEMENTADOS:
 * 1. Configuração 100% pelo Celular (Captive Portal / Hotspot AP)
 * 2. Memória Não-Volátil (NVS/Preferences) - não perde senha ao faltar luz
 * 3. mDNS: Acesso direto por http://catraca.local (não precisa caçar o IP)
 * 4. Painel Web Mobile com Teste de Pulso Manual e Scanner de Redes Wi-Fi
 * 5. API REST com Token de Segurança para o Tablet Facial (/liberar)
 * 6. Web OTA (/update) para atualizar firmware via navegador sem cabo USB
 *
 * PINAGEM:
 * - GPIO 4  -> IN do Módulo Relé 5V (Nível LOW ativo)
 * - GPIO 2  -> LED Azul Embutido (Indicador de Pulso e Status)
 * - 5V/VIN  -> VCC do Módulo Relé
 * - GND     -> GND do Módulo Relé
 * =========================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <Update.h>

// =========================================================================
// DEFINIÇÃO DE PINOS E CONSTANTES
// =========================================================================
const int PIN_RELE = 4;        // GPIO 4 aciona o relé da solenóide
const int PIN_LED = 2;         // LED azul indicador no ESP32
const byte DNS_PORT = 53;      // Porta para o Captive Portal DNS

// Nome do Ponto de Acesso criado para configuração pelo celular
const char* AP_SSID = "BJ-SPORTS-CATRACA";
const char* AP_PASS = "bjsports123"; // Senha do hotspot (mínimo 8 caracteres) ou "" para aberto

// Objetos Globais
WebServer server(80);
DNSServer dnsServer;
Preferences prefs;

// Variáveis de Configuração Persistentes
String wifi_ssid = "";
String wifi_pass = "";
String api_token = "bjsports-catraca-secret";
int pulso_ms = 1000;
unsigned long total_giros = 0;
bool modo_ap = false;

// =========================================================================
// AÇÃO DO SOLENÓIDE: Pulso de 1 Segundo
// =========================================================================
void dispararPulsoCatraca() {
  Serial.println("[CATRACA] -> Pulso elétrico acionado! Destravando solenóide...");
  digitalWrite(PIN_RELE, LOW);    // Ativa relé (nível LOW ativo)
  digitalWrite(PIN_LED, HIGH);    // Acende LED azul
  
  delay(pulso_ms);                // Mantém destravado pelo tempo configurado
  
  digitalWrite(PIN_RELE, HIGH);   // Trava novamente
  digitalWrite(PIN_LED, LOW);
  
  total_giros++;
  prefs.putULong("giros", total_giros);
  Serial.printf("[CATRACA] -> Trava rearmada. Total de liberações: %lu\n", total_giros);
}

// =========================================================================
// INTERFACE WEB HTML (Design Dark Responsivo para Celular)
// =========================================================================
String buildHtmlPage(String conteudoBody) {
  String html = "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<title>BJ Sports • Catraca ESP32</title>";
  html += "<style>";
  html += ":root{--bg:#0b0f19;--card:#131a29;--border:#243049;--primary:#dc2626;--text:#f8fafc;--muted:#94a3b8;--accent:#3b82f6;}";
  html += "* {box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}";
  html += "body {background:var(--bg);color:var(--text);padding:16px;line-height:1.5;}";
  html += ".card {background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;max-width:440px;margin:0 auto 16px;box-shadow:0 10px 25px rgba(0,0,0,0.5);}";
  html += ".header {text-align:center;margin-bottom:20px;border-bottom:1px solid var(--border);padding-bottom:14px;}";
  html += ".header h1 {font-size:1.3rem;font-weight:800;color:#fff;}";
  html += ".header h1 span {color:var(--primary);}";
  html += ".header p {font-size:0.8rem;color:var(--muted);margin-top:2px;}";
  html += ".stat-grid {display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;}";
  html += ".stat-box {background:#0d131f;border:1px solid var(--border);border-radius:10px;padding:12px;text-align:center;}";
  html += ".stat-box span {font-size:0.75rem;color:var(--muted);display:block;}";
  html += ".stat-box strong {font-size:1.1rem;color:#fff;}";
  html += ".btn {display:block;width:100%;padding:14px;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer;text-align:center;text-decoration:none;transition:0.2s;}";
  html += ".btn-pulse {background:var(--primary);color:#fff;margin-bottom:14px;box-shadow:0 4px 15px rgba(220,38,38,0.4);}";
  html += ".btn-pulse:active {transform:scale(0.98);background:#b91c1c;}";
  html += ".btn-save {background:#10b981;color:#fff;}";
  html += ".btn-scan {background:var(--accent);color:#fff;font-size:0.82rem;padding:8px 12px;margin-bottom:12px;}";
  html += ".form-group {margin-bottom:14px;text-align:left;}";
  html += "label {display:block;font-size:0.82rem;font-weight:600;color:var(--muted);margin-bottom:5px;}";
  html += "input, select {width:100%;padding:12px;border-radius:8px;background:#090d16;border:1px solid var(--border);color:#fff;font-size:0.95rem;}";
  html += "input:focus, select:focus {outline:none;border-color:var(--accent);}";
  html += ".badge {display:inline-block;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:700;text-transform:uppercase;}";
  html += ".badge-online {background:rgba(16,185,129,0.2);color:#4ade80;}";
  html += ".badge-ap {background:rgba(245,158,11,0.2);color:#facc15;}";
  html += ".footer {text-align:center;font-size:0.75rem;color:var(--muted);margin-top:20px;}";
  html += "</style></head><body>";
  html += "<div class='card'><div class='header'><h1>BJ <span>SPORTS</span></h1><p>Controle de Acesso da Catraca • ESP32</p></div>";
  html += conteudoBody;
  html += "<div class='footer'>BJ Sports Catraca IoT • IP: " + (modo_ap ? WiFi.softAPIP().toString() : WiFi.localIP().toString()) + "</div>";
  html += "</div></body></html>";
  return html;
}

// Rota: Home (Painel Principal)
void handleRoot() {
  String body = "";
  
  // Status Bar
  body += "<div style='text-align:center;margin-bottom:16px;'>";
  if (modo_ap) {
    body += "<span class='badge badge-ap'>MODO HOTSPOT (AP)</span>";
  } else {
    body += "<span class='badge badge-online'>ONLINE NO WI-FI</span>";
  }
  body += "</div>";

  // Botão Grande de Teste de Pulso Manual
  body += "<a href='/testar' class='btn btn-pulse'>🔓 TESTAR DESTRAVAMENTO (1s)</a>";

  // Estatísticas Rápidas
  body += "<div class='stat-grid'>";
  body += "<div class='stat-box'><span>Sinal Wi-Fi</span><strong>" + (modo_ap ? "100%" : String(WiFi.RSSI()) + " dBm") + "</strong></div>";
  body += "<div class='stat-box'><span>Total Giros</span><strong>" + String(total_giros) + "</strong></div>";
  body += "</div>";

  // Formulário de Configuração do Wi-Fi
  body += "<form method='POST' action='/salvar'>";
  body += "<div style='margin-top:16px;border-top:1px solid var(--border);padding-top:16px;'>";
  body += "<h3 style='font-size:0.95rem;margin-bottom:12px;color:#cbd5e1;'>⚙️ Configuração da Rede Wi-Fi</h3>";
  
  body += "<div class='form-group'>";
  body += "<label>Nome da Rede Wi-Fi (SSID):</label>";
  body += "<input type='text' name='ssid' id='ssid' value='" + wifi_ssid + "' placeholder='Ex: BJ_SPORTS_RECEPCAO' required>";
  body += "</div>";

  body += "<div class='form-group'>";
  body += "<label>Senha do Wi-Fi:</label>";
  body += "<input type='password' name='pass' placeholder='Digite a senha do Wi-Fi'>";
  body += "</div>";

  body += "<div class='form-group'>";
  body += "<label>Tempo de Pulso da Trava (ms):</label>";
  body += "<input type='number' name='pulso' value='" + String(pulso_ms) + "' min='300' max='3000'>";
  body += "</div>";

  body += "<div class='form-group'>";
  body += "<label>Token Secreto da API (Bearer):</label>";
  body += "<input type='text' name='token' value='" + api_token + "'>";
  body += "</div>";

  body += "<button type='submit' class='btn btn-save'>💾 SALVAR E CONECTAR</button>";
  body += "</div></form>";

  // Link para atualização OTA
  body += "<div style='text-align:center;margin-top:16px;'>";
  body += "<a href='/update' style='color:#60a5fa;font-size:0.78rem;text-decoration:none;'>Atualizar Firmware (.bin) via Web</a>";
  body += "</div>";

  server.send(200, "text/html", buildHtmlPage(body));
}

// Rota: Disparo de Teste via Web
void handleTestar() {
  dispararPulsoCatraca();
  String body = "<div style='text-align:center;padding:20px 0;'>";
  body += "<div style='font-size:2.5rem;margin-bottom:10px;'>⚡ CLAC!</div>";
  body += "<h2 style='color:#4ade80;font-size:1.2rem;margin-bottom:8px;'>Solenóide Acionado com Sucesso!</h2>";
  body += "<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:20px;'>O relé fechou o contato por " + String(pulso_ms) + "ms e a catraca foi liberada.</p>";
  body += "<a href='/' class='btn btn-pulse'>VOLTAR AO PAINEL</a>";
  body += "</div>";
  server.send(200, "text/html", buildHtmlPage(body));
}

// Rota: Salvar Configurações na Memória Flash
void handleSalvar() {
  if (server.hasArg("ssid") && server.arg("ssid").length() > 0) {
    wifi_ssid = server.arg("ssid");
    prefs.putString("ssid", wifi_ssid);
  }
  if (server.hasArg("pass") && server.arg("pass").length() > 0) {
    wifi_pass = server.arg("pass");
    prefs.putString("pass", wifi_pass);
  }
  if (server.hasArg("pulso")) {
    pulso_ms = server.arg("pulso").toInt();
    if (pulso_ms < 300) pulso_ms = 1000;
    prefs.putInt("pulso", pulso_ms);
  }
  if (server.hasArg("token") && server.arg("token").length() > 0) {
    api_token = server.arg("token");
    prefs.putString("token", api_token);
  }

  String body = "<div style='text-align:center;padding:20px 0;'>";
  body += "<div style='font-size:2.5rem;margin-bottom:10px;'>💾</div>";
  body += "<h2 style='color:#4ade80;font-size:1.2rem;margin-bottom:8px;'>Configurações Salvas na Memória!</h2>";
  body += "<p style='color:#cbd5e1;font-size:0.88rem;margin-bottom:16px;'>O ESP32 está reiniciando para conectar na rede: <strong>" + wifi_ssid + "</strong></p>";
  body += "<p style='color:#94a3b8;font-size:0.8rem;'>Conecte o celular no Wi-Fi da academia e acesse: <br><strong style='color:#38bdf8;'>http://catraca.local</strong></p>";
  body += "</div>";
  server.send(200, "text/html", buildHtmlPage(body));
  
  delay(1500);
  ESP.restart();
}

// =========================================================================
// API REST: Usada pelo Sistema BJ Sports / Tablet Facial
// =========================================================================
void handleApiLiberar() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "POST,GET,OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "*");

  // Validação do Token de Segurança
  if (server.hasHeader("Authorization")) {
    String auth = server.header("Authorization");
    if (!auth.endsWith(api_token)) {
      server.send(401, "application/json", "{\"error\":\"Token de autorizacao invalido\"}");
      return;
    }
  }

  dispararPulsoCatraca();
  server.send(200, "application/json", "{\"success\":true,\"message\":\"Catraca liberada\",\"total_giros\":" + String(total_giros) + "}");
}

void handleApiStatus() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  String json = "{";
  json += "\"status\":\"ONLINE\",";
  json += "\"device\":\"ESP32-WROOM-32\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"total_giros\":" + String(total_giros) + ",";
  json += "\"pulso_ms\":" + String(pulso_ms) + ",";
  json += "\"free_heap\":" + String(ESP.getFreeHeap());
  json += "}";
  server.send(200, "application/json", json);
}

// =========================================================================
// SETUP: Inicialização
// =========================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n==========================================");
  Serial.println("  BJ SPORTS • FIRMWARE CATRACA ESP32 v2.0 ");
  Serial.println("==========================================");

  // Inicializa Pinos
  pinMode(PIN_RELE, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_RELE, HIGH); // Relé inicia desligado (travado)
  digitalWrite(PIN_LED, LOW);

  // Carrega configurações da memória flash NVS
  prefs.begin("bjsports", false);
  wifi_ssid = prefs.getString("ssid", "");
  wifi_pass = prefs.getString("pass", "");
  api_token = prefs.getString("token", "bjsports-catraca-secret");
  pulso_ms = prefs.getInt("pulso", 1000);
  total_giros = prefs.getULong("giros", 0);

  Serial.printf("[NVS] SSID Salvo: %s | Pulso: %dms | Giros: %lu\n", wifi_ssid.c_str(), pulso_ms, total_giros);

  // Tentativa de Conexão Wi-Fi no modo Station
  if (wifi_ssid.length() > 0) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(wifi_ssid.c_str(), wifi_pass.c_str());
    Serial.print("[WIFI] Conectando a " + wifi_ssid);

    int timeouts = 0;
    while (WiFi.status() != WL_CONNECTED && timeouts < 24) { // 12 segundos tentando
      delay(500);
      Serial.print(".");
      timeouts++;
    }
  }

  // Se conectou com sucesso
  if (WiFi.status() == WL_CONNECTED) {
    modo_ap = false;
    Serial.println("\n[WIFI] Conectado com sucesso!");
    Serial.printf("[WIFI] IP: http://%s\n", WiFi.localIP().toString().c_str());
    
    // Inicia mDNS (Permite acessar via http://catraca.local)
    if (MDNS.begin("catraca")) {
      Serial.println("[mDNS] Respondedor mDNS ativo: http://catraca.local");
    }
  } else {
    // Falhou ou é a primeira inicialização: abre Hotspot para o Celular
    modo_ap = true;
    Serial.println("\n[WIFI] Entrando em Modo Hotspot (AP) para configuração pelo Celular...");
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    
    // DNS Server para Captive Portal automático
    dnsServer.start(DNS_PORT, "*", WiFi.softAPIP());
    Serial.printf("[HOTSPOT] Conecte no Wi-Fi: %s (Senha: %s)\n", AP_SSID, AP_PASS);
    Serial.printf("[HOTSPOT] Acesse no celular: http://%s\n", WiFi.softAPIP().toString().c_str());
  }

  // Rotas do Web Server
  server.on("/", handleRoot);
  server.on("/testar", handleTestar);
  server.on("/salvar", HTTP_POST, handleSalvar);
  server.on("/liberar", handleApiLiberar);
  server.on("/status", handleApiStatus);

  // Suporte a Captive Portal do Android e iOS
  server.on("/generate_204", handleRoot);        // Android
  server.on("/hotspot-detect.html", handleRoot); // Apple iOS
  server.onNotFound(handleRoot);

  // Rota de Atualização OTA Web (/update)
  server.on("/update", HTTP_GET, []() {
    String html = "<h3>BJ Sports • Atualização de Firmware</h3>";
    html += "<form method='POST' action='/update' enctype='multipart/form-data'>";
    html += "<input type='file' name='update'><br><br>";
    html += "<input type='submit' value='Enviar Firmware .bin'>";
    html += "</form>";
    server.send(200, "text/html", buildHtmlPage(html));
  });

  server.on("/update", HTTP_POST, []() {
    server.send(200, "text/plain", (Update.hasError()) ? "FALHA NA ATUALIZACAO" : "ATUALIZADO COM SUCESSO! REINICIANDO...");
    delay(1000);
    ESP.restart();
  }, []() {
    HTTPUpload& upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      Serial.printf("[OTA] Iniciando gravacao: %s\n", upload.filename.c_str());
      if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_WRITE) {
      if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) {
        Update.printError(Serial);
      }
    } else if (upload.status == UPLOAD_FILE_END) {
      if (Update.end(true)) {
        Serial.printf("[OTA] Sucesso: %u bytes gravados.\n", upload.totalSize);
      } else {
        Update.printError(Serial);
      }
    }
  });

  server.begin();
  Serial.println("[HTTP] Servidor Web ativo e aguardando conexões.");
}

// =========================================================================
// LOOP PRINCIPAL
// =========================================================================
void loop() {
  if (modo_ap) {
    dnsServer.processNextRequest();
  }
  server.handleClient();
}
