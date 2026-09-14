/* BJ Sports ESP32-WROOM-32 — v2.2.0
 * GPIO4: relé ativo LOW; GPIO2: LED; GPIO27: botão de manutenção para GND.
 * Leia README.md antes de gravar. Sem sensor: contabiliza comandos, não passagens.
 */
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <Update.h>
#include <esp_task_wdt.h>
#include <esp_timer.h>
#include <esp_system.h>
#include <esp_idf_version.h>
#include "access_policy.h"

const char* FIRMWARE_VERSION = "v2.2.0";
const int PIN_RELE = 4, PIN_LED = 2, PIN_MANUTENCAO = 27;
const uint32_t MAINTENANCE_MS = 600000;
WebServer server(80);
DNSServer dnsServer;
Preferences prefs;
String wifi_ssid, wifi_pass, api_token, admin_pass, ap_pass, csrf, boot_id;
String allowed_origin = "https://bjsports.com.br";
int pulso_ms = 1000;
unsigned long total_liberacoes = 0, persisted_count = 0;
uint32_t last_flush = 0, last_reconnect = 0;
bool modo_ap = false, maintenance = false, ota_active = false, ota_ok = false;
bool watchdog_ready = false, mdns_started = false, timer_ready = false;
volatile bool pulso_ativo = false;
portMUX_TYPE pulse_mux = portMUX_INITIALIZER_UNLOCKED;
esp_timer_handle_t pulse_timer;
String command_ids[64];
uint32_t command_deadlines[64] = {};

String randomSecret() {
  uint8_t bytes[24];
  esp_fill_random(bytes, sizeof(bytes));
  const char* hex = "0123456789abcdef";
  String result;
  result.reserve(48);
  for (uint8_t b : bytes) { result += hex[b >> 4]; result += hex[b & 15]; }
  return result;
}
String escapeHtml(String value) {
  value.replace("&", "&amp;"); value.replace("<", "&lt;");
  value.replace(">", "&gt;"); value.replace("\"", "&quot;"); value.replace("'", "&#39;");
  return value;
}
void errorResponse(int code, const char* message) {
  server.send(code, "application/json", String("{\"success\":false,\"error\":\"") + message + "\"}");
}
void stopPulse(void*) {
  portENTER_CRITICAL(&pulse_mux);
  digitalWrite(PIN_RELE, HIGH);
  digitalWrite(PIN_LED, LOW);
  pulso_ativo = false;
  portEXIT_CRITICAL(&pulse_mux);
}
bool startPulse() {
  if (!timer_ready || ota_active || pulso_ativo) return false;
  // Timer em tarefa dedicada: não depende do servidor HTTP voltar ao loop.
  // O callback não acessa NVS, String, rede ou Serial.
  portENTER_CRITICAL(&pulse_mux);
  if (esp_timer_start_once(pulse_timer, uint64_t(pulso_ms) * 1000) != ESP_OK) {
    portEXIT_CRITICAL(&pulse_mux); return false;
  }
  digitalWrite(PIN_RELE, LOW);
  digitalWrite(PIN_LED, HIGH);
  pulso_ativo = true;
  portEXIT_CRITICAL(&pulse_mux);
  total_liberacoes++;
  return true;
}
void flushCounter() {
  if (total_liberacoes != persisted_count && !pulso_ativo && !ota_active) {
    if (prefs.putULong("giros", total_liberacoes) == sizeof(unsigned long)) persisted_count = total_liberacoes;
  }
  last_flush = millis();
}
bool maintenanceOpen() { return maintenance && millis() < MAINTENANCE_MS; }
bool adminAuthenticated() { return server.authenticate("admin", admin_pass.c_str()); }
bool requireAdmin(bool mutation = false) {
  if (!adminAuthenticated()) { server.requestAuthentication(DIGEST_AUTH, "BJ Sports"); return false; }
  if (mutation && (!maintenanceOpen() || server.arg("csrf") != csrf)) {
    errorResponse(403, "Manutencao fechada ou CSRF invalido"); return false;
  }
  return true;
}
bool cors() {
  String origin = server.header("Origin");
  if (origin.length() && origin != allowed_origin) { errorResponse(403, "Origem nao permitida"); return false; }
  if (origin.length()) {
    server.sendHeader("Access-Control-Allow-Origin", allowed_origin);
    server.sendHeader("Vary", "Origin");
  }
  server.sendHeader("Cache-Control", "no-store");
  return true;
}
bool requireApi() {
  if (!cors()) return false;
  if (!bj::validBearer(server.header("Authorization").c_str(), api_token.c_str())) {
    errorResponse(401, "Token ausente ou invalido"); return false;
  }
  return true;
}
String page(String body) {
  server.sendHeader("Cache-Control", "no-store");
  server.sendHeader("X-Content-Type-Options", "nosniff");
  return "<!doctype html><html lang='pt-BR'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>BJ Sports Catraca</title><style>body{font:16px system-ui;background:#0b0f19;color:#f8fafc;max-width:520px;margin:30px auto;padding:16px}input,button{box-sizing:border-box;width:100%;padding:12px;margin:8px 0}a{color:#60a5fa}</style><h1>BJ Sports • Catraca</h1>" + body + "</html>";
}
String csrfInput() { return "<input type='hidden' name='csrf' value='" + csrf + "'>"; }
void handleRoot() {
  if (!requireAdmin()) return;
  String body = "<p>Firmware " + String(FIRMWARE_VERSION) + "</p><p>Wi-Fi: " + String(WiFi.status() == WL_CONNECTED ? "conectado" : "desconectado") + "</p>";
  body += "<p>Liberações enviadas: " + String(total_liberacoes) + " • Passagens: sensor não instalado</p>";
  if (!maintenanceOpen()) {
    body += "<p>Para alterar configurações, testar ou atualizar: reinicie com o botão GPIO27 pressionado. Janela de 10 minutos.</p>";
  } else {
    body += "<form method='post' action='/testar'>" + csrfInput() + "<button>Testar pulso (" + String(pulso_ms) + " ms)</button></form>";
    body += "<form method='post' action='/salvar'>" + csrfInput();
    body += "<label>Rede Wi-Fi<input name='ssid' maxlength='32' required value='" + escapeHtml(wifi_ssid) + "'></label>";
    body += "<label>Senha Wi-Fi (vazio mantém a atual)<input type='password' name='pass' maxlength='63'></label>";
    body += "<label>Pulso em ms (300–3000)<input type='number' name='pulso' min='300' max='3000' required value='" + String(pulso_ms) + "'></label>";
    body += "<label>Novo token API (32–128 caracteres; vazio mantém)<input type='password' name='token' minlength='32' maxlength='128' autocomplete='new-password'></label>";
    body += "<button>Salvar e reiniciar</button></form><p><a href='/update'>Atualização OTA</a></p>";
  }
  server.send(200, "text/html", page(body));
}
void handleSalvar() {
  if (!requireAdmin(true)) return;
  if (pulso_ativo || ota_active) { errorResponse(409, "Dispositivo ocupado"); return; }
  String ssid = server.arg("ssid"), pass = server.arg("pass"), token = server.arg("token");
  uint32_t pulse;
  if (!bj::parseUnsigned(server.arg("pulso").c_str(), pulse) || !bj::validPulse(pulse) ||
      !ssid.length() || ssid.length() > 32 || pass.length() > 63 ||
      (pass.length() && pass.length() < 8) || (token.length() && !bj::validToken(token.c_str()))) {
    errorResponse(400, "Configuracao invalida"); return;
  }
  // Validação completa antes de qualquer escrita.
  bool ok = prefs.putString("ssid", ssid) > 0;
  if (pass.length()) ok = (prefs.putString("pass", pass) > 0) && ok;
  if (token.length()) ok = (prefs.putString("token", token) > 0) && ok;
  ok = (prefs.putInt("pulso", pulse) == sizeof(int)) && ok;
  if (!ok) { errorResponse(500, "Falha de persistencia; confira a configuracao"); return; }
  flushCounter();
  server.send(200, "text/html", page("<p>Configuração salva. Reiniciando; reconecte à rede da academia.</p>"));
  delay(200); ESP.restart();
}
void handleApiStatus() {
  if (!requireApi()) return;
  String json = "{\"version\":\"" + String(FIRMWARE_VERSION) + "\",\"boot_id\":\"" + boot_id + "\",\"uptime_ms\":" + String(millis());
  json += ",\"wifi_connected\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false");
  json += ",\"liberacoes_enviadas\":" + String(total_liberacoes) + ",\"passagens_confirmadas\":null";
  json += ",\"pulso_ativo\":" + String(pulso_ativo ? "true" : "false") + ",\"pulso_ms\":" + String(pulso_ms);
  json += ",\"free_heap\":" + String(ESP.getFreeHeap()) + ",\"ready\":" + String(timer_ready && !ota_active ? "true" : "false") + "}";
  server.send(200, "application/json", json);
}
void handleApiLiberar() {
  if (!requireApi()) return;
  String id = server.header("X-Command-ID");
  uint32_t deadline, now = millis();
  if (!bj::validCommandId(id.c_str()) || server.header("X-Boot-ID") != boot_id ||
      !bj::parseUnsigned(server.header("X-Expires-Ms").c_str(), deadline) || !bj::validDeadline(now, deadline)) {
    errorResponse(400, "Comando invalido ou expirado"); return;
  }
  int slot = -1;
  for (int i = 0; i < 64; i++) {
    if (command_ids[i] == id) { errorResponse(409, "Comando ja recebido; nao repetir"); return; }
    if (!command_ids[i].length() || int32_t(now - command_deadlines[i]) > 0) slot = i;
  }
  if (slot < 0 || !startPulse()) { errorResponse(409, "Dispositivo ocupado"); return; }
  command_ids[slot] = id; command_deadlines[slot] = deadline;
  server.send(200, "application/json", "{\"success\":true,\"state\":\"command_accepted\",\"command_id\":\"" + id + "\",\"passage_confirmed\":false}");
}
void handlePreflight() {
  if (!cors()) return;
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Authorization, X-Command-ID, X-Boot-ID, X-Expires-Ms");
  server.send(204);
}
void setupOta() {
  server.on("/update", HTTP_GET, []() {
    if (!requireAdmin()) return;
    if (!maintenanceOpen()) { errorResponse(403, "Abra manutencao fisica"); return; }
    server.send(200, "text/html", page("<p>Use somente binário compilado e verificado. Não há assinatura criptográfica habilitada nesta placa.</p><form method='post' action='/update?csrf=" + csrf + "' enctype='multipart/form-data'><input type='file' name='update' accept='.bin' required><button>Atualizar firmware</button></form>"));
  });
  server.on("/update", HTTP_POST, []() {
    // A janela precisa estar aberta no início; upload já autorizado pode terminar.
    if (!adminAuthenticated() || server.arg("csrf") != csrf) {
      Update.abort(); ota_active = false; ota_ok = false;
      errorResponse(403, "Atualizacao nao autorizada"); return;
    }
    bool success = ota_active && ota_ok && !Update.hasError() && Update.end(true);
    ota_active = false; ota_ok = false;
    if (!success) { Update.abort(); errorResponse(400, "Atualizacao falhou; firmware atual mantido"); return; }
    server.send(200, "text/plain", "Atualizado. Reiniciando.");
    delay(200); ESP.restart();
  }, []() {
    HTTPUpload& upload = server.upload();
    if (watchdog_ready) esp_task_wdt_reset();
    if (upload.status == UPLOAD_FILE_START) {
      ota_ok = false;
      if (!adminAuthenticated() || !maintenanceOpen() || server.arg("csrf") != csrf || pulso_ativo || ota_active) return;
      flushCounter();
      ota_active = Update.begin(UPDATE_SIZE_UNKNOWN);
    } else if (upload.status == UPLOAD_FILE_WRITE && ota_active) {
      if (Update.write(upload.buf, upload.currentSize) != upload.currentSize) { Update.abort(); ota_active = false; }
    } else if (upload.status == UPLOAD_FILE_END && ota_active) {
      ota_ok = upload.totalSize > 0; // Só confirma a partição no handler final autenticado.
    } else if (upload.status == UPLOAD_FILE_ABORTED) {
      Update.abort(); ota_active = false; ota_ok = false;
    }
  });
}
void setup() {
  digitalWrite(PIN_RELE, HIGH); pinMode(PIN_RELE, OUTPUT);
  pinMode(PIN_LED, OUTPUT); digitalWrite(PIN_LED, LOW);
  pinMode(PIN_MANUTENCAO, INPUT_PULLUP);
  Serial.begin(115200);
  if (!prefs.begin("bjsports", false)) { Serial.println("NVS indisponivel; bloqueado"); return; }
  wifi_ssid = prefs.getString("ssid", ""); wifi_pass = prefs.getString("pass", "");
  WiFi.mode(WIFI_STA); // Habilita fonte de entropia RF antes de gerar credenciais.
  admin_pass = prefs.getString("admin", ""); ap_pass = prefs.getString("ap_pass", "");
  bool provision = !admin_pass.length() || !ap_pass.length();
  if (provision) {
    admin_pass = randomSecret(); ap_pass = randomSecret();
    if (!prefs.putString("admin", admin_pass) || !prefs.putString("ap_pass", ap_pass)) return;
    Serial.println("Provisionamento: guarde as credenciais em local seguro.");
    Serial.println("Usuario: admin"); Serial.println("Senha admin: " + admin_pass);
    Serial.println("Senha AP: " + ap_pass);
  }
  api_token = prefs.getString("token", "");
  if (!bj::validToken(api_token.c_str())) {
    api_token = randomSecret();
    if (!prefs.putString("token", api_token)) return;
    Serial.println("Novo token API (substitui legado): " + api_token);
  }
  csrf = randomSecret(); boot_id = randomSecret();
  pulso_ms = prefs.getInt("pulso", 1000);
  if (!bj::validPulse(pulso_ms)) pulso_ms = 1000;
  total_liberacoes = persisted_count = prefs.getULong("giros", 0);
  esp_timer_create_args_t args = {};
  args.callback = stopPulse; args.name = "relay_off";
  timer_ready = esp_timer_create(&args, &pulse_timer) == ESP_OK;
  maintenance = provision || !wifi_ssid.length() || digitalRead(PIN_MANUTENCAO) == LOW;
  if (maintenance) {
    modo_ap = true; WiFi.mode(WIFI_AP_STA);
    WiFi.softAP(("BJ-CATRACA-" + boot_id.substring(0, 6)).c_str(), ap_pass.c_str());
    dnsServer.start(53, "*", WiFi.softAPIP());
  }
  WiFi.setAutoReconnect(true);
  if (wifi_ssid.length()) WiFi.begin(wifi_ssid.c_str(), wifi_pass.c_str());
#if ESP_IDF_VERSION_MAJOR >= 5
  esp_task_wdt_config_t config = {};
  config.timeout_ms = 8000; config.trigger_panic = true;
  esp_err_t wd = esp_task_wdt_init(&config);
  if (wd == ESP_ERR_INVALID_STATE) wd = esp_task_wdt_reconfigure(&config);
#else
  esp_err_t wd = esp_task_wdt_init(8, true);
#endif
  if (wd == ESP_OK) watchdog_ready = esp_task_wdt_add(NULL) == ESP_OK;
  const char* headers[] = {"Authorization", "Origin", "X-Command-ID", "X-Boot-ID", "X-Expires-Ms"};
  server.collectHeaders(headers, 5);
  server.on("/", HTTP_GET, handleRoot);
  server.on("/salvar", HTTP_POST, handleSalvar);
  server.on("/testar", HTTP_POST, []() {
    if (!requireAdmin(true)) return;
    if (!startPulse()) { errorResponse(409, "Dispositivo ocupado"); return; }
    server.send(200, "text/html", page("<p>Pulso iniciado. Passagem não confirmada por sensor.</p><a href='/'>Voltar</a>"));
  });
  server.on("/liberar", HTTP_POST, handleApiLiberar);
  server.on("/liberar", HTTP_OPTIONS, handlePreflight);
  server.on("/status", HTTP_GET, handleApiStatus);
  server.on("/status", HTTP_OPTIONS, handlePreflight);
  server.onNotFound([]() { errorResponse(404, "Rota ou metodo nao permitido"); });
  setupOta(); server.begin();
}
void loop() {
  if (watchdog_ready) esp_task_wdt_reset();
  if (maintenance && millis() >= MAINTENANCE_MS) maintenance = false;
  if (modo_ap) {
    dnsServer.processNextRequest();
    if (!maintenanceOpen() && !ota_active) { dnsServer.stop(); WiFi.softAPdisconnect(true); modo_ap = false; WiFi.mode(WIFI_STA); }
  }
  if (WiFi.status() == WL_CONNECTED && !mdns_started) mdns_started = MDNS.begin("catraca");
  if (wifi_ssid.length() && WiFi.status() != WL_CONNECTED && millis() - last_reconnect >= 30000) {
    last_reconnect = millis(); WiFi.reconnect();
  }
  server.handleClient();
  if (millis() - last_flush >= 60000) flushCounter();
  delay(1);
}
