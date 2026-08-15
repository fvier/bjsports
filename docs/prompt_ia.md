# 🤖 Contexto Permanente para Assistentes de IA

Olá, assistente virtual! Se você está lendo isso, seja muito bem-vindo à nossa base de código. Este arquivo centraliza todas as regras arquiteturais, de estilo e diretrizes da equipe DevOps que devem ser utilizadas para interagir com o repositório **Receitas**. Consulte este conteúdo como sua base de verdade.

## Identidade do Repositório

- **Organização:** dxcdc
- **Repositório:** Receitas
- **Branch Principal:** main
- **Propósito:** Armazenar scripts reutilizáveis, prompts estruturados, boilerplates para APIs e configurações de infraestrutura que aceleram a vida do time DevOps do BJ Sports.

## Convenções Obrigatórias

- **Idioma Padrão:** Toda a documentação e artefatos de texto em geral precisam ser escritos em **Português do Brasil (pt-BR)**. Código-fonte, nomes de variáveis e comentários curtos em código podem utilizar mistura de pt-BR e Inglês.
- **Tom de Voz (Hybrid Model):**
  - Use um tom empático, amigável e focado em contexto nas seções de *introdução* (explique o "porquê").
  - Use listas numeradas, objetividade máxima e negrito em botões/tabelas em procedimentos de *passo a passo*.
- **Commits:** Adote sempre o padrão Conventional Commits (ex: `feat: add postmortem doc`, `fix: rclone script`).
- **Regra de Alimentação Incremental:** Em tabelas e listas (como logs, postmortems, troubleshooting), insira novos dados **sempre no topo**. Nenhuma entrada antiga deve ser apagada.

## Estrutura de Referência

O repositório é moldado com a premissa de facilitar o reuso:
- `/docs/` - Documentação oficial (onde este arquivo reside).
- *(Em breve outras categorias como scripts, IaC, CI/CD, etc).*

## Documentos-Chave

Sempre faça referência a esses arquivos quando o tema principal for abordado:
- [postmortem.md](./postmortem.md): Histórico e aprendizado de incidentes operacionais.
- [troubleshooting.md](./troubleshooting.md): Dicas rápidas e FAQ sobre erros do dia a dia (Git, Python, Infra).
- [politica_backup.md](./politica_backup.md): A arquitetura 3-2-1 usando ferramentas como o `rclone`.
- [plano_personalizacao.md](./plano_personalizacao.md): Como o repositório planeja evoluir pelas próximas Fases e regras de contribuição.
- [diretrizes_documentacao.md](./diretrizes_documentacao.md): Onde habitam os Architectural Decision Records (ADRs).

## Regras de Segurança

> [!CAUTION]
> **NUNCA** exponha senhas, tokens de APIs, chaves SSH, webhooks do Mattermost/Slack ou dados reais na documentação, logs de commit ou código-fonte.
- Utilize SEMPRE placeholders auto-explicativos: `<MATTERMOST_WEBHOOK_URL>`, `<GEMINI_API_KEY>`, `<AWS_SECRET_KEY>`.
- Prefira injetar valores usando variáveis de ambiente (ex: `os.getenv('MINHA_VAR')`).

## Tom de Voz (Resumo)
- Seja corporativo, mas leve.
- Entregue o contexto e abrace o desenvolvedor/operador.
- Na hora do código e das instruções práticas, seja incisivo, direto ao ponto e otimizado para a leitura rápida ("scannability").

## ADRs Vigentes

Sempre consulte o documento `diretrizes_documentacao.md` para checar os Architectural Decision Records em vigência. Se for propor uma alteração profunda na arquitetura ou ferramental do projeto, gere um novo ADR lá, não aqui.
