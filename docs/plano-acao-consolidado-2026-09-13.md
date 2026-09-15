**BJ Sports — Plano de ação consolidado**

Versão 1.7 • 14/09/2026 • **Situação: segunda entrega publicada e conferida; preferências, matrículas e portal integrados. Faixas etárias reais aguardam dados da academia.**

Revisão 1.7: cinco etapas concluídas. [Relatório atual da segunda entrega](segunda-entrega-2026-09-14/README.md), com regras operacionais, validação, correções, backup e reversão. As revisões anteriores abaixo são históricas.

Revisão 1.6: a consulta da grade real foi publicada no cadastro, adiantando a parte independente de 8/12. Individuais, combos e aula particular estão acessíveis; filtros de unidade/período e horários foram conferidos em 24 verificações publicadas, além de 110 testes PostgreSQL. As 23 contas atuais foram preservadas. A escolha com preferência/matrícula permanece pendente; [relatório atual](cadastro-horarios-2026-09-13/README.md).

Revisão 1.5: campos opcionais de idade publicados, com 105 testes PostgreSQL e conferência autenticada no HTTPS. Nesta retomada foi corrigida uma nova divergência entre backend e templates da VPS, preservando suas 22 contas. Backup vigente, limpeza dos testes e evidências no [relatório de 7/12](faixas-etarias-2026-09-13/README.md). A etapa 7/12 permanece parcial por depender das idades reais e das regras de escolha; 8–12/12 ainda não foram implementadas.

Revisão 1.4: etapas 1–6/12 concluídas no acompanhamento novo. Após autorização específica, os fluxos publicados e a navegação autenticada foram testados; todos os dados técnicos foram removidos e os registros anteriores preservados. A etapa 7/12 prepara limites de idade configuráveis, sem atribuir faixas às turmas existentes.

Revisão 1.3: o usuário pediu um novo plano com acompanhamento X/Y. O [plano de execução em 12 etapas](plano-execucao-2026-09-13.md) registra o estado atual: etapas 1–5 concluídas e 6 parcialmente validada. A divergência da VPS foi reconciliada na publicação, após backup restaurado e testes PostgreSQL. Veja o [relatório atual](execucao-2026-09-13/README.md). As seções históricas abaixo mantêm a base e a organização do plano anterior; use o acompanhamento novo para o estado operacional.

Revisão 1.2: usuário autorizou “comece a implementação das melhorias” e pediu continuidade. Implementada a entrega A conforme D01/D02 recomendadas. As decisões comerciais restantes continuam abertas. Veja o [relatório da entrega A](turmas-planos-2026-09-13/README.md).

Revisão 1.1: conferência de cobertura dos dois blocos reenviados pelo usuário, sobre integração do cadastro e consolidação de Turmas e planos. Foram explicitados requisitos já discutidos e acrescentada a correspondência ao final. Esta conferência não representa aceite para implementação.

Este documento reúne cadastro, login, contratos, turmas, planos, créditos, check-in, interface móvel, publicação e catraca. A implementação foi autorizada após a revisão do plano. A entrega A foi publicada e revalidada na VPS; os limites opcionais de idade também estão disponíveis. As decisões comerciais abertas e os novos vínculos de cadastro continuam nas próximas etapas.

A administração já está consolidada em **Turmas e planos**. A integração das turmas ao cadastro vem depois. O trabalho físico da catraca e o futuro contrato têm dependências próprias e não impedem as entregas do portal.

**1. Como acompanhar este plano**

- Usar os identificadores E01–E12 para etapas e D01–D10 para decisões.
- Estados de execução: aguardando aceite, a fazer, em andamento, em validação, validado localmente, publicado, conferido em produção, dependência externa.
- Registrar em cada entrega: escopo aprovado, arquivos/revisão, decisões utilizadas, testes, evidências, limitações e próximo passo.
- Diferenciar código pronto, migração ensaiada, publicação, navegação autenticada e operação física. Um resultado não substitui o outro.
- Atualizar este documento ao terminar cada etapa. Manter relatórios anteriores como histórico e apontar qual relatório os complementa.
- Não atribuir datas de entrega antes de resolver as decisões necessárias e estimar o trabalho. A ordem abaixo representa prioridade e dependência.
- O aceite do plano libera somente o escopo aceito. Uma decisão comercial ainda aberta precisa ser resolvida antes da implementação que dependa dela.
- Preparar e validar cada pacote antes da publicação. A pausa inicial foi encerrada pela autorização de implementação e publicação; a continuidade mantém essa autorização dentro do escopo aprovado. Registrar autorizações existentes e solicitar outra somente quando houver ação que exceda esse escopo.

**2. Base existente e limites da evidência**

Os itens abaixo foram conferidos nos relatórios do projeto e na análise realizada nesta conversa. A revisão 1.2 incluiu uma consulta somente leitura à VPS: há divergência entre os relatórios anteriores e o contêiner atual, conforme o relatório da entrega A. Os resultados anteriores permanecem históricos. Contagens e resultados históricos não representam uma medição contínua da produção.

| Frente | Situação registrada | Como entra neste plano |
| --- | --- | --- |
| DDD, CPF, cadastro, responsável e login por e-mail | Correções publicadas e testadas em 12/09, conforme relatório de produção | Preservar e incluir na regressão E06/E09 |
| Contrato após entrar, com 60 horas para novas contas | Publicado; sem aceite automático e sem prazo retroativo nas contas antigas | Preservar a decisão em todas as entregas |
| Check-in por turma, dia/horário, modalidade e capacidade | Correções publicadas; testes de aluno, monitor e instrutor registrados | Revalidar os efeitos dos novos vínculos em E07 |
| Créditos por modalidade | Implementação e testes registrados; regras descritas abaixo | Preservar limites e flexibilidade, sem reinterpretar planos legados |
| Interface a partir do celular | Publicada; conferência final registrada em 13/09 | Usar como base para as telas novas, sem refazer os ajustes já concluídos |
| Backup e PostgreSQL da primeira publicação | Backups restaurados em ambiente isolado e 93 testes aprovados no relatório de 12/09 | Evidência histórica; cada nova entrega exige preparação correspondente |
| Validação da publicação de layout | 44 combinações de página/perfil/largura; navegação pública e autenticada | Nessa publicação de layout não houve envio de cadastros, aceites ou check-ins; esses fluxos têm evidência na publicação anterior e em ambiente isolado |
| `/esp` e `/catracadoc` | Fonte, catálogo e procedimentos publicados | Manter documentação consistente com a versão e com os ensaios reais |
| Botão, relé, tablet e OTA na placa | Pendentes de bancada; software compilado e testado | Executar E11 com equipamento e operador disponíveis |
| Gestão e planos na mesma página | Publicada e revalidada em 13/09 | E02 concluída; manter no pacote completo |
| Turmas no cadastro | Consulta da grade por modalidade e combo publicada; ainda sem seleção persistida | Concluir escolha/resumo de E04 e vínculos E05 após as definições E03 |

Evidências consultadas:

- [Publicação de cadastro, check-in e documentação](validacao-2026-09-12/producao.md).
- [Revisão e publicação da interface móvel](interface-mobile-2026-09-12/README.md).
- [Regras de créditos por modalidade](regras_creditos_modalidades.md). Seu relato de implantação local é histórico; a evidência posterior está nos relatórios de publicação.
- [Firmware e limites de bancada](../firmware/README.md). As notas locais de ausência de publicação antecedem o relatório de produção; publicação do fonte não comprova gravação em placa.
- [Procedimentos da catraca](../templates/catraca_doc.html).
- Código analisado: [aplicação](../app.py), [turmas](../templates/gestao_turmas.html), [planos integrados](../templates/_plan_catalog.html) e [cadastro](../templates/login.html).

**3. Decisões já estabelecidas que devem ser preservadas**

| ID | Regra |
| --- | --- |
| R01 | A página principal será `/gestao_turmas.html`, com o nome visível **Turmas e planos**. |
| R02 | Trazer a administração de planos para essa gestão e retirar a página separada de `/planos_admin.html`. O destino de links antigos está em D02. |
| R03 | Modalidades e turmas serão tratadas nessa gestão unificada; planos utilizarão a mesma referência de modalidades. |
| R04 | O aceite do contrato acontece após entrar. Novas contas têm 60 horas contadas desde a criação, conforme o fluxo já implementado. Entrar novamente não reinicia esse prazo. |
| R05 | Registrar aceite somente após confirmação explícita, com versão, data e consistência entre conta e histórico. Criar conta ou visualizar o contrato não equivale a aceitar. |
| R06 | Ignorar as contas antigas pendentes por enquanto: não atribuir prazo, bloquear retroativamente nem criar aceite. A futura solicitação em massa dependerá do novo contrato. |
| R07 | Coletar e validar os dados do responsável no cadastro de menor. A coleta desses dados não deve produzir consentimento automático nem autorização de imagem. |
| R08 | Planos individuais de Jiu-Jitsu, Boxe e Muay Thai têm créditos e horários flexíveis dentro da modalidade. MMA, combos e especiais mantêm suas condições próprias. |
| R09 | A referência comercial registrada é R$ 90 para 2 aulas/semana, R$ 100 para 3 e R$ 120 para ilimitado, por modalidade elegível. A reorganização de telas não autoriza reajustes. |
| R10 | Cada aula é uma ocorrência: duas aulas no mesmo dia correspondem a duas ocorrências e, quando aplicável, dois créditos. Créditos expiram no próximo vencimento e não migram entre modalidades. |
| R11 | Manter dados reais, identificadores, presenças, faturas, aceites, configurações e uploads. Não criar vínculos ou atribuir frequências a contas antigas por suposição. |
| R12 | Manter a abordagem móvel, o acesso a Filiais/Ícones, os filtros necessários e os formulários com mensagem clara e dados preservados quando houver erro. |
| R13 | Botão de manutenção, comando autorizado, pulso do relé e passagem física precisam de evidências separadas. O botão ainda não foi validado no equipamento. |

**4. Decisões abertas para o aceite**

D01/D02 foram adotadas na entrega A. D03/D05/D08/D09 receberam tratamento operacional na segunda entrega, conforme o relatório atual: preferências sem vaga, uma matrícula fixa por modalidade e cadastro sem escolha pendente. Os limites reais de idade e as decisões comerciais futuras permanecem a definir.

| ID | Decisão | Recomendação ou definição necessária | Depende dela |
| --- | --- | --- | --- |
| D01 | Organização da página — publicada | Duas abas: **Turmas** e **Planos**. Em Planos, separar Individuais de Combos e especiais. Manter Filiais e Ícones como atalhos. | E02 |
| D02 | Destino da rota antiga — publicado | Tela/menu antigos retirados; GET de `/planos_admin` e `/planos_admin.html` redireciona para a aba Planos, preservando a categoria. POST antigo é recusado e não reexecutado. | E02 |
| D03 | O que significa escolher uma turma | Implementado: créditos salvam preferência sem reserva; os demais planos coletivos salvam matrícula na turma escolhida. | E03–E05, E07 |
| D04 | Idade e nível | Academia define faixas etárias de Kids/adulto e critérios de nível, inclusive iniciante/profissional. Não deduzir turma Kids simplesmente de idade inferior a 18 anos. | E03–E05, E07 |
| D05 | Capacidade e reserva | Implementado: preferência não consome capacidade; matrícula fixa entra na contagem de vagas. A última vaga é conferida com bloqueio no servidor. As reservas por ocorrência mantêm suas regras existentes. | E03, E05, E07 |
| D06 | Efeito da edição de um plano | O código atual pode atualizar nome/preço registrados em contas vinculadas. Na reorganização, não executar reajustes. Definir quando alterações futuras atingem novos cadastros, alunos existentes e próximos períodos, com impacto explícito. | E02 para preservar comportamento; E03 para qualquer mudança dessa política |
| D07 | Significado de “valor da turma” | Esclarecer seu uso atual e sua relação com a mensalidade. Manter campos separados até a definição; não substituir um valor pelo outro. | E03 e textos da gestão |
| D08 | Quantidade de escolhas | Regra operacional adotada: várias preferências nos créditos; uma turma fixa por modalidade; combos respeitam modalidades contratadas. Aula particular mantém o profissional. A pergunta sobre quantidades continua disponível para eventual ajuste da academia. | E03–E05 |
| D09 | Ausência de turma elegível | Regra operacional adotada: permite criar conta sem turma, com escolha pendente e sem reservar vaga; preserva o fluxo anteriormente disponível. Não escolhe turma incompatível automaticamente. | E04/E05 |
| D10 | Futuro contrato e aceite em massa | Conteúdo, versão, público, prazo, avisos e efeito da falta de aceite serão definidos depois. Não presumir que as novas regras sejam iguais às 60 horas do cadastro atual. | E12 |

D01 e D02 permitem iniciar a consolidação visual. D03–D09 orientam a integração com matrícula e não precisam atrasar a reorganização que preserve os dados e as regras atuais.

**5. Etapas de execução**

| Etapa | Prioridade | Dependência | Estado atual |
| --- | --- | --- | --- |
| E01 — Registrar a base e preparar o trabalho | Inicial | Aceite recebido | Concluída para entrega A; divergência de produção registrada |
| E02 — Unificar Turmas e planos | Primeira entrega | E01, D01–D02 | Publicada e conferida com autenticação na VPS |
| E03 — Definir catálogo, elegibilidade e vínculos | Antes do novo cadastro | E01, D03–D09 | Implementada a elegibilidade configurável e as regras operacionais; faixas etárias reais dependem da academia. |
| E04 — Exibir turmas no cadastro | Segunda entrega | E02/E03 | Publicada a seleção da grade real e o resumo por modalidade. |
| E05 — Persistir a escolha com consistência | Segunda entrega | E03/E04 | Publicada e validada a persistência atômica de conta e vínculos. |
| E06 — Preservar login, cadastro e contrato | Transversal | E02–E05 conforme alterações | Revalidada na publicação: CPF/e-mail, menor com responsável e contrato sem aceite automático. |
| E07 — Integrar portal, calendário e check-in | Segunda entrega | E03/E05 | Publicado e validado painel, calendário e check-in por modalidade e ocorrência. |
| E08 — Validar interface móvel e acessibilidade | Transversal | Cada tela alterada | Cadastro e portal conferidos em Chrome 390/1440; temas claro e escuro verificados localmente. |
| E09 — Validar dados, suíte e documentação | Por entrega | Implementação do pacote | Suíte e evidências concluídas para segunda entrega; ver relatório atual. |
| E10 — Backup, publicação e conferência | Por entrega | E09 e autorização da publicação | Segunda entrega publicada; recuperação atual em cadastro-integrado-r2, incluindo lockfix. |
| E11 — Validar catraca e equipamentos | Frente posterior | Hardware, operador e decisões de instalação | Dependência externa; aguarda aceite |
| E12 — Novo contrato e aceite em massa | Frente futura | Novo texto e D10 | Dependência externa; aguarda aceite |

**E01 — Registrar a base e preparar o trabalho**

Objetivo: iniciar sem misturar entregas anteriores com a implementação nova.

- [x] Registrar o aceite e as etapas incluídas; D01/D02 adotadas para entrega A, D03–D10 mantidas abertas.
- [x] Conferir a revisão local e a publicada nos arquivos afetados; inventariar as alterações já existentes no workspace.
- [x] Preservar os trabalhos anteriores, arquivos enviados e uploads sem agrupá-los automaticamente ao novo pacote.
- [x] Mapear rotas, menus, formulários, permissões, catálogo público, cadastro, financeiro, contratos, calendário e check-in que dependem de planos/turmas.
- [x] Preparar ambiente isolado e dados de teste para instrutor, monitor, adulto, menor, plano por créditos e plano fora de créditos.
- [x] Registrar somente dados necessários à comparação; relatórios compartilháveis não devem conter dados pessoais ou credenciais.

Critério de conclusão: escopo e dependências documentados, ambiente de teste preparado e base preservada.

**E02 — Unificar a administração em Turmas e planos**

Objetivo: manter uma entrada administrativa para a oferta da academia.

- [x] Renomear título, cabeçalho e item de menu para **Turmas e planos**.
- [x] Manter `/gestao_turmas.html` como endereço principal e tratar seus aliases existentes.
- [x] Criar a organização aprovada em D01, com navegação que conserve a aba após salvar ou apresentar erro.
- [x] Trazer os planos individuais da antiga aba “Modalidades”, além dos combos e especiais. Não perder os preços individuais ao retirar a tela antiga.
- [x] Preservar criação/edição, frequências, preços, descontos, benefícios, destaque, modalidades incluídas, compartilhamento e escolha de profissional quando aplicável.
- [x] Separar as ações dos formulários de turma e plano para evitar que um envio acione o cadastro errado.
- [x] Manter autorização de instrutor, proteção CSRF e bloqueio de exclusão de planos em uso.
- [x] Manter os atalhos de Filiais/Ícones e os filtros e detalhes das turmas.
- [x] Atualizar referências internas e implementar o tratamento aprovado em D02 para ambos os endereços antigos de planos.
- [x] Preservar IDs, preços, vínculos e históricos; a mudança de organização não deve disparar sincronizações comerciais ou recriar registros.

Critério de conclusão: criar e editar turma e plano pela página unificada, sem navegação interna para a tela antiga, sem perda de funções e sem mudança involuntária em contas existentes.

**E03 — Definir catálogo, elegibilidade e vínculo**

Objetivo: estabelecer uma referência comum para modalidade, oferta comercial e turma.

Cuidado identificado na análise: o vínculo de matrícula atual participa da contagem de ocupação das turmas. Salvar uma preferência como matrícula pode reservar capacidade indevidamente; definir D03/D05 antes dessa gravação.

- [ ] Definir as regras D03–D09 com exemplos reais da academia.
- [ ] Centralizar as referências de modalidades usadas na gestão, nos planos e no cadastro, mantendo a compatibilidade dos registros existentes.
- [ ] Revisar nome, unidade, público, nível, horários, situação e publicação das turmas. Registrar inconsistências para correção explícita, sem inferir a unidade pelo nome.
- [ ] Separar faixa etária de nível técnico quando necessário; não criar limites de idade não informados pela academia.
- [ ] Explicitar a diferença entre preferência de horário, matrícula fixa, reserva de aula e presença.
- [ ] Reutilizar matrícula existente quando essa for a regra aprovada. Se preferência exigir armazenamento próprio, propor migração aditiva e validação antes de aplicá-la.
- [ ] Alinhar rótulos de frequência: 2/3 aulas e ilimitado nos créditos; condições próprias de dias/horários para MMA e especiais.
- [ ] Revisar a influência das edições de plano nas contas, mensalidades e períodos de crédito. Exibir impacto e aplicar a política aprovada em D06.
- [ ] Definir o texto e a finalidade dos campos de valor da turma e mensalidade do plano segundo D07.
- [ ] Não migrar alunos antigos para turmas por nome de plano, preço ou modalidade presumida.

Critério de conclusão: regras suficientes para avaliar a elegibilidade e a ocupação de uma turma sem contradições entre cadastro, gestão e check-in.

**E04 — Apresentar as turmas no cadastro**

Objetivo: ao escolher a modalidade, o aluno conhecer a oferta real e fazer a escolha prevista em seu plano.

Fluxo proposto: **modalidade → frequência/plano → turmas e horários → resumo → criação da conta**. Unidade e público entram como filtros quando necessários.

- [x] Consultar as turmas da gestão; não manter horários duplicados em textos manuais do cadastro. Consulta publicada em 8/12, ainda sem escolha persistida.
- [ ] Apresentar nome, unidade, dias, horários, público/nível e responsável quando disponíveis.
- [ ] Permitir seleção apenas das turmas publicadas e elegíveis, com condição de disponibilidade coerente com D05.
- [ ] Identificar turmas lotadas sem prometer vaga; não oferecer turmas inativas ou não publicadas.
- [ ] Oferecer filtros por unidade e período quando ajudarem a escolher; usar cartões legíveis no celular.
- [ ] Limpar escolhas incompatíveis ao alterar modalidade, plano, unidade ou dados de elegibilidade e informar o motivo.
- [ ] Não selecionar turma ou frequência silenciosamente.
- [ ] Tratar carregamento, falha de consulta e ausência de turma com mensagens claras, aplicando D09.
- [ ] Nos combos, apresentar turmas para cada modalidade contratada/escolhida, respeitando a elegibilidade. Definir a quantidade de escolhas conforme D08, atender os compartilhados e preservar a seleção específica de profissional para aula particular.
- [ ] Mostrar resumo de modalidade, frequência, preço e natureza da escolha: preferência ou matrícula.

Critério de conclusão: mudança de horário na gestão aparece no cadastro; cada escolha corresponde a um registro real; ausência ou indisponibilidade têm tratamento compreensível.

**E05 — Salvar conta e escolha com consistência**

Objetivo: garantir que a escolha vista pelo aluno corresponda ao resultado persistido.

- [ ] Validar no servidor plano, modalidade, idade/público, unidade, situação, publicação, cardinalidade das escolhas e capacidade, conforme as regras aprovadas.
- [ ] Recusar identificadores adulterados, turma excluída/inativada ou escolha que deixou de ser elegível entre abrir e enviar o formulário.
- [ ] Quando houver matrícula, salvar conta e vínculos em uma transação; quando houver preferência, persistir como preferência, sem reservar vaga permanente.
- [ ] Proteger a disputa pela última vaga e submissões simultâneas no PostgreSQL; manter compatibilidade com o ambiente local de testes.
- [ ] Impedir duplicidade de CPF, conta e vínculo em cliques ou envios repetidos.
- [ ] Em erro, devolver mensagem específica e preservar os campos adequados sem expor dados pessoais em cookies ou logs e sem guardar senhas para reapresentação.
- [ ] Não gerar presença, pagamento ou aceite de contrato apenas porque a conta ou a matrícula foi criada.
- [ ] Registrar data/origem dos novos vínculos quando necessário e mostrar o resultado no portal.

Critério de conclusão: falhas não deixam contas ou matrículas parciais; duas solicitações concorrentes não recebem a mesma última vaga.

**E06 — Preservar login, cadastro e contrato**

Objetivo: manter as correções já publicadas ao alterar o formulário e suas dependências.

- [ ] Conferir todos os 67 DDDs brasileiros, largura do seletor, envio do campo correto e cadastro com DDDs distintos.
- [ ] Conferir CPF pontuado e sem pontuação, normalização, validação e rejeição de duplicidade inclusive em concorrência.
- [ ] Manter a indicação de login por CPF ou e-mail e testar ambos.
- [ ] Conferir data de nascimento, identificação de menor e coleta/validação dos dados do responsável.
- [ ] Criar nova conta sem aceite automático e com 60 horas desde a criação.
- [ ] Testar confirmação explícita, consistência conta/histórico, nova sessão sem reiniciar prazo e comportamento após vencimento, usando dados de teste.
- [ ] Confirmar que contas antigas pendentes não recebem prazo ou aceite retroativo.
- [ ] Preservar a separação entre contrato, aviso de privacidade e autorização de imagem, conforme o fluxo existente.
- [ ] Conferir textos comerciais e opções contra o catálogo aprovado; não alterar versões de contrato por uma reorganização de interface.

Critério de conclusão: fluxos adulto/menor, CPF/e-mail, prazo e aceite passam sem regressão e sem alteração dos registros legados.

**E07 — Integrar painel, calendário e check-in**

Objetivo: refletir a escolha feita no cadastro sem retirar a flexibilidade dos planos por créditos.

- [ ] Mostrar turmas matriculadas e preferências com rótulos que expressem sua natureza.
- [ ] Alimentar calendário e links de horários com a grade oficial, respeitando o tipo de vínculo.
- [ ] Manter acesso a outras aulas elegíveis da mesma modalidade nos créditos flexíveis; preferência não deve virar restrição automática.
- [ ] Validar a turma e a ocorrência escolhidas: situação, dia, horário, modalidade, elegibilidade e disponibilidade.
- [ ] Conferir capacidade zero, turma lotada, matrícula fixa, presença pendente/confirmada e reserva, segundo D05; vínculo existente não deve mascarar capacidade inválida.
- [ ] Evitar uso dos dias de outras matrículas para autorizar a turma selecionada.
- [ ] Preservar uma identidade por aluno/data/turma/horário, permitindo duas aulas no mesmo dia sem duplicar a mesma ocorrência.
- [ ] Preservar reserva de crédito no check-in pendente, consumo na confirmação e liberação na recusa; respeitar vencimento e limites por modalidade.
- [ ] Conferir os planos fora de créditos e as regras de aula experimental, sem aplicar automaticamente o modelo de Jiu-Jitsu/Boxe/Muay Thai a MMA ou especiais.
- [ ] Testar aluno solicitando, monitor confirmando e instrutor recusando, com permissões e resultado persistido conferidos.

Critério de conclusão: o aluno vê sua situação corretamente e o servidor decide cada check-in pela aula selecionada e pelas regras do seu plano.

**E08 — Interface móvel e acessibilidade**

Objetivo: manter o portal utilizável em celulares e tornar a nova gestão prática.

- [ ] Priorizar formulário e ação principal; evitar apresentação extensa antes do cadastro.
- [ ] Usar apenas o conteúdo da aba ativa em Turmas e planos, sem obrigar o usuário a percorrer duas páginas administrativas empilhadas.
- [ ] Adaptar listas/tabelas para leitura e edição em telas pequenas, com rótulos claros e sem rolagem horizontal da página.
- [ ] Conferir teclado, foco, abertura/fechamento de menu e modal, mensagens de erro e campos obrigatórios.
- [ ] Preservar controles com área de toque confortável, contraste em tema claro/escuro, movimento reduzido e área segura inferior.
- [ ] Conferir sobreposição de WhatsApp/barra inferior e o comportamento com teclado virtual.
- [ ] Validar 360/390 px, tablet e desktop; incluir aparelhos físicos Android/iOS quando disponíveis e registrar quando houver somente emulação.

Critério de conclusão: fluxos essenciais podem ser concluídos por toque e teclado, com conteúdo legível, sem botões encobertos ou perda de campos após erro.

**E09 — Testes, integridade e documentação por entrega**

Objetivo: preparar uma entrega concreta, reproduzível e revisável.

- [ ] Atualizar os testes afetados pelos nomes, rotas e formulários, mantendo os testes das regras de negócio.
- [ ] Adicionar testes para nova elegibilidade, preferências/matrículas, concorrência pela última vaga e consistência da transação.
- [ ] Executar primeiro verificações pertinentes ao pacote; executar a suíte completa antes da entrega e repetir quando alterações ou falhas justificarem.
- [ ] Ensaiar migrações necessárias em cópia isolada no PostgreSQL, incluindo execução repetida, preservação de IDs e relações. Não usar importação da aplicação de produção como consulta somente leitura se ela executa migrações na inicialização.
- [ ] Conferir integridade somente dos dados e relações necessários ao escopo, evitando exportações de informações pessoais.
- [ ] Validar no navegador público/autenticado em ambiente de teste: gestão, cadastro, entrada, contrato, calendário e check-in aplicáveis ao pacote.
- [ ] Cobrir explicitamente adulto, menor com responsável, combo com turmas por modalidade, ausência de turma, turma lotada ou inativada entre abrir/enviar, alteração de modalidade, envio duplicado e disputa pela última vaga. Conferir aluno, monitor e instrutor; usar PostgreSQL isolado nos testes de persistência e concorrência.
- [ ] Testar a edição de turma/plano e conferir seus efeitos no cadastro, catálogo público, conta do aluno e financeiro, conforme D06. Alterar um horário de teste na gestão e verificar sua atualização no cadastro; confirmar que apenas reorganizar a página não altera preços ou registros financeiros.
- [ ] Registrar resultados, evidências sanitizadas, limitações e instruções para reproduzir.
- [ ] Atualizar a documentação administrativa de Turmas e planos e o fluxo do aluno; atualizar `/catracadoc` apenas com procedimentos e resultados relacionados à catraca.
- [ ] Acrescentar notas de situação aos documentos que ainda descrevem etapas locais anteriores à publicação, preservando o histórico.
- [ ] Apresentar o pacote final com alterações, migrações, riscos concretos e reversão antes de sua publicação.

Critério de conclusão: verificações pertinentes aprovadas, nenhuma falha sem explicação no escopo e documentação alinhada à entrega.

**E10 — Backup, publicação e conferência na VPS**

Objetivo: aplicar cada pacote aprovado e confirmar seu comportamento publicado.

Controles concluídos para o pacote atual, conforme o [relatório de 7/12](faixas-etarias-2026-09-13/README.md). A lista abaixo permanece como preparação obrigatória da próxima entrega B; não significa que a publicação atual esteja pendente.

- [ ] Confirmar alvo, arquivos e revisão, migrações e janela de ativação necessários à entrega.
- [ ] Guardar backup novo do PostgreSQL, fonte/imagem anterior, volume e uploads relevantes; verificar integridade e ensaiar a restauração do backup PostgreSQL em ambiente isolado antes da ativação do pacote.
- [ ] Não tratar o backup de setembro anterior como cobertura de dados criados depois dele.
- [ ] Preparar reversão de código e avaliar compatibilidade da migração. Não restaurar o banco automaticamente sobre cadastros, presenças ou pagamentos posteriores.
- [ ] Registrar a autorização aplicável ao pacote validado. O usuário já autorizou a implementação, a publicação na VPS e a continuidade; pedir nova autorização somente para ações que excedam esse escopo.
- [ ] Aplicar somente o pacote aprovado, recriando os serviços necessários e evitando interrupção do banco quando não exigida.
- [ ] Conferir serviços, logs, hashes de arquivos ativos e assets públicos, URLs e tratamento das rotas antigas.
- [ ] Validar os fluxos publicados em desktop/celular, com autenticação nos perfis pertinentes. HTTP 200 não substitui essa conferência.
- [ ] Quando o escopo de validação incluir criação/envio, usar registros técnicos identificáveis e removê-los por identificadores exatos ao final; não alterar alunos reais para simular regras.
- [ ] Registrar o que foi apenas consultado e o que foi efetivamente enviado, gravado e conferido no banco.
- [ ] Em falha que impeça a operação, executar o procedimento aprovado de correção/reversão, preservando dados novos; documentar o resultado.

Critério de conclusão: versão correta ativa, fluxos pertinentes conferidos no site, dados técnicos tratados e procedimento de reversão preservado.

**E11 — Firmware, botão, tablet e catraca física**

Objetivo: concluir a validação que o software e a documentação publicados ainda não comprovam.

- [ ] Registrar placa, relé, mecanismo, alimentação, versão instalada, configuração de partições e possibilidade de recuperação física; preservar a versão anterior.
- [ ] Reavaliar as APIs do servidor utilizadas pelo kiosk: autenticação do dispositivo, acesso a dados do aluno e decisão financeira/de acesso. O token do ESP não substitui a autorização do aluno no backend.
- [ ] Validar o botão GPIO27 na inicialização, a abertura restrita de manutenção e seu encerramento após 10 minutos. Confirmar que manutenção não equivale a destravamento.
- [ ] Medir relé desligado em boot/reset/retorno de energia e pulsos de 300/1000/3000 ms, inclusive sob requisições lentas e repetidas.
- [ ] Conferir recusa de token inválido, origem indevida, comando expirado/repetido, dispositivo ocupado e preflight sem acionamento.
- [ ] Testar Wi-Fi indisponível, reconexão, perda de resposta e ausência de repetição automática do comando no tablet.
- [ ] Selecionar e validar o transporte entre site HTTPS e dispositivo local no tablet real, conforme a instalação. Não presumir que CORS resolva restrições de HTTPS/HTTP.
- [ ] Ensaiar atualização válida, arquivo inválido, interrupção, reinício e recuperação por USB; definir assinatura e estratégia de retorno de versão conforme a placa antes da liberação operacional.
- [ ] Validar proteções elétricas e saída de emergência com o responsável pela instalação e o mecanismo real.
- [ ] Se houver sensor, definir e testar o registro de passagem. Sem sensor, mostrar comando/pulso sem chamar o contador de giros ou presenças.
- [ ] Registrar ensaios prolongados, resultados e limitações em `/catracadoc`; publicar binário somente com identificação/manifesto e critérios de liberação cumpridos.

Critério de conclusão: relatório de bancada com data, operador, montagem, versão e resultado de cada ensaio; liberação operacional depende desses resultados, não apenas da compilação.

**E12 — Novo contrato e solicitação de aceite em massa**

Objetivo: preparar a atualização futura mencionada pelo usuário, sem alterar as pendências antigas agora.

- [ ] Receber o novo texto aprovado pela academia e definir D10.
- [ ] Criar nova versão preservando versões e aceites anteriores.
- [ ] Definir destinatários e regras para titular, dependente e responsável quando aplicáveis.
- [ ] Implementar solicitação e confirmação explícita com data/versão e histórico consistente; nunca gerar aceite em nome do aluno.
- [ ] Exibir situação real de pendência e confirmação e testar prazos/avisos com contas técnicas.
- [ ] Separar aceite contratual de autorização de imagem.
- [ ] Apresentar a população afetada e o efeito operacional para revisão, sem expor dados desnecessários.
- [ ] Publicar e iniciar a solicitação somente quando a nova versão e a ativação forem autorizadas. Comunicações por canais externos exigem autorização própria.

Critério de conclusão: nova versão solicitada apenas ao público definido, histórico anterior preservado e confirmações registradas somente por ação explícita.

**6. Melhorias posteriores propostas**

Estes itens ficam visíveis no planejamento, mas não entram automaticamente na primeira entrega.

| ID | Melhoria | Benefício e condição |
| --- | --- | --- |
| M01 | Aluno editar suas preferências de horário | Facilitar mudanças sem consumir vaga indevida; depende de D03–D05. |
| M02 | Lista de espera por turma | Registrar interesse sem garantir matrícula; definir ordem, aviso e confirmação antes de automatizar. |
| M03 | Impacto e vigência de alterações comerciais | Mostrar quem será afetado por reajuste e a partir de quando; depende de D06. |
| M04 | Referência estável ao plano contratado | Avaliar associação por identificador e versão das condições, reduzindo dependência de nomes/textos; exige migração explícita, sem adivinhar planos legados. |
| M05 | Histórico de alterações da gestão | Identificar responsável, data e mudança em turma/plano, com acesso administrativo. |
| M06 | Medição agregada do cadastro | Identificar erros e abandono por etapa com dados reais, sem registrar CPF, senha ou dados do responsável na telemetria. |
| M07 | Lembretes de aula | Usar horários e preferências/matrículas corretos; revisar o mecanismo existente antes de criar outro e obter autorização antes de enviar comunicações. |

**7. Organização das entregas e controle de conclusão**

| Entrega | Conteúdo | Condição para publicar |
| --- | --- | --- |
| A — Gestão unificada | E01/E02 e definições de catálogo estritamente necessárias; E06/E08/E09 aplicáveis | Gestão funcional, dados preservados, rotas resolvidas e E10 autorizado |
| B — Cadastro conectado às turmas | E03–E07 e adaptação E08 | Regras de matrícula/preferência resolvidas, PostgreSQL e fluxos aprovados em E09, E10 autorizado |
| C — Catraca operacional | E11 e sua documentação | Equipamento real validado e ativação autorizada |
| D — Novo contrato | E12 | Novo texto, público, prazo e ativação aprovados |
| Melhorias posteriores | M01–M07 selecionadas | Escopo priorizado e validado antes de cada publicação |

Para cada entrega, preencher:

| Campo | Registro inicial |
| --- | --- |
| Escopo aceito | Início da implementação autorizado; entrega A executada |
| Decisões utilizadas | D01/D02 recomendadas; demais decisões comerciais abertas |
| Responsável pela validação de negócio | A definir pela academia |
| Revisão e arquivos do pacote | Manifesto e alterações no relatório da entrega A |
| Testes e evidências | 98 testes; 28 verificações de navegador; evidências no relatório A |
| Migração/backup/reversão | A preencher para o pacote concreto |
| Autorização da publicação | Aguardando |
| Resultado no site/aparelho | Nova entrega não publicada; consulta atual encontrou `/catracadoc` em 404 e divergência no código de contrato |
| Pendências e próximo passo | Reconciliar base para publicação da entrega A; definir regras pendentes de E03 |

**8. Correspondência com os dois blocos conferidos pelo usuário**

Esta tabela permite localizar os requisitos sem reiniciar o planejamento. A numeração dos dois textos foi incorporada aos identificadores E01–E12; a implementação da entrega A foi autorizada posteriormente à conferência; as demais dependências continuam registradas.

| Requisito dos textos anteriores | Onde está no plano | Tratamento |
| --- | --- | --- |
| Consolidar a gestão antes de integrar o cadastro | E02; entregas A/B | Primeira implementação nova é Turmas e planos. |
| Título e único item de menu; abas Turmas e Planos | R01–R03, D01, E02 | Planos contém Individuais e Combos e especiais. |
| Trazer toda a configuração comercial, inclusive preços individuais | E02 | Preservar formulários, frequências, descontos e benefícios. |
| Modalidades e horários como referência comum | E03/E04 | Usar os registros da gestão e eliminar horários manuais divergentes. |
| Retirar tela/links antigos e redirecionar favoritos | D02, E02 | Redirecionamento implementado localmente para ambos os endereços antigos. |
| Preferência nos créditos; matrícula em turma fixa | D03/D05, E03/E05/E07 | Preferência proposta sem reserva permanente e com liberdade para outras aulas elegíveis. |
| Turmas de cada modalidade do combo | D08, E04/E09 | Apresentação e teste explícitos; quantidade de escolhas ainda depende da regra do plano. |
| Kids por faixa etária; nível técnico separado; unidade correta | D04, E03 | Faixas definidas pela academia e revisão dos registros de turmas. |
| Filtros, professor, horários e indicação de indisponibilidade | D09, E04 | Excluir da seleção turmas inativas/não publicadas e não prometer vaga em turma lotada. |
| Fluxo modalidade → frequência/plano → turmas → resumo | E04/E08 | Cartões móveis, filtros por unidade/período e remoção de escolhas incompatíveis. |
| Salvar conta e matrícula juntas e proteger última vaga | E05/E09 | Validação no servidor, transação, duplicidade e concorrência. |
| Contrato após entrar, 60 horas para novos, antigas pendentes preservadas | R04–R07, E06 | Sem aceite automático nem cobrança retroativa às contas antigas. |
| Painel, calendário, check-in e créditos por aula/modalidade | R08–R10, E07 | Preservar flexibilidade, duas aulas no dia e regras próprias de MMA/especiais. |
| Testes adulto/menor/combos/lotação/inativação/troca/perfis | E06–E09 | Cenários explícitos, navegador móvel/desktop e PostgreSQL isolado. |
| Conferir edição, catálogo público e financeiro | D06, E02/E09 | Validar efeitos conforme a política aprovada, sem reajuste pela reorganização. |
| Separar valor da turma de mensalidade; mostrar impacto do reajuste | D06/D07, E03, M03 | Finalidade dos campos e vigência comercial dependem das definições da academia. |
| Interface com apenas a aba ativa e atalhos Filiais/Ícones | D01, E02/E08 | Preservar navegação e usar formulários legíveis no celular. |
| Backup, restauração, reversão, publicação e evidências | E09/E10 | Ensaio de restauração isolada, publicação autorizada e conferência dos fluxos publicados. |
| Aluno alterar preferência; lista de espera; medição agregada | M01/M02/M06 | Melhorias posteriores já registradas, sem promessa antecipada de vaga ou dados inventados. |

**Situação final desta versão:** entrega A implementada e validada localmente. A VPS recebeu somente consultas de leitura. A publicação depende da preparação de um pacote compatível com a base atual, validação correspondente e autorização. Integração do cadastro, hardware e novo contrato permanecem nas próximas etapas.
