# Etapa 8/12 — Consulta de turmas no cadastro

Publicado em **13/09/2026 às 23h13, America/Recife** (14/09 às 02h13 UTC), em [Cadastro](https://bjsports.com.br/login?mode=register). Esta entrega conclui a parte de **consulta da grade** de 8/12. A escolha persistida como preferência ou matrícula ainda depende das decisões pendentes de 7/12.

## O que o aluno pode consultar

1. Escolher **Individuais** ou **Combos e especiais** e selecionar o plano.
2. Consultar as turmas da modalidade; no combo, indicar suas modalidades para ver cada grupo de horários.
3. Filtrar unidade e período, quando aplicável, e conferir nome, público, faixa etária informada, professor, dias e horários.
4. Usar **Atualizar horários** para consultar novamente a gestão. Uma edição de horário aparece na próxima consulta, sem texto manual duplicado.

Turmas privadas, inativas e vinculadas a unidades inativas ou inexistentes ficam fora da consulta. Turmas marcadas como lotadas, com capacidade zero ou com capacidade preenchida por matrículas ativas são sinalizadas. Essa sinalização não substitui a capacidade de uma ocorrência de aula nem garante uma vaga nos planos por créditos.

Faixas não configuradas aparecem como **Faixa etária não definida**. O cadastro mostra a grade da modalidade para consulta; ainda não filtra elegibilidade por idade nem cria matrícula ou preferência. A tela explica a necessidade de confirmar a turma adequada com a academia. O contrato continua após entrar, com 60 horas para contas novas e confirmação explícita.

No celular, listas com mais de duas turmas começam recolhidas e podem ser abertas pelo toque ou teclado. Trocar de plano limpa o resultado anterior e os filtros; respostas de consultas antigas não devem substituir a modalidade atual. Falhas de carregamento apresentam mensagem e opção de atualizar, sem bloquear o formulário. Aula particular mantém a escolha específica de profissional.

O teste de navegador encontrou os botões de troca de tipo de plano ausentes, embora a lógica dos combos já existisse. Foram restaurados os controles visíveis e seus estados acessíveis. A mensagem durante envio passou de “Realizando matrícula” para “Criando conta”, coerente com o comportamento atual.

## Implementação e validação

- [app.py](../../app.py): `GET /api/cadastro/turmas`, com consulta somente de leitura e `Cache-Control: no-store`. A resposta contém exclusivamente informações da grade pública, sem dados de alunos, contatos, matrículas individuais ou financeiro.
- [login.html](../../templates/login.html), [registration_schedule.js](../../static/js/registration_schedule.js) e [interface.css](../../static/css/interface.css): consulta da grade, filtros, estados de erro/vazio, modalidades do combo e apresentação no celular.
- [test_registration_schedule.py](../../tests/test_registration_schedule.py): cinco testes de visibilidade, capacidade, campos públicos, ausência de gravações e edição na gestão refletida na próxima consulta.
- [registration_schedule.py](../../tests/ui/registration_schedule.py): oito cenários de navegador em dados sintéticos, com temas claro/escuro e larguras 390/1440 px, filtros, combos, particular, recuperação de erro e expansão por teclado.

**110 testes SQLite** passaram em 55,518 s; **110 testes PostgreSQL** passaram em 117,134 s. O clone privado preservou os registros das 21 tabelas após inicializar o candidato. O ajuste final de compactação alterou somente JavaScript; foi validado nos oito cenários locais antes de reconstruir a imagem final.

Na publicação, passaram **24 verificações no Chrome**, em 390/1440 px e claro/escuro. As turmas exibidas foram comparadas com a grade real para cada modalidade e combo; aula particular continuou acessível. Sem erros JavaScript ou rolagem horizontal nessas verificações. Esta rodada pública não criou contas, presenças, aceites, preferências ou matrículas. Os fluxos autenticados de cadastro e check-in têm evidência na [entrega imediatamente anterior](../faixas-etarias-2026-09-13/README.md); não são contados novamente como envios nesta rodada.

## Publicação e recuperação

O pacote completo tem 28 arquivos e a remoção da tela antiga de planos: **29 itens conferidos na fonte e no contêiner ativo, sem divergência**. Imagem publicada: `sha256:283d12258c64eba1bfb83d6f38c9156fb3ed5f24b25384afd18295bcced7025e`.

Somente a aplicação foi recriada. Após a publicação e as consultas do navegador, as 21 tabelas permaneciam idênticas ao snapshot anterior à ativação. Foram preservadas **23 contas**, incluindo duas que já tinham prazo de contrato antes desta entrega; não se atribuiu prazo retroativo nem faixa etária. Nenhuma conta ou turma técnica permaneceu em produção. Configurações, uploads e arquivos de outras áreas foram preservados.

Backup vigente e privado: `/data/bjsports/backups/20260914-cadastro-horarios`.

- Fonte, imagem anterior, volume e dump corrente com integridade SHA-256 conferida. Foram restaurados 27 arquivos anteriores do pacote e três arquivos do volume em diretório privado; a imagem anterior foi carregada do arquivo salvo.
- Dump corrente e dump final anterior à ativação restaurados em bancos isolados. O último reproduziu os registros das 21 tabelas.
- `rollback.sh` restaura somente os arquivos do pacote e a imagem anterior, sem restaurar automaticamente o banco nem apagar novos registros. Recusa sobrescrever arquivos alterados depois do pacote.
- O PostgreSQL de ensaio, seu volume anônimo e sua rede privada foram removidos ao encerrar a validação. O servidor sintético local também foi encerrado. Backups foram preservados.

A imagem anterior desta entrega é a versão coerente e validada de 7/12. Este backup passa a ser a referência atual de recuperação; os relatórios anteriores permanecem históricos.

Para verificar os arquivos locais do pacote, sem abrir o banco:

```sh
venv/bin/python scripts/verify_release_manifest.py . docs/cadastro-horarios-2026-09-13/manifesto-publicacao.json
```

Repetir a conferência dentro do contêiner efetivamente publicado, com `/app` como raiz. O verificador é um controle manual; não foi integrado ao build automático nesta entrega.

## Pendências para concluir a integração

Permanecem necessárias as faixas etárias reais, a quantidade de turmas/preferências por modalidade e a regra para cadastro sem turma disponível. Conferir também a unidade de “Jiu-Jitsu | São Jose Piranhas”, atualmente vinculada à sede de Cajazeiras; o nome não foi usado para mudar seu vínculo.

Depois dessas definições: habilitar a escolha e o resumo, validar elegibilidade e capacidade no servidor, salvar conta e preferência/matrícula com consistência, integrar painel/calendário/check-in e testar concorrência. As etapas 9–12/12 continuam pendentes. Não houve mudança na contagem de créditos ou migração de alunos antigos para turmas.

## Evidências

- [Testes](validacao.json), [navegador local](navegador-local.json) e [navegador publicado](navegador-producao.json).
- [Manifesto](manifesto-publicacao.json), [conferência final da VPS e preservação dos dados](verificacao-final.json) e [limpeza do ensaio](limpeza-ensaio.json).
- [Visualização publicada em celular](horarios-celular.png) e [serviços/rotas após a limpeza](saude-publicacao.json).
- [Acompanhamento das etapas](../plano-execucao-2026-09-13.md).

Artefatos operacionais privados: `/tmp/bj-schedule-20260913` e a pasta do backup. Credenciais, dumps e capturas privadas não integram este relatório.
