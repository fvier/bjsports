# Cadastro, check-in e documentação — plano de publicação

**Executado em 12/09/2026, com autorização expressa.**
Veja o [resultado da publicação e da validação](producao.md).
As seções abaixo preservam o plano e o estado anterior para referência.

## Escopo autorizado e decisões

- Página pública /catracadoc: instalação, botão GPIO27, janela de 10 minutos,
  pulso, tablet, OTA, recuperação e checklist de bancada. Link na Central ESP32
  e na página de integração. O hardware está explicitamente pendente de validação.
- Cadastro: 67 DDDs válidos, seletor legível, CPF canônico, bloqueio de duplicidade,
  responsável identificado pela idade, login também por e-mail, apresentação móvel reduzida.
  Fonte dos códigos: [Anatel](https://www.gov.br/anatel/pt-br/regulado/numeracao/codigos-nacionais).
- Aceite somente após entrar. Nova conta começa pendente e recebe contract_due_at
  de 60 horas desde o cadastro. Sem confirmação explícita, não há ContractAcceptance.
  Após o prazo, aluno acessa contrato, saída e troca obrigatória de senha;
  demais funções do portal são bloqueadas. Login e pagamento não prorrogam prazo.
- Conforme decisão do usuário: contas antigas pendentes não recebem prazo, bloqueio
  nem pedido em massa. contract_due_at permanece NULL. O contrato mantém a versão
  2026-09-11.1; uma atualização de texto e aceite em massa será feita em outra etapa.
  O texto atual ainda contém referências ao aceite no cadastro. Um aviso operacional
  explícito explica o fluxo novo; o texto contratual original foi preservado.
- Check-in fora de créditos: turma/ocorrência do dia, matrícula/modalidade, capacidade,
  reserva da vaga e ausência de duplicidade. Cada ocorrência é um registro distinto.
  Conta sem matrícula pode usar o fluxo experimental durante o período já existente,
  com indicação explícita. Não inventa matrícula, modalidade ou presença.
- Monitor confirma e instrutor pode confirmar/recusar. Papel é conferido no banco.
- Ajuste adicional da suíte: botão Faturas do monitor aponta para sua área financeira,
  em coerência com as permissões existentes. Testes de reservas agora enviam o
  consentimento de risco explícito que a API já exigia.

## Situação antes da publicação

Implementação local. Nenhum deploy ou alteração da base de produção realizado.
A página /catracadoc respondeu 404 na consulta pública antes desta mudança.
Os procedimentos documentados não comprovam firmware instalado nem botão físico.

Backup local em /tmp/bj-prepublish-20260912:

- bjsports-before.db: snapshot consistente via API sqlite3.backup.
- source-head.tar: fonte da revisão Git anterior às alterações locais deste conjunto.
- sha256.json: integridade dos artefatos de backup.
- migration-test.db: cópia descartável para ensaio; não usar como backup original.
- data-before.json: referência privada dos registros para a comparação da migração.

Diretório privado (modo 700), fora do Git. O backup local não substitui o backup
PostgreSQL/VPS e não deve ser publicado. Os uploads existentes permanecem intactos.

## Migração e proteção de dados

1. Parar entrada de novos cadastros/check-ins durante a janela de publicação.
2. Criar backup do PostgreSQL, imagem/source anteriores e uploads na VPS; validar
   pg_restore --list e testar restauração em banco isolado antes da troca.
3. Executar scripts/audit_registration_data.py com DATABASE_URL do destino no
   ambiente, sem colocar credenciais na linha de comando. O script não importa app.py.
4. Se houver colisões de CPF ou formato não suportado, parar. O relatório mostra
   somente IDs; não mesclar nem apagar contas automaticamente.
5. Com auditoria limpa, executar o mesmo script com --apply-index. Ele cria índice
   único por CPF sem pontuação. Não reescreve registros legados.
6. Publicar os arquivos completos, incluindo registration_rules.py e firmware_catalog.py.
   Na importação, a migração existente adicionará contract_due_at nullable. Não há
   preenchimento retroativo. O PostgreSQL utiliza a trava de migração já existente.
7. Reiniciar somente o serviço da aplicação, mantendo o banco ativo. Verificar logs
   sem expor credenciais e validar as rotas públicas e autenticadas.

Não executar import app apontando para a produção como simples teste: o módulo
possui rotinas legadas de migração/inicialização na importação.

## Reversão

- Antes do deploy, registrar ID da imagem anterior e revisão/hash dos arquivos,
  além do instante do backup. Não sobrescrever esse registro a cada tentativa.
- Em falha de aplicação, reativar a imagem/source anteriores com o banco preservado.
  A coluna nullable e o índice são aditivos. Conferir compatibilidade com o fonte
  anterior e manter a janela de manutenção até a avaliação.
- A versão anterior tinha cadastro/aceite inconsistentes: não reabrir cadastros
  automaticamente numa reversão. Decidir entre hotfix e rollback com a equipe.
- Restaurar banco somente se necessário e após avaliar novos registros posteriores
  ao backup. Não apagar presenças, pagamentos ou novas contas para reverter código.
- Depois da reversão, validar login, perfis, cadastros e integridade novamente.

## Checklist da versão publicada (após autorização)

- /catracadoc e /esp acessíveis; links e status de bancada corretos.
- Cadastro adulto e menor, DDD diferente de 83, CPF pontuado/não pontuado,
  tentativa duplicada, responsável válido e inválido.
- Conta nova com contrato pendente e deadline; nenhuma linha de aceite automática.
- Contas antigas preservadas, sem novo deadline. Contrato explícito atualiza conta
  e histórico juntos; envio repetido não duplica histórico.
- Prazo de 60 horas e bloqueio em ambiente de teste da versão publicada (sem alterar
  datas de alunos reais), login por e-mail/CPF/usuário e saída.
- Check-in em desktop/celular, turma inativa, dia incorreto, sem matrícula,
  lotação, modalidades, duas ocorrências, confirmação de monitor e recusa de instrutor.
- Rotas e banco de produção não serão considerados validados apenas por HTTP 200.

Autorização específica recebida e publicação concluída em 12/09/2026; ver relatório vinculado acima.
