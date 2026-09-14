# BJ Sports ESP32 — v2.2.0

Status: implementação local; requer ensaio na placa antes de uso operacional.

## Plano de ação e resultado

1. Segurança: token Bearer obrigatório e exato, credenciais exclusivas, painel Digest,
   CSRF nas ações administrativas e manutenção física com janela de 10 minutos.
2. Acionamento: 300–3000 ms validados no firmware, rejeição enquanto ocupado,
   desligamento por esp_timer em tarefa própria; nenhuma gravação NVS durante pulso.
3. Protocolo: POST autenticado, preflight sem acionamento, origem permitida explícita,
   ID de comando e prazo relativo ao boot; rejeição de repetição durante validade.
4. Confiabilidade: conexão Wi-Fi sem espera bloqueante, reconexão periódica,
   watchdog com verificação de retorno, contador salvo a cada 60 segundos.
5. Tablet: confirmação explícita do ESP, timeout, nenhuma repetição automática,
   nenhum registro fictício de giro. Correção de sintaxe no fallback CPF.
6. Distribuição: projeto completo ZIP e versão derivada do fonte; binário só é
   servido se manifesto corresponder ao binário e aos arquivos do projeto.
7. Pendentes de hardware: sensor de passagem, proteção elétrica e medição temporal,
   teste do navegador real, assinatura criptográfica/rollback OTA e ensaio prolongado.

## Compilar

Instale PlatformIO Core 6.1.18 em ambiente isolado e execute na pasta firmware:

    pio run -e esp32dev

Plataforma fixada espressif32 6.9.0 (Arduino-ESP32 2.0.17), placa esp32dev,
partições default.csv com dois slots OTA. O código contempla a assinatura do
watchdog IDF 5, mas apenas o ambiente fixado acima integra esta validação.
Resultado: .pio/build/esp32dev/firmware.bin. Não enviar o .ino sozinho: ele depende
 de access_policy.h. O ZIP da página inclui ambos e a configuração de compilação.

## Instalação e credenciais

- Guarde fonte/binário anterior e exporte a configuração existente antes da troca.
- Primeira gravação via USB por operador, com relé desconectado da catraca.
- Abra monitor serial em 115200 baud. Credenciais de admin/AP são exibidas apenas
  quando criadas; token legado é substituído por um token aleatório de 48 caracteres.
  Guarde as credenciais fora de Git/logs compartilhados.
- Migração conserva SSID/senha e contador legado; este contador representa liberações,
  nunca prova de giro. Pulso legado fora de limite volta para 1000 ms.
- Na primeira configuração, conecte ao AP BJ-CATRACA-xxxxxx usando a senha exclusiva.
  Abra http://192.168.4.1, usuário admin. Configure Wi-Fi e, se desejar, novo token.
- Próximas manutenções: botão entre GPIO27 e GND, pressionado ao reiniciar.
  Solte depois do boot. A janela/AP fecha após 10 minutos. Sem botão e sem primeira
  configuração, falha de Wi-Fi não abre um AP automaticamente.
- Configure no tablet a URL e o token. A origem permitida é https://bjsports.com.br.
  Para outra origem, altere allowed_origin e recompile; não use curinga.
- Senha Wi-Fi em branco preserva a atual; redes abertas não são configuradas pelo painel.
- Credenciais perdidas: recuperação física via USB; não existe senha universal.

## Protocolo

1. GET /status com Authorization: Bearer TOKEN.
2. Use boot_id e uptime_ms recebidos. Crie ID único (UUID), validade uptime_ms+5000
   módulo 2^32. POST /liberar sem corpo, com o mesmo Authorization e cabeçalhos:
   X-Command-ID, X-Boot-ID e X-Expires-Ms.
3. Aceite somente success=true, state=command_accepted e command_id correspondente.
   Isso confirma comando de pulso, não passagem física. Sensor não implementado.
4. Requisição sem token: 401. Origem não permitida: 403. Comando inválido/expirado:
   400. Ocupado/repetido: 409. Métodos não cadastrados: 404. OPTIONS nunca aciona.
5. São retidos até 64 IDs de comandos ainda válidos (máximo 10 segundos). Reinício
   muda boot_id. Se a resposta se perder, confira fisicamente; não tente de novo
   automaticamente. Um novo ID é um novo comando.

O protocolo usa HTTP local e segredo compartilhado. Não protege contra interceptação
na própria rede. Use rede isolada de dispositivos e tablet controlado. Em navegador,
o site HTTPS pode bloquear fetch para HTTP local (mixed content/permissões de rede).
CORS não resolve esse bloqueio: a instalação precisa de ponte local com TLS confiável
ou aplicativo nativo com transporte local autorizado. Não desabilite segurança do
navegador. A seleção/instalação dessa ponte depende do equipamento real e está pendente.
As regras financeiras/biometria do backend não foram reescritas nesta etapa: autenticar
um dispositivo não substitui validar o aluno e a autorização no servidor.

## OTA e limites

OTA exige senha admin, CSRF, manutenção física aberta e relé ocioso. Upload abortado
cancela a gravação; reinício automático só depois de sucesso. O binário não tem
assinatura criptográfica imposta: antes de produção, definir chaves, suporte da placa,
partições e estratégia de rollback e testar cortes de energia. Digest não cifra HTTP.
O manifesto de distribuição identifica integridade/versão; não é assinatura.

O desligamento usa tarefa esp_timer, independente do HTTP; não é garantia elétrica
contra falha total da CPU ou alimentação. Prever estado desligado no boot/reset por
circuito externo, módulo compatível com lógica 3,3 V e proteção da carga indutiva.
Não conectar uma solenóide diretamente ao GPIO. Dimensionamento depende do conjunto.

Contador: gravação a cada 60 segundos, apenas ocioso; falta de energia pode perder
comandos ainda não persistidos, e fluxo contínuo pode adiar a gravação. NVS não é
trilha de auditoria. O valor legado é preservado, sem reinterpretar como presença.

## Checklist de bancada (pendente)

- Medir relé desligado no boot, reset e queda de alimentação.
- Medir 300/1000/3000 ms sob HTTP lento e tráfego repetido.
- Verificar 401 sem token, 403 origem inválida e OPTIONS sem pulso.
- Verificar busy, replay, comando expirado, boot antigo e Wi-Fi ausente.
- Confirmar AP restrito, fechamento em 10 min e reconexão após queda de roteador.
- Testar OTA válida, arquivo inválido, upload interrompido e recuperação via USB.
- Testar tablet físico e diferenciar autorização, pulso e passagem.
- Validar saída de emergência conforme o mecanismo instalado.

Nenhuma publicação no site ou gravação em placa faz parte da aplicação local.

## Validação local realizada em 12/09/2026

- Compilação PlatformIO esp32dev aprovada: RAM 49.128 bytes (15,0%);
  aplicação 834.597 bytes (63,7% da partição).
- Testes C++ de Bearer ausente/inválido/exato, token legado, limites do pulso,
  números inválidos/overflow, validade inclusive rollover e formato do ID: aprovados.
- Node: sintaxe de todos os scripts do kiosk e sete cenários de comunicação
  (sucesso, credencial recusada, comando recusado, ID divergente, rede indisponível,
  configuração ausente e dispositivo ocupado): aprovados.
- Dois testes Python do catálogo: ZIP completo; bloqueio por manifesto ausente,
  binário corrompido e fonte divergente: aprovados.
- Flask com SQLite somente em memória: /esp, ZIP, metadados, header de fonte,
  bloqueio do binário não publicado e de nome não permitido: aprovados.
- git diff --check e compilação Python: aprovados. Suíte geral não executada.
- Não houve teste elétrico, validação visual autenticada, deploy ou gravação em ESP32.
- Backup dos quatro arquivos originais em /tmp/bjsports-firmware-backup nesta sessão;
  para rollback local duradouro use a revisão Git anterior e preserve outros trabalhos.

Repetir testes de software a partir da raiz do repositório:

    c++ -std=c++11 tests/firmware/access_policy_test.cpp -o /tmp/bj-policy-test
    /tmp/bj-policy-test
    node tests/firmware/kiosk_protocol_test.cjs
    venv/bin/python -m unittest discover -s tests -p 'test_firmware_catalog.py' -v

A compilação desta sessão usou PlatformIO e Zig em /tmp, sem instalar ferramentas
no venv da aplicação. O binário local está em firmware/.pio/build/esp32dev/firmware.bin;
não foi promovido ao catálogo público. Fonte/binário anteriores continuam no site.
