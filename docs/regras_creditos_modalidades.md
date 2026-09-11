# Mensalidades e créditos por modalidade

Implementação local de 11/09/2026 para planos individuais de jiu-jitsu, boxe e muay thai. Cada contratação cobre somente a sua modalidade. MMA e contratos especiais existentes não recebem esta regra.

| Frequência | Mensalidade por modalidade |
| --- | --- |
| 2 aulas por semana | R$ 90 |
| 3 aulas por semana | R$ 100 |
| Ilimitado | R$ 120 |

## Funcionamento

- Horários flexíveis dentro da modalidade, respeitando a disponibilidade da turma.
- Cada ocorrência é identificada por aluno, data, turma e horário. Duas aulas no mesmo dia são dois registros e dois créditos.
- Os créditos são liberados em blocos de sete dias, começando no início do período da mensalidade (ou no cadastro, quando posterior). O último bloco pode ser menor que sete dias, mas recebe a mesma quantidade semanal.
- Créditos acumulam somente dentro do período e expiram na data do próximo vencimento, sem transferência entre modalidades.
- Um check-in pendente reserva um crédito. A confirmação mantém o consumo; a rejeição libera o crédito. Reenvio da mesma ocorrência não gera outro consumo.
- O período e a frequência ficam persistidos no primeiro check-in aceito. Alterações posteriores de vencimento ou frequência não reiniciam esse saldo; valem para o próximo período. Troca de modalidade não transfere créditos.
- O ilimitado também exige identificar cada aula, sem limite de créditos.
- A liberação financeira existente continua sendo verificada antes do check-in.

## Catálogo, histórico e ativação

A inicialização executa uma migração única dos preços do catálogo e converte a chave diária das presenças para uma chave por ocorrência. Os campos internos `ter-qui`, `seg-qua-sex` e `todos` continuam compatíveis com os formulários antigos; para estas três modalidades, representam 2 aulas, 3 aulas e ilimitado.

Os valores de faturas e textos dos contratos já registrados não são reescritos. Novas contratações e alterações administrativas usam o catálogo atualizado. Contratos antigos com frequência explícita são reconhecidos. Cadastros sem frequência identificável precisam ter o plano definido; não se presume uma quantidade de aulas pelo preço antigo. Os seis cadastros antigos de boxe sem frequência foram migrados, com autorização do responsável, para três aulas semanais por R$ 100. Essa associação é feita uma única vez, sem alterar faturas históricas.

A aplicação ainda possui um plano principal por aluno. Esta alteração não acrescenta uma interface para manter várias mensalidades individuais simultâneas no mesmo cadastro.

Antes da publicação, guardar backup do banco e a revisão anterior. A migração SQLite reconstrói apenas a tabela de presenças em transação, preservando IDs e histórico. PostgreSQL usa alteração da restrição e bloqueio entre inicializações concorrentes. Após registrar múltiplas aulas diárias, restaurar o esquema antigo exige restaurar também o backup correspondente.

## Validação local

- 13 testes específicos: limites, duas aulas no dia, duplicidade, confirmação, rejeição, reposição, expiração, modalidade, ilimitado, lotação, inadimplência, mudança de vencimento e migrações.
- Migração ensaiada em cópia isolada da base local: 51 presenças preservadas, três linhas do catálogo atualizadas e integridade SQLite aprovada.
- Suíte final: 78 testes, 75 aprovados e três falhas preexistentes: dois testes de texto/consentimento no cadastro e um de navegação por perfil. Confirmadas executando a revisão original em diretório isolado.
- Migração aplicada e conferida na base local: seis contratos de boxe atualizados, 51 presenças preservadas e faturas existentes intactas. Backup: `instance/backups/credits-20260911-003139/before.db`. VPS não alterada. Sem validação visual autenticada ou execução da migração em PostgreSQL nesta etapa.
