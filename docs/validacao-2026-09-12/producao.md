# Publicação e validação em produção — 12/09/2026

## Resultado

Versão publicada em https://bjsports.com.br em 12/09/2026, por volta de 15h45
(America/Recife), com autorização expressa do usuário. A documentação está em
https://bjsports.com.br/catracadoc e a Central ESP32 em https://bjsports.com.br/esp.

Somente o serviço bjsports-app foi recriado. O PostgreSQL bjsports-db permaneceu
ativo. Os 17 arquivos do pacote final conferem por SHA-256 no contêiner público.
O código anterior da VPS coincidia com o HEAD local 6088ce6 nos arquivos alterados.
Não havia uploads ou outros arquivos da aplicação modificados na camada gravável
do contêiner anterior; os arquivos existentes foram preservados na imagem base.

## Backup e restauração comprovada

Diretório privado na VPS: /data/bjsports/backups/20260912-registration-release.

- source-before.tar.gz: fonte anterior, incluindo arquivos e uploads existentes;
  exclui a própria pasta de backups e o diretório Git.
- instance-before.tar.gz: volume persistente da aplicação.
- image-before.tar.gz e previous-image-id: imagem anterior e identificação.
- database-before.dump: primeiro backup PostgreSQL em formato custom.
- globals-before.sql: definições globais privadas do PostgreSQL.
- database-final-before-activation.dump: último backup consistente, obtido com
  o aplicativo parado imediatamente antes da ativação bem-sucedida.
- SHA256SUMS e SHA256SUMS-final: integridade dos artefatos.
- rollback.sh: restaura apenas os arquivos do pacote e a imagem anterior;
  não restaura nem apaga o banco.

Os dois backups PostgreSQL foram restaurados em bancos descartáveis de um
PostgreSQL 16 separado, em rede Docker interna, sem portas públicas.
O último backup restaurado reproduziu os registros das 21 tabelas do snapshot
anterior à ativação, comparados por hashes de todas as colunas existentes.
Os backups contêm dados privados e não devem ser servidos pelo site ou enviados ao Git.

## Migração

- 21 contas reais auditadas, sem colisões de CPF ou formatos incompatíveis.
- Índice uq_user_cpf_normalized criado sem reescrever CPFs legados.
- Coluna contract_due_at adicionada como timestamp nullable.
- Duas inicializações consecutivas no clone preservaram todos os registros.
- Migração em produção preservou todas as colunas e registros existentes das
  21 tabelas, conferidos novamente após a remoção dos testes públicos.
- Nenhuma das 21 contas antigas recebeu prazo; nenhum aceite em massa foi criado.
- Novos cadastros recebem 60 horas desde a criação. O histórico de aceite nasce
  vazio; somente confirmação explícita após login registra o aceite.

## Testes

- Suíte completa em PostgreSQL descartável: 93/93 aprovados em 105,739 segundos.
- A primeira execução teve uma falha no preparo de um teste legado, que usava
  DATETIME do SQLite. O teste passou a usar TIMESTAMP/SERIAL no PostgreSQL.
  A suíte completa foi repetida em banco limpo e passou. Os 13 testes de créditos
  também foram repetidos no SQLite e passaram.
- Chrome com 1440×900 e 390×900, primeiro no clone PostgreSQL e depois no HTTPS
  público: cadastro adulto, 67 DDDs, DDD 99, CPF normalizado, prazo de 60 horas,
  ausência de aceite automático, rejeição de POST sem confirmação explícita,
  aceite consistente entre conta/histórico, saída, login por e-mail e CPF pontuado.
- Cadastro de menor no celular: DDD 11, responsável persistido sem consentimento,
  opção de aceite adulto indisponível e confirmação explícita do responsável.
- Check-in nos dois tamanhos: aluno envia ocorrência específica, monitor confirma
  e instrutor recusa com confirmação visível; quatro ocorrências conferidas no banco.
- Ajuste descoberto no ensaio: nomes maiores de turma provocavam rolagem horizontal
  no celular. A largura do seletor e da área principal foi corrigida e revalidada.
- Documentação e formulários sem rolagem horizontal nos tamanhos testados.
- Regras de prazo vencido, duplicidade, turma inativa, dia incorreto, matrícula,
  modalidade e capacidade: cobertas pela suíte PostgreSQL. Não foram alteradas
  datas ou condições de alunos reais para simular esses casos no site público.
- /login, /catracadoc e /esp: HTTPS 200; pacote ZIP contém os quatro arquivos do
  projeto de firmware. Catálogo informa v2.2.0 e binary_available=false.

Seis contas técnicas @example.test e uma turma técnica fora da grade pública foram
usadas na validação publicada. Foram removidas ao final, juntamente com quatro
presenças, três aceites e uma matrícula de teste. Nenhum pagamento foi criado.
A comparação final confirmou os registros originais idênticos ao snapshot anterior.
As sequências de IDs avançaram normalmente durante os testes; não foram reduzidas.

## Ocorrência durante a ativação

A primeira tentativa parou antes da troca de código porque o processo isolado de
migração não recebeu SECRET_KEY. O aplicativo anterior foi reativado; nessa
etapa somente o índice aditivo de CPF havia sido aplicado. Corrigida a passagem
privada da configuração e o tratamento de falhas, a ativação foi repetida com
sucesso. As chaves não foram incluídas no pacote de publicação nem neste relatório.

## Operação e reversão

A imagem anterior está preservada como bjsports-rollback:20260912-registration.
Em necessidade de reversão de código, executar na VPS o rollback.sh privado e
conferir os fluxos antes de reabrir cadastros. A coluna nullable e o índice de CPF
são aditivos. Não restaurar o banco automaticamente, pois isso poderia eliminar
novos registros posteriores à publicação.

Os contêineres, bancos e rede de ensaio são descartáveis. Os backups, relatórios
sanitizados e o procedimento de reversão permanecem preservados na VPS.
As capturas autenticadas ficam somente na área privada local
/tmp/bj-prod-20260912, pois podem conter informações da interface administrativa.

## Limite que permanece

Não houve gravação nem ensaio de hardware ESP32. Botão GPIO27, relé, acionamento
real a partir do tablet e OTA físico continuam pendentes de bancada, conforme
informado na documentação pública. Não há binário liberado para download.
