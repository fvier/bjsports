# Etapa 7/12 — Faixas etárias e correção da publicação

Publicado em **13/09/2026 às 22h36, America/Recife** (14/09 às 01h36 UTC). Os campos opcionais de idade estão disponíveis em **Turmas e planos**. A etapa 7/12 ainda depende das faixas reais e das regras de escolha da academia; a seleção de turmas no cadastro permanece pendente.

**Atualização posterior:** a consulta de horários no cadastro foi publicada às 23h13. O backup e o manifesto vigentes estão no [relatório de 8/12](../cadastro-horarios-2026-09-13/README.md). Os dados abaixo registram a entrega de 22h36.

## Comportamento publicado

- O editor e os detalhes da turma mostram idade mínima e máxima, em anos completos. Limites vazios significam **não definido**. É possível informar somente um dos limites.
- O servidor e o banco recusam intervalos invertidos e valores fora dos limites de entrada. A entrada aceita inteiros de 0 a 150; isso é uma validação do campo, não uma faixa atribuída às turmas.
- Kids não recebe faixa automática. Nenhuma turma existente teve idade preenchida, nenhuma matrícula foi criada para alunos reais e a regra de responsável de menores continua separada.
- Um formulário antigo que omite os novos campos preserva as idades existentes. Apagar explicitamente os campos limpa os limites. Erros conservam o formulário para correção.
- No celular, o modal fica acima do menu inferior, permitindo tocar em Salvar. Os campos receberam altura de toque e texto legíveis. O problema de sobreposição foi reproduzido no navegador antes da correção.
- Esta entrega armazena a configuração. A validação de idade na futura escolha de turma do cadastro e seus efeitos no check-in ainda não foram implementados.

Código: [modelo e migração](../../app.py), [validação de entrada](../../registration_rules.py), [editor](../../templates/gestao_turmas.html), [detalhes](../../templates/gestao_turma_detalhes.html), [JavaScript](../../static/js/main.js) e [estilos](../../static/css/turmas_planos.css). Casos de regressão em [test_class_ages.py](../../tests/test_class_ages.py) e [ensaio de navegador](../../tests/ui/class_ages.py).

## Divergência corrigida na VPS

Ao retomar o trabalho, a imagem ativa era diferente da primeira publicação validada. O backend coincidia com o código local mais recente, incluindo os campos de idade, mas faltavam templates, estilos e arquivos de firmware correspondentes. `/catracadoc` respondia **500** por ausência de seu template. A causa da troca de versão não foi determinada.

Foi preservado o estado corrente e construída a imagem sobre essa base, acrescentando o pacote completo. Isso manteve as alterações atuais de outras áreas, configurações, uploads e as **22 contas** existentes. O pacote contém 27 arquivos e a remoção de `templates/planos_admin.html`; os favoritos antigos continuam redirecionando pela aplicação.

O [manifesto](manifesto-publicacao.json) foi conferido diretamente na fonte da VPS e no contêiner publicado: **28 itens, nenhuma divergência**. A imagem ativa passou a ser `sha256:5c9465f44ad38ce1a5926def038991b495816dccba27993dbe65f98a1dc3182c`. `/catracadoc` voltou a responder 200 no HTTPS público.

## Validações

| Ambiente | Evidência |
| --- | --- |
| SQLite descartável | Suíte intermediária: 104 testes em 58,780 s. Após o último ajuste, os 7 testes de idade passaram em 4,043 s. Migração legada inicializada duas vezes: 21 tabelas preservadas e intervalo invertido recusado. |
| PostgreSQL descartável, pacote final | **105 testes aprovados em 120,170 s**, incluindo o novo caso de preservação das idades ao dividir o horário legado. |
| Clone privado do PostgreSQL atual | Inicialização preservou as 21 tabelas e 22 contas. Para ensaiar a migração legada, as colunas de idade foram retiradas somente desse clone; duas inicializações as recriaram sem alterar os registros anteriores. |
| Chrome local, dados técnicos | 6 verificações do editor: intervalo inválido, correção, salvar, recarregar, limpar e temas claro/escuro em 390/1440 px. |
| Chrome no HTTPS publicado | 10 verificações públicas, 7 fluxos de cadastro/contrato/login/check-in, 6 verificações do editor de idades, 12 da gestão e 44 de navegação por perfil. Sem erros JavaScript ou rolagem horizontal nas verificações concluídas. |
| Produção após limpeza | 21 tabelas com registros idênticos ao snapshot anterior aos testes; 22 contas, zero usuários/turmas técnicos, duas restrições de idade presentes e nenhuma faixa atribuída a turma real. |

A conferência de navegação inicialmente leu o arquivo local de configuração errado e parou antes do login autenticado. O caminho do teste foi corrigido; somente os três perfis técnicos foram recriados para repetir essa leitura. A limpeza da primeira rodada já havia removido seis contas, uma turma não publicada, uma matrícula, quatro presenças e três aceites. A segunda rodada removeu os três perfis e não criou presenças, matrículas ou aceites.

Existe uma conta real com prazo de contrato neste snapshot. Ela já estava presente antes desta publicação e foi preservada; a comparação das tabelas confirma que nenhum prazo foi aplicado retroativamente pela entrega.

Os testes de navegador são emulação no Chrome. Não comprovam funcionamento em aparelhos físicos Android/iOS nem botão, relé ou OTA do ESP32.

## Backup e reversão

Backup vigente e privado: `/data/bjsports/backups/20260913-age-rehearsal`.

- `current-source.tar.gz`, `database-current.dump`, `current-volume.tar.gz` e `current-image.tar.gz`: integridade conferida por SHA-256; 19 arquivos anteriores do pacote e três arquivos de volume restaurados em diretório privado. A imagem anterior também foi carregada novamente do arquivo de backup.
- O dump corrente foi restaurado em PostgreSQL isolado. `database-final-before-activation.dump`, feito com a aplicação parada imediatamente antes da ativação, foi restaurado em outro banco isolado e reproduziu os registros das 21 tabelas.
- `rollback.sh` restaura somente os arquivos do pacote e a imagem anterior. Não restaura automaticamente o banco nem apaga contas posteriores; recusa sobrescrever alterações fora do pacote. A versão anterior salva representa exatamente o estado encontrado, inclusive sua inconsistência em `/catracadoc`.
- A pasta da primeira publicação, `/data/bjsports/backups/20260913-turmas-planos`, foi encontrada incompleta nesta retomada. Os resultados antigos continuam como histórico, mas **essa pasta não deve ser usada como backup disponível**. Utilizar o backup vigente acima.

O contêiner, volume anônimo e rede interna do ensaio foram removidos após a comparação final, mantendo os arquivos de backup e a produção. Scripts operacionais e credenciais de testes permanecem em diretórios privados, fora do repositório.

## Conferência reproduzível do pacote

Usar [verify_release_manifest.py](../../scripts/verify_release_manifest.py) antes de ativar e diretamente no contêiner após a ativação. O verificador não importa a aplicação nem abre o banco; falha se faltar um arquivo, divergir seu SHA-256 ou reaparecer uma tela marcada como removida.

Na raiz do projeto:

```sh
venv/bin/python scripts/verify_release_manifest.py . docs/faixas-etarias-2026-09-13/manifesto-publicacao.json
```

No contêiner, copiar o verificador e o manifesto para um diretório temporário e executar com `/app` como raiz. A conferência do disco de origem, sozinha, não comprova o conteúdo da imagem ativa. Este é um controle manual documentado; ainda não foi integrado automaticamente ao processo de build.

## Decisões necessárias para o cadastro

A [leitura da grade pública](grade-publica.json) identificou 15 turmas, todas sem faixas definidas, com vínculos para unidades ativas. Há três turmas Kids: Jiu-Jitsu Kids 1, Jiu-Jitsu Kids 2 e Muay Thai Kids. É necessário informar suas idades e as das turmas Adulto, incluindo exceções por turma.

A turma **Jiu-Jitsu | São Jose Piranhas** está vinculada a **Cajazeiras (Sede Matriz)**. O nome sugere uma divergência, mas não comprova a unidade correta. O vínculo foi preservado para conferência da academia.

Também estão pendentes a quantidade de escolhas por modalidade e a regra para concluir cadastro quando não houver turma compatível disponível. Créditos continuam separados por modalidade e por ocorrência; preferência não será transformada em matrícula com reserva de vaga. Não se atribuirão turmas aos alunos antigos por suposição.

As etapas 8–12/12 permanecem pendentes no [plano de execução](../plano-execucao-2026-09-13.md).

## Evidências sanitizadas

- [Verificações finais da VPS](verificacao-final.json), [migração SQLite](migracao-sqlite.json) e [manifesto publicado](manifesto-publicacao.json).
- [Editor local](navegador-idades-local.json), [editor publicado](navegador-idades-producao.json), [gestão publicada](navegador-gestao-producao.json), [páginas públicas](navegador-publico-producao.json) e [fluxos publicados](fluxos-producao.json).
- [Navegação por perfil](navegacao-producao.json), [limpeza dos fluxos](limpeza-fluxos-producao.json), [limpeza da repetição de navegação](limpeza-navegacao-producao.json) e [limpeza do ensaio PostgreSQL](limpeza-ensaio.json).
