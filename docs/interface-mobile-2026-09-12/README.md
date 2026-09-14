# Revisão da interface para celulares — 12/09/2026

## Escopo e situação

Alterações publicadas na VPS com autorização expressa do usuário. Conferência
final no site público concluída em 13/09/2026. A imagem anterior está preservada
para reversão.
Nenhuma regra de cadastro, contrato, cobrança, permissões ou check-in foi alterada.

A análise cobriu início, login, cadastro, catálogo de turmas, resumo, presenças,
calendário, perfil, contrato, mensalidades e gestão de turmas. Foram examinadas
68 combinações de página, perfil e largura: 360, 390, 768 e 1440 pixels, com
perfis de aluno e instrutor em banco descartável.

## Problemas encontrados e ajustes

- Menu lateral ocupava espaço antes do conteúdo no celular: a área principal
  começava em cerca de 681 px na medição inicial. Agora começa em 64 px nas
  seis telas de aluno avaliadas, com menu em painel aberto pelo botão do cabeçalho.
- Menu móvel recebe foco ao abrir, contém a navegação por Tab/Shift+Tab, fecha
  por botão, fundo ou Escape e devolve o foco. Conteúdo de fundo fica inerte.
  No desktop, expandir/recolher depende do botão e conserva a preferência.
- A página inicial ultrapassava a largura disponível. A decoração e o cabeçalho
  da grade foram dimensionados corretamente; os horários viram cartões no celular.
  A tabela continua disponível no desktop e mantém seus cabeçalhos semânticos.
- Calendário semanal passa a lista de dias no celular e duas colunas no tablet,
  mantendo eventos e horários livres. Desktop mantém as sete colunas.
- Login/cadastro ganham controles de 48 px, textos auxiliares maiores, menos
  apresentação antes do formulário e seções “Seus dados”, “Seu treino” e
  “Acesso à conta”. Autocomplete foi ajustado para nome, usuário e novas senhas.
- Check-in ganha ação principal de largura completa; histórico aceita quebra
  de linha. Barra inferior respeita a área segura do aparelho.
- Temas claro/escuro preservados; contraste de frequência/graduação corrigido
  no tema claro. Preferência de movimento reduzido respeitada.

## Arquivos da revisão

- static/css/interface.css: composição a partir do celular, com ampliação em
  600/992 px, carregada depois do CSS existente e somente para tela.
- static/js/main.js: menus e foco, indicação de página atual e rótulos dos
  cartões da grade pública.
- templates/base.html: carregamento dos estilos, fundo do menu e versão dos assets.
- templates/_erp_sidebar.html: fechamento do painel e nomes acessíveis.
- templates/login.html: seções e autocomplete, preservando campos e fluxo.
- tests/ui/mobile_navigation.py: teste reproduzível de teclado, fundo e resize.

## Validação

- 68 combinações finais sem rolagem horizontal da página; páginas responderam 200.
- Chrome: cadastro adulto, DDDs, aceite explícito e login por e-mail aprovados em
  desktop e celular, sem erros de JavaScript.
- Cadastro de menor no celular: responsável persistido sem aceite automático e
  confirmação explícita aprovados.
- Check-in: quatro ocorrências enviadas pelo aluno, confirmação do monitor e
  recusa do instrutor aprovadas, com resultado conferido no banco descartável.
- Menus público/portal em 320, 390 e 768 px: teclado, fechamento por fundo,
  Escape, mudança para desktop e retorno ao tamanho original.
- Seis páginas adicionais verificadas no tema claro, com movimento reduzido.
- Suíte existente: 93 testes aprovados (54,489 s); JavaScript e diff sem erros.

Os tamanhos móveis foram emulados no Chrome. Não se trata de teste em aparelhos
físicos iOS/Android. A conferência publicada está registrada na seção final.
As capturas usam dados de teste, sem alterações em alunos reais.

## Prévia e publicação

Veja preview-mobile-dashboard.png e preview-mobile-registration.png nesta pasta.
O pacote local /tmp/bj-mobile-20260912/release-mobile.tar.gz contém somente os cinco
arquivos de execução desta revisão; release-mobile.json registra seus hashes.

Publicação concluída em /data/bjsports, recriando somente bjsports-app. O banco
bjsports-db permaneceu ativo. Esta revisão não exige migração de banco.

Para repetir o teste de navegação, inicie a aplicação em loopback com banco
local descartável, instale Playwright no ambiente de teste e execute
`tests/ui/mobile_navigation.py` com BJ_UI_BASE_URL, BJ_UI_TEST_USERNAME e
BJ_UI_TEST_PASSWORD no ambiente. BJ_UI_OUTPUT define a pasta das evidências e
BJ_UI_CHROME permite escolher o executável do Chrome. Não use contas reais.

## Conferência da versão publicada

- Cinco arquivos ativos conferidos por SHA-256; CSS e JavaScript públicos também
  conferem com o pacote local.
- 44 páginas verificadas em HTTPS, em 390 e 1440 px, incluindo início, entrada,
  formulário de cadastro, turmas e telas autenticadas de aluno, monitor e instrutor.
- Nenhuma rolagem horizontal ou erro de JavaScript nessas verificações.
- Menus móveis: abertura, foco, Escape e retorno ao botão aprovados.
- Nesta etapa publicada, as páginas foram consultadas sem enviar cadastros,
  aceites, pagamentos ou check-ins. Os fluxos de envio foram validados localmente
  conforme descrito acima.
- Três contas técnicas, uma turma não pública e uma matrícula técnica foram
  criadas para a conferência autenticada. Foram removidas ao final por IDs e
  identificadores exatos; sua ausência foi confirmada.
- Backup privado em /data/bjsports/backups/20260912-mobile-layout: arquivos
  anteriores, imagem, volume persistente e dump PostgreSQL. SHA-256 aprovado para
  os quatro artefatos; lista do dump conferida. Este novo dump de precaução não
  passou por ensaio adicional de restauração nesta publicação de layout.
- rollback.sh preservado no mesmo diretório; restaura os arquivos e a imagem
  anteriores, sem restaurar o banco.

A checagem ampla por hashes de todas as tabelas foi bloqueada pela revisão
automática por exceder o escopo de interface e foi dispensada. A conferência
final se limitou ao layout e aos registros técnicos explicitamente identificados.

Evidências sanitizadas: published-layout-results.json e published-cleanup.json.
