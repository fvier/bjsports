# Segunda entrega — cadastro, turmas e portal

14/09/2026. Execução autorizada pelo usuário nas cinco etapas: seleção da grade real, consistência dos vínculos, portal, validação e publicação/documentação.

## Comportamento

- O cadastro usa os registros de Turmas e planos, por modalidade e unidade ativa. Mostra horários, professor, público, limites de idade e lotação.
- Planos individuais por créditos de Jiu-Jitsu, Boxe e Muay Thai salvam uma ou mais preferências em `class_preference`. Esses registros não entram na contagem de vagas e não restringem os créditos a uma turma.
- Os demais planos coletivos salvam matrícula ativa em `class_enrollment`, com uma turma por modalidade selecionada. Combos respeitam as modalidades permitidas pelo plano. Aulas particulares continuam com escolha de profissional.
- Sem escolha, a conta pode ser criada e a modalidade fica pendente. Nenhuma vaga é reservada para essa modalidade. Esse comportamento preserva o cadastro sem vínculo anteriormente disponível; a quantidade e obrigatoriedade foram apresentadas ao usuário para eventual ajuste.
- A idade é validada contra os limites cadastrados pela academia. Limites vazios não são preenchidos por suposição, e o formulário orienta confirmar a adequação. As faixas reais ainda precisam ser informadas pela academia. Menores exigem responsável legal.
- Conta e todos os vínculos são gravados em uma transação. IDs inválidos, turma indisponível, modalidade incompatível, idade/dia incompatível ou última vaga ocupada desfazem toda a gravação. As turmas são bloqueadas em ordem de ID durante a disputa de vagas.
- O painel identifica matrícula, preferência e escolhas pendentes. O calendário semanal marca as escolhas; a agenda pessoal identifica preferências como provisórias, sem reserva. A agenda dos planos fixos respeita os dias contratados e acompanha alterações da grade.
- Check-in continua separado da escolha. Créditos são por modalidade e por ocorrência; duas aulas no mesmo dia contam separadamente. Monitor/instrutor continuam responsáveis pela confirmação.
- O aceite permanece explícito depois de entrar: 60 horas desde novos cadastros; contas antigas pendentes não recebem prazo retroativo. Nenhum aceite ou vínculo é criado automaticamente para contas antigas.

## Migração e reversão

A mudança de esquema cria somente `class_preference`, com chaves estrangeiras e unicidade por aluno/turma. Não há migração de preferências, matrículas ou preços antigos.

Backup e operações desta entrega: `/data/bjsports-releases/20260914-cadastro-integrado-r2`. A pasta fica fora da árvore de backups antigos, encontrada incompleta na retomada. As pastas antigas não são consideradas recuperação disponível nesta entrega.

A revisão r2 preserva também a rota `/agorasim`, o template de orientação e suas imagens, adicionados em paralelo na fonte e no contêiner. A primeira tentativa de ativação foi interrompida pela proteção de divergência antes de parar o serviço. A imagem de recuperação da revisão r2 captura o estado efetivo do contêiner.

A reversão repõe somente os arquivos deste pacote e a imagem anterior. A tabela aditiva pode permanecer; não se restaura o banco sobre novos registros. O script recusa reversão automática se detectar uma publicação ou edição posterior. Os arquivos privados de banco, ambiente e imagens não fazem parte deste documento nem do Git.

## Evidências e estado

Entrega publicada em 14/09/2026 às 17h44 (America/Recife). As cinco etapas estão concluídas. Resultados de publicação, restauração, suíte e navegador em [validacao.json](validacao.json), e os nove arquivos alterados em [manifesto.json](manifesto.json). Capturas locais usam somente dados sintéticos. Evidência de HTTP, hash ou migração não substitui a conferência autenticada no navegador.

Procedimento operacional público: `/catracadoc#cadastro-turmas`. Os testes físicos de ESP32/relé/OTA continuam pendentes e não fazem parte desta entrega.


## Encerramento das cinco etapas

1. Grade real: seleção e resumo publicados, com 15 turmas públicas na conferência.
2. Persistência: preferências e matrículas atômicas; concorrência pela última vaga testada no PostgreSQL. Os bloqueios preservam a data de edição das turmas.
3. Portal: painel, calendário, agenda pessoal e check-in integrados.
4. Validação: 126 testes SQLite, 127 testes na primeira revisão PostgreSQL; na base atualizada, 126 passaram e um teste temporal foi corrigido e revalidado com outros três. A correção final passou em 28 testes PostgreSQL. Seis cadastros locais completos e oito verificações de catálogo; cinco fluxos publicados com adulto, menor e combo.
5. Publicação: backup restaurado, cópia privada fora da VPS conferida, cinco fluxos públicos aprovados e sete contas técnicas removidas. As 22 tabelas ficaram idênticas ao snapshot anterior; 23 contas existentes preservadas.

O backup imediatamente anterior à correção final está em `lockfix/database.dump` e `lockfix/volume.tar.gz`; ambos foram restaurados e conferidos. Para reverter somente a correção de datas, use `lockfix/rollback.sh`. Para reverter a entrega completa, primeiro reverta essa correção e depois execute `rollback.sh` na raiz da pasta de recuperação. Os scripts conferem imagem e hashes antes de agir, preservam o banco e recusam alterações posteriores.

A pasta de recuperação também contém a imagem anterior completa e o pacote `release.tar.gz`, necessários para reconstruir a versão intermediária. As etapas e falhas corrigidas permanecem registradas em `validacao.json`; os testes físicos de hardware e o novo contrato em massa continuam fora desta entrega.
