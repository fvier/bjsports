**Entrega A — Turmas e planos**

13/09/2026 • Relato da implementação local. **Atualização: publicada e conferida posteriormente no mesmo dia, inclusive com navegação autenticada, conforme o [relatório de execução](../execucao-2026-09-13/README.md).** Os resultados e a divergência descritos abaixo registram a situação anterior à publicação.

A publicação e o backup vigentes foram atualizados novamente na etapa 7/12, conforme o [relatório das faixas etárias e correção da publicação](../faixas-etarias-2026-09-13/README.md).

A administração de turmas e planos foi reunida em `/gestao_turmas.html`. A página e o único item de menu usam o nome **Turmas e planos**. As abas principais são Turmas e Planos; a aba Planos organiza Individuais e Combos e especiais. Filiais e Ícones continuam acessíveis.

**Comportamento entregue**

- A aba principal é renderizada pelo servidor; consultar Planos não carrega a tabela/modal de turmas. A categoria do catálogo permanece selecionada ao salvar, recarregar ou abrir um favorito antigo.
- Os endereços `/planos_admin` e `/planos_admin.html` aceitam consulta GET e redirecionam para a aba Planos. Envios POST antigos não são reexecutados. A tela independente foi removida.
- Formulários de planos usam ações próprias (`plan_create`, `plan_update`, `plan_delete`). A rota mantém a autorização existente de instrutor e CSRF; misturar uma ação de turma com o destino de planos é recusado.
- Formulários de criação/edição preservam modalidades, frequências, preços, descontos, benefícios e comportamento comercial existente. A navegação por si só não altera contas, preços ou relações.
- A tela informa que editar nome/preço de um plano também pode atualizar o plano registrado nas contas vinculadas. A política comercial existente foi preservada; nenhum reajuste de alunos reais foi executado.
- Erros de validação de planos reapresentam a escolha digitada no mesmo POST, sem guardar os dados no cookie. Falha de persistência ao criar/editar desfaz a transação e reapresenta o formulário com mensagem clara.
- Os seletores e a validação de modalidades da gestão utilizam a mesma referência no servidor. A integração dessa referência com o novo cadastro é uma próxima etapa.
- Em celular, planos são apresentados como linhas em formato de cartões com campos identificados e ações de toque. Temas claro/escuro, foco e navegação por teclado foram conferidos. O cálculo visual de ocupação tolera capacidade zero.

**Arquivos e escopo**

- `app.py`: redirecionamento, tratamento de planos integrado à gestão, renderização compartilhada, preservação em erros e referência de modalidades da gestão.
- `templates/gestao_turmas.html`, `templates/_plan_catalog.html`: página única e catálogo incorporado.
- `templates/_erp_sidebar.html`, `templates/locais_admin.html`, `templates/gestao_icones.html`: navegação atualizada.
- `templates/base.html`: estilos da gestão carregados apenas nessa rota.
- `static/js/plan_catalog.js`, `static/css/turmas_planos.css`: categorias, recuperação de formulário, apresentação móvel e contraste.
- `templates/planos_admin.html`: removido; seus controles foram incorporados ao parcial.
- `tests/test_app.py`, `tests/ui/management_plans.py`: testes atualizados e novos casos de integridade, permissão, redirecionamento e navegador.

A entrega A não exige alteração de esquema. Cadastro, regras de créditos, contratos e check-in existentes foram mantidos no código local. A escolha de turmas pelo aluno ainda não foi implementada. As faixas etárias foram solicitadas para a próxima etapa.

**Validação realizada**

- 98 testes aprovados em SQLite em memória, em 48,296 segundos. Incluem cadastro, contrato, créditos, check-in, gestão e os novos testes de permissões, separação das ações e integridade.
- Falha de gravação simulada: catálogo e planos das contas vinculadas preservados após rollback; resposta com erro compreensível, sem sucesso falso.
- Navegador Chrome: 28 verificações, abrangendo 360, 390, 768 e 1440 px e temas claro/escuro; nenhuma rolagem horizontal da página ou erro de JavaScript nessas verificações.
- Em 390 e 1440 px: criação de plano, erro com campos preservados, correção, edição, persistência do valor, exclusão e redirecionamento de favoritos aprovados em banco descartável.
- Categoria de planos acionada por teclado e conservada após recarga; foco vai para a criação e para a mensagem de erro conforme a ação.
- Conferência visual adicional dos horários e botões após ajustes finais de contraste.
- Verificação de sintaxe JavaScript, compilação Python e espaços do diff aprovadas.

Os testes de navegador usam somente contas técnicas no servidor local e criam/excluem planos técnicos. Não são ensaios em aparelhos físicos. A suíte desta entrega não foi executada em PostgreSQL nem foram enviados formulários em produção. Resultados de publicações anteriores continuam documentados separadamente.

Para reproduzir o teste de interface, preparar um servidor em loopback com banco descartável e uma conta de instrutor. Executar `tests/ui/management_plans.py` em ambiente com Playwright/Chrome usando `BJ_UI_BASE_URL`, `BJ_UI_TEST_USERNAME`, `BJ_UI_TEST_PASSWORD` e, opcionalmente, `BJ_UI_OUTPUT` e `BJ_UI_CHROME`. O teste recusa destinos fora de localhost/127.0.0.1.

**Divergência encontrada na VPS**

A consulta somente leitura ao host e ao contêiner `bjsports-app` confirmou divergência entre a base local anterior a esta implementação e dois arquivos ativos: `app.py` e `templates/_erp_sidebar.html`. Os outros cinco arquivos comparados coincidem com a base local. As definições de `Plan`, `ClassGroup`, `planos_admin`, `gestao_turmas` e `role_required` coincidem.

No arquivo `app.py` lido do contêiner, não existem `contract_due_at` nem a função da rota `/catracadoc` presentes no código local. Na consulta pública, `/catracadoc` respondeu 404; `/login?mode=register` respondeu 200 e ainda apresenta o texto das 60 horas. Essa combinação exige reconciliar fonte, templates e comportamento antes de publicar. A causa da divergência não foi determinada; não presumimos quem alterou ou reverteu a versão.

Os relatórios de 12/09 registram uma publicação anterior com essas correções. Eles permanecem como histórico, mas não comprovam a situação atual do contêiner. Nenhum código ou dado da VPS foi alterado nesta entrega. As correções locais anteriores foram preservadas.

**Preparação da próxima publicação**

1. Definir o conjunto de arquivos e correções de base que deverá compor a versão publicada, conciliando a divergência detectada. O arquivo local `app.py` inclui correções anteriores ausentes no contêiner e não pode ser tratado como uma alteração exclusivamente visual.
2. Ensaiar o pacote consolidado em PostgreSQL isolado, incluindo as migrações eventualmente necessárias às correções de base. A entrega A, isoladamente, não acrescenta colunas ou tabelas.
3. Criar backup atualizado de fonte, imagem e dados; conferir integridade, restauração e reversão conforme E10.
4. Apresentar o pacote concreto para autorização da publicação e conferir os fluxos após ativação.

Base de trabalho e logs privados desta sessão: `/tmp/bj-management-20260913`. A cópia dos arquivos anteriores é proteção local de trabalho e não substitui backup da VPS. Evidências sanitizadas e manifesto estão nesta pasta de documentação.

- [Prévia móvel da aba Planos](preview-mobile-planos.png).
- [Prévia móvel da edição](preview-mobile-edicao.png).
- [Verificações de navegador](browser-results.json) e [conferência visual final](visual-results.json).
- [Manifesto das alterações](change-manifest.json), [comparação da base](baseline-comparison.json) e [consulta pública da base](public-baseline-check.json).

O acompanhamento das etapas e decisões está no [plano consolidado](../plano-acao-consolidado-2026-09-13.md).
