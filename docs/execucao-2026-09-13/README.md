# Primeira publicação do plano acompanhado

13/09/2026. **Etapas 1–6/12 concluídas, incluindo conferência autenticada em produção e limpeza dos testes.** Acompanhar no [plano de execução](../plano-execucao-2026-09-13.md).

**Atualização posterior, 13/09 às 22h36:** uma nova divergência entre backend e templates foi corrigida durante 7/12. O pacote atual inclui idades opcionais e foi novamente conferido em produção. A pasta de backup citada neste relato foi encontrada incompleta; a referência vigente é `/data/bjsports/backups/20260913-age-rehearsal`. Consultar o [relatório atual](../faixas-etarias-2026-09-13/README.md). Os números e resultados abaixo são históricos da primeira publicação.

A consulta dos horários no cadastro foi publicada depois, às 23h13, com novo backup e conferência: [relatório vigente de 8/12](../cadastro-horarios-2026-09-13/README.md).

## Entrega publicada

A página administrativa é **Turmas e planos**, com abas Turmas/Planos e categorias Individuais/Combos e especiais. A tela antiga foi retirada; seus endereços GET redirecionam depois da autenticação. O pacote também restabelece as correções de cadastro, CPF/DDD, responsável, contrato após entrar, check-in por turma, interface móvel e documentação da catraca que estavam ausentes em partes do código publicado.

Foram publicados 26 arquivos e removido `templates/planos_admin.html`, conforme o [manifesto](manifesto-primeira-entrega.json). Configurações e uploads da VPS foram preservados. Somente `bjsports-app` foi recriado, às 19h23 UTC (16h23 em America/Recife). O banco PostgreSQL continuou ativo.

## Validação e limites

- SQLite: 98 testes aprovados em 43,779 s.
- PostgreSQL descartável: 98 testes aprovados em 109,680 s. A configuração da suíte recusa o nome/host do banco de produção.
- Clone real: duas inicializações do pacote preservaram os registros das 21 tabelas.
- Chrome com banco sintético: 7 fluxos de cadastro adulto/menor, responsável, prazo de 60 horas, ausência de aceite automático, confirmação explícita consistente, login por CPF/e-mail e check-in confirmado/negado por monitor/instrutor.
- Gestão em banco sintético: 28 verificações em 360, 390, 768 e 1440 px, nos temas claro/escuro, incluindo criar/editar/excluir, tratamento de erros, teclado e redirecionamento.
- Produção: 27 itens conferidos por SHA-256 no contêiner ativo. Dez verificações de páginas públicas em 390/1440 px, sem erros JavaScript ou rolagem horizontal. `/catracadoc` voltou a responder 200.
- Conferência autenticada após autorização específica: 7 fluxos de cadastro adulto/menor, contrato, login e check-in aprovados no HTTPS público; 12 verificações da gestão em claro/escuro e 44 de navegação nos perfis aluno, monitor e instrutor em 390/1440 px. A edição de planos foi testada no banco sintético; na produção, a gestão foi conferida sem alterar o catálogo.
- Comparação após os testes e a limpeza: registros anteriores das 21 tabelas preservados; 21 contas existentes, nenhum prazo aplicado a contas antigas e nenhuma conta técnica restante.

Os testes de navegador representam emulação no Chrome, não ensaio físico Android/iOS. A criação de registros técnicos em produção foi inicialmente rejeitada pela revisão automática; o usuário respondeu “continue” à solicitação específica e os testes foram executados. A primeira rodada criou e removeu 6 usuários, 1 turma não publicada, 1 matrícula, 4 presenças e 3 aceites. Um erro transitório de rede interrompeu a leitura da gestão. Somente os 3 perfis técnicos foram recriados para repetir as leituras; foram removidos ao final, sem novos aceites ou presenças. A comparação utiliza um novo snapshot obtido imediatamente antes dos testes.

A revisão automática também recusou um túnel para o clone de dados reais. A alternativa utilizada foi um banco novo, com dados exclusivamente técnicos; o clone real permaneceu privado. O teste inicial de banco vazio encontrou disputa entre workers na criação da conta padrão: a preparação passou a inicializar o banco uma vez antes do Gunicorn, como já previsto na publicação. Essa preparação não alterou contas reais.

## Backup e recuperação

Pasta privada: `/data/bjsports/backups/20260913-turmas-planos`.

- Fonte completa anterior, imagem anterior, volume persistente, dump PostgreSQL custom e definições globais guardados com checksums.
- Fonte: 24 arquivos anteriores do pacote restaurados em diretório isolado e conferidos por hash.
- Volume: 3 arquivos restaurados em diretório privado de ensaio.
- Imagem anterior recuperada do arquivo de backup na tag `bjsports-rollback:20260913-turmas-planos`.
- Banco inicial e dump final, obtido com a aplicação parada antes da troca, restaurados em bancos isolados. O dump final reproduziu os registros das 21 tabelas do snapshot anterior à ativação.
- `rollback.sh` restaura arquivos do pacote e a imagem anterior; não restaura automaticamente o banco nem apaga registros criados depois da publicação. Recusa sobrescrever arquivos que tenham sido alterados fora do pacote.

Dados privados, credenciais e capturas autenticadas ficam fora deste relatório. Os artefatos operacionais e logs privados estão em `/tmp/bj-execution-20260913` e na pasta privada do backup.

Os dois contêineres de ensaio, seus volumes anônimos e as redes temporárias foram removidos após a validação. Backups foram preservados. A conferência final confirmou aplicação e PostgreSQL de produção ativos e `/catracadoc` em HTTPS 200.

## Evidências sanitizadas

- [Resultados dos testes](validacao-primeira-entrega.json), [fluxos no banco sintético](navegador-fluxos-ensaio.json) e [gestão no banco sintético](navegador-gestao-ensaio.json).
- [Navegador público em produção](navegador-publico-producao.json), [hashes publicados](hashes-publicados.json) e [endpoints](endpoints-publicados.json).
- [Preservação dos registros](preservacao-producao.json), [restauração do último dump](restauracao-banco-final.json) e [restauração dos arquivos](restauracao-arquivos.json).
- [Contagens e públicos da grade](grade-contagens-producao.json) e [limpeza dos ambientes de ensaio](limpeza-ensaios.json).
- [Fluxos autenticados publicados](production-browser-results.json), [gestão publicada](published-management.json) e [navegação por perfil](published-layout-results.json).
- [Limpeza da primeira rodada](production-cleanup.json), [limpeza da repetição de leituras](production-readonly-cleanup.json), [preservação após testes](production-data-after-ui.json) e [contagens finais](production-final-counts.json).

Observação para o ciclo da catraca: o catálogo devolve `source_url` com esquema HTTP atrás do proxy, embora a consulta e o ZIP em HTTPS funcionem. Rever a geração do endereço externo nesse ciclo; não há binário liberado nem OTA físico validado.

## Próxima entrega

A escolha de turmas no cadastro ainda não foi implementada. A leitura da grade confirmou 15 turmas publicadas ativas e ausência de limites de idade armazenados. As faixas Kids/adulto e as regras pendentes do vínculo precisam ser definidas antes da integração dependente. Aceite em massa e testes físicos da catraca continuam em frentes separadas.
