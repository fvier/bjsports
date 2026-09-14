# Resultado da validação — 12/09/2026

**Atualização:** publicação autorizada e concluída. Backup restaurado, migração e
93 testes aprovados em PostgreSQL, navegador autenticado validado no site público
e dados técnicos removidos. Veja o [relatório de produção](producao.md).

O restante deste documento registra a etapa local anterior à publicação.

## Implementação

A rota /catracadoc está preparada localmente, com os procedimentos e avisos de
validação física pendente. Cadastro, DDD, CPF, responsável, login por e-mail e
check-in por ocorrência foram corrigidos. O contrato será aceito após entrar,
com 60 horas apenas para novos cadastros. Contas antigas pendentes ficam intactas,
sem novo prazo nem bloqueio; nenhuma solicitação de aceite em massa foi criada.

## Testes e evidências

- Suíte anterior: 80 testes, 7 falhas.
- Suíte após implementação: **93 testes, todos aprovados** (45,792 s).
- Chrome em desktop 1440×900 e celular 390×900: cadastro adulto completo, 67 DDDs,
  dados de menor exibidos/validados, aceite explícito e login por e-mail aprovados.
- Cadastro de menor completo no Chrome móvel: responsável persistido sem aceite,
  opção de adulto bloqueada e confirmação explícita do responsável aprovados.
- Chrome nos dois tamanhos: check-in de aluno, confirmação por monitor e recusa
  por instrutor com confirmação visível aprovados; zero erros de JavaScript.
- Sem rolagem horizontal na documentação e no formulário. DDD usa uma única seta
  nativa e não recorta o código; apresentação móvel reduzida antes do formulário.
- Cópia SQLite: 31 contas, nenhuma colisão de CPF nem formato não suportado.
- Índice normalizado e migração da coluna nullable ensaiados nessa cópia.
  Comparação de todas as colunas legadas de todas as tabelas: registros preservados.
  Nenhuma conta antiga recebeu contract_due_at. PRAGMA integrity_check aprovado.
- Python compilado, JavaScript verificado e git diff --check sem erros.

Arquivos da sessão (ambiente local, fora do pacote público):

- /tmp/bj-suite-passed.log — suíte completa.
- /tmp/bj-browser-results.json — cadastro/aceite/login nos dois tamanhos.
- /tmp/bj-checkin-browser-results.json — confirmação/recusa por perfil.
- /tmp/bj-register-desktop.png e /tmp/bj-register-mobile.png — telas revisadas.
- /tmp/bj-prepublish-20260912 — backup privado e ensaio de migração.

## Limites da validação

Os navegadores usaram um banco isolado em /tmp, com dados sintéticos. Isso não
constitui validação de produção. O PostgreSQL da VPS, o navegador autenticado da
versão publicada e o botão/relé físicos não foram testados nesta etapa.

Na conclusão da etapa local, a publicação e o backup PostgreSQL/VPS ainda estavam
pendentes. Essas etapas foram concluídas conforme o relatório de produção acima.
O [plano de publicação e reversão](plano-publicacao.md) descreve a sequência.
