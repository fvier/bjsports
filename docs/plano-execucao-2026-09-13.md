# Plano de execução acompanhado — BJ Sports

Atualizado em 14/09/2026. Solicitado pelo usuário: novo plano e avisos de etapa X/Y até concluir.

Este é o acompanhamento operacional do [plano consolidado](plano-acao-consolidado-2026-09-13.md). A primeira entrega publica a gestão unificada e reconcilia as correções anteriores ausentes na VPS. A segunda integra a escolha de turmas ao cadastro e ao portal, conforme as decisões comerciais.

| Etapa | Trabalho e critério de conclusão | Estado |
| --- | --- | --- |
| 1/12 | Conferir fonte local, contêiner, pendências e escopo. | Concluída: divergência de app.py e menu confirmada novamente na VPS. |
| 2/12 | Consolidar o pacote de correções e Turmas e planos; registrar hashes, preservar configurações e uploads. | Concluída: 26 arquivos e remoção da tela antiga; todas as diferenças locais de runtime cobertas. |
| 3/12 | Ensaiar o pacote em PostgreSQL isolado, conferir migração e executar suíte e navegador. | Concluída: 98 testes SQLite, 98 PostgreSQL, 7 fluxos e 28 verificações de gestão no navegador. |
| 4/12 | Backup atualizado de banco, fonte, imagem e volume; comprovar restauração e preparar reversão. | Concluída: banco, 24 arquivos de fonte, 3 arquivos do volume e imagem recuperados. |
| 5/12 | Publicar a primeira entrega na VPS com o pacote validado. | Concluída em 13/09 às 16h23 (America/Recife). |
| 6/12 | Conferir cadastro, contrato, login, check-in, gestão e documentação na publicação; remover somente dados técnicos. | Concluída: 7 fluxos, 12 verificações da gestão e 44 de navegação publicados; limpeza e preservação das 21 tabelas confirmadas. |
| 7/12 | Definir preferência versus matrícula, faixas etárias, disponibilidade, combos e cadastro sem turma. | Regras operacionais implementadas: créditos como preferência; turma fixa com matrícula; uma turma fixa por modalidade; sem escolha, conta pendente sem vaga. Permanecem as faixas etárias reais a informar pela academia. |
| 8/12 | Consultar turmas reais no cadastro e exibir modalidade, unidade, público, professor e horários em celular/desktop. | Concluída: grade real, seleção, filtros e resumo publicados em celular/desktop. |
| 9/12 | Persistir conta e escolha em transação; validar elegibilidade, duplicidade e disputa de vaga. | Concluída: transação, duplicidade e última vaga verificadas em PostgreSQL; bloqueios não alteram metadados das turmas. |
| 10/12 | Mostrar escolhas no painel/calendário e manter as regras de cada check-in e modalidade. | Concluída: painel, calendário, agenda pessoal e check-in integrados e conferidos no HTTPS. |
| 11/12 | Ensaiar segunda entrega em PostgreSQL, validar concorrência e fluxos adulto/menor/combo/perfis e interface. | Concluída: suíte PostgreSQL, concorrência, adulto/menor/combo, aluno/monitor/instrutor e navegação publicados. |
| 12/12 | Preparar backup próprio, publicar a segunda entrega, conferir produção e registrar evidências finais. | Concluída: publicação final às 17h44 de 14/09, backups restaurados, sete contas técnicas removidas e 22 tabelas preservadas. Ver relatório da segunda entrega. |

## Regras preservadas

- Contrato após entrar: 60 horas desde a criação para contas novas, sem aceite automático ou reinício do prazo. Contas antigas pendentes ficam sem cobrança retroativa.
- Créditos de Jiu-Jitsu, Boxe e Muay Thai permanecem separados e contam cada ocorrência de aula. Não reclassificar registros antigos por suposição nem alterar preços.
- Implementado na segunda entrega: horário em plano por créditos é preferência, sem matrícula ou reserva permanente; plano de turma fixa gera matrícula e ocupa vaga. A capacidade precisa ser validada no servidor.
- Turmas Kids usam faixas informadas pela academia; menoridade para responsável é uma regra distinta. Nenhum limite será inventado.
- Usar somente registros reais para a oferta; testes usam dados técnicos identificáveis em ambientes isolados e, na conferência publicada, com remoção restrita a esses registros.
- Registrar separadamente testes locais, PostgreSQL, emulação de navegador, produção e equipamento físico.

## Limites e dependências

A verificação física do botão/relé/OTA depende de equipamento e operador. O futuro aceite em massa depende do novo texto e das regras da campanha. Essas duas frentes permanecem no plano consolidado e não serão marcadas como concluídas com testes de software.

As etapas dependentes de decisões comerciais permanecem pendentes enquanto não houver resposta suficiente. A execução das demais etapas continua. Uma mudança de estado será documentada e comunicada como etapa X/12; somente evidência efetiva permite marcar conclusão.

## Registro da execução

- 1/12: leitura da VPS em 13/09 confirmou o host e contêiner ativos. app.py e menu permanecem divergentes da base local. Configurações privadas não foram expostas. Nenhuma mudança remota nesta etapa.
- 2/12: inventário completo confirmou 21 contas, coluna contract_due_at e índice de CPF existentes. Fonte da VPS coincide com seu contêiner. O pacote reúne gestão unificada, correções de cadastro/contrato/check-in, documentação e interface; não inclui dados locais, uploads ou configurações. Criado suporte protegido a testes PostgreSQL isolados. Cópia para ensaio não equivale a publicação.
- 3/12: SQLite 98/98 em 43,779 s; PostgreSQL 98/98 em 109,680 s. Clone real permaneceu privado e duas inicializações não alteraram registros das 21 tabelas. Após rejeição automática do túnel ao clone, foi criado um PostgreSQL vazio e contas técnicas para o navegador: 7 fluxos de cadastro/contrato/login/check-in e 28 verificações de gestão aprovados. Inicializar o banco vazio em processo único antes dos workers evita disputa pela conta padrão na preparação. A suíte recusa configuração direcionada ao banco de produção.
- 4/12: backup privado em /data/bjsports/backups/20260913-turmas-planos; checksums e gzip conferidos. Restauração de banco, arquivos, volume e imagem anterior ensaiada. Reversão restaura somente arquivos do pacote e imagem anterior, sem restaurar automaticamente o banco nem apagar novos registros. O procedimento recusa arquivos modificados após o pacote.
- 5/12: publicação concluída às 19h23 UTC (16h23 local), somente bjsports-app recriado. PostgreSQL permaneceu ativo. Os 27 itens do manifesto conferem diretamente no contêiner publicado; a tela antiga foi removida e seus GETs exigem autenticação e redirecionam na aplicação nova.
- 6/12: 10 consultas de páginas públicas em Chrome 390/1440 px aprovadas, sem erro JavaScript nem rolagem horizontal. Último dump, obtido com a aplicação parada, restaurado isoladamente; 21 tabelas idênticas. Leitura após publicação confirmou as 21 contas e registros anteriores preservados, nenhum prazo novo em conta antiga e zero contas técnicas criadas em produção. A revisão automática recusou a gravação dos registros técnicos; a solicitação explícita ao usuário descreve 6 contas, 1 turma fora da grade pública, 4 presenças e 3 aceites, com limpeza restrita. A conferência autenticada não foi declarada concluída.
- Preparação de 7/12: existem 15 turmas publicadas ativas: 12 com público Adulto e 3 Kids (2 Jiu-Jitsu, 1 Muay Thai). Não há limites de idade armazenados. Kids e menoridade legal precisam ser tratados separadamente; a pergunta de faixas etárias permanece aberta.
- Encerramento do ensaio: contêineres, volumes anônimos e redes temporários removidos; backups mantidos. Produção ativa na conferência final. Estado detalhado e evidências no [relatório da publicação](execucao-2026-09-13/README.md). Continuar 6/12 após resposta à autorização específica; a integração dependente de faixa etária permanece em 7/12.
- 6/12 concluída após o usuário responder “continue” à solicitação específica: cadastro adulto/menor, contrato, login por CPF/e-mail e quatro check-ins aprovados no HTTPS público. Gestão: 12 verificações; navegação: 44 verificações nos três perfis, em 390/1440 px. Um erro transitório ERR_NETWORK_CHANGED interrompeu a leitura da gestão; a primeira rodada foi limpa e somente as três contas de perfis foram recriadas para repetir as leituras. Ao final foram removidos os registros técnicos das duas rodadas. Snapshot anterior à validação: 21 tabelas idênticas após limpeza; 21 contas, zero contas técnicas e nenhum prazo retroativo.
- 7/12: implementados localmente limites opcionais de idade por turma, sem preenchimento automático para Kids/adulto. Vazio continua significando não definido. Servidor e banco recusam valores inválidos e intervalo invertido; a edição legada que omite os novos campos preserva os limites existentes. Esta preparação ainda não altera cadastro, matrículas ou check-in nem foi publicada.

- Continuidade de 7/12, 13/09 às 22h36: a VPS foi encontrada com backend recente e templates/assets incompletos; /catracadoc retornava 500. A causa da troca de imagem não foi determinada. Foi feito um novo backup do estado corrente, com 22 contas, e publicado um pacote coerente sobre a imagem atual, preservando as demais alterações. Os 28 itens conferem na fonte e no contêiner; /catracadoc voltou a responder 200.
- 7/12, validação técnica concluída: 105 testes no PostgreSQL; migração legada ensaiada duas vezes em clone privado e em SQLite; editor de idades com 6 verificações locais e 6 publicadas. No HTTPS publicado, passaram novamente 7 fluxos de cadastro/contrato/login/check-in, 12 verificações da gestão e 44 de navegação. A repetição da navegação corrigiu um caminho de configuração no teste; não foi uma falha da aplicação.
- Limpeza desta rodada: seis contas, uma turma técnica, uma matrícula, quatro presenças e três aceites removidos; depois, três perfis temporários removidos após repetir somente a navegação. As 21 tabelas ficaram idênticas ao snapshot anterior aos testes. Permanecem 22 contas reais, nenhuma conta/turma técnica e nenhuma faixa etária atribuída por suposição. Contêiner, volume e rede do PostgreSQL de ensaio removidos.
- Backup vigente: /data/bjsports/backups/20260913-age-rehearsal, com restauração de banco, imagem, fonte e volume conferida. A pasta do primeiro backup foi encontrada incompleta e deixou de ser referência de recuperação disponível. Procedimento e evidências no [relatório das faixas etárias e correção da publicação](faixas-etarias-2026-09-13/README.md).
- Pendências de 7/12: solicitadas as idades por turma/modalidade, a quantidade de escolhas e o tratamento do cadastro sem turma disponível. Existem 15 turmas públicas sem idade definida; Jiu-Jitsu Kids 1, Jiu-Jitsu Kids 2 e Muay Thai Kids precisam de limites da academia. Conferir também a unidade da turma Jiu-Jitsu | São Jose Piranhas, atualmente vinculada à sede de Cajazeiras; não alterar pelo nome. As etapas 8–12 continuam pendentes.

- Continuidade autorizada: avançada a parte de 8/12 independente das decisões comerciais. Publicados às 23h13 de 13/09 a consulta da grade real no cadastro, filtros por unidade/período, faixas informadas, professor e horários, com indicação de lotação. Consulta não cria matrícula ou preferência. Restabelecido o acesso visível a Individuais/Combos e especiais.
- 8/12, validação: 110 testes SQLite e 110 PostgreSQL aprovados; oito cenários de navegador sintético e 24 verificações no HTTPS publicado. Horários de cada modalidade/combinação comparados à gestão. As listas maiores começam recolhidas; falha da consulta permite tentar novamente sem bloquear o formulário.
- Publicação de 8/12: 29 itens conferidos na fonte e no contêiner, 23 contas e todas as 21 tabelas preservadas. Nenhuma gravação técnica em produção nesta rodada. Backup atual: /data/bjsports/backups/20260914-cadastro-horarios, com restauração comprovada de banco, fonte, volume e imagem. [Relatório e evidências](cadastro-horarios-2026-09-13/README.md).
- Estado para a próxima continuidade: 7/12 parcial por depender de dados da academia; 8/12 com consulta concluída, escolha/resumo ainda pendentes; 9–12 pendentes. A publicação da consulta não equivale à publicação da matrícula integrada prevista em 12/12.

## Encerramento — segunda entrega, 14/09/2026

As cinco etapas da continuidade foram concluídas. [Relatório, regras adotadas, evidências e recuperação](segunda-entrega-2026-09-14/README.md). O resumo do cadastro distingue preferência sem vaga de matrícula efetiva; escolhas vazias ficam pendentes. As faixas etárias reais permanecem como dado da academia a cadastrar. A nova rota de catraca publicada em paralelo foi preservada. Após a conferência final, sete contas técnicas e seus vínculos foram removidos; as 22 tabelas voltaram ao estado anterior, sem diferenças.
