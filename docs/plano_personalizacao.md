# 🎨 Plano de Personalização & Expansão

Bem-vindo(a) ao roadmap do repositório de Receitas! Este espaço foi pensado não apenas para armazenar os artefatos atuais da equipe DevOps (dxcdc), mas para suportar organicamente a evolução das nossas ferramentas, processos e automações. 

Aqui estruturamos como vamos crescer.

## Roteiro de Expansão

O roteiro a seguir direciona o foco da nossa área nos próximos ciclos:

- **Fase 1: Consolidação (Atual)** - Mapeamento e unificação dos scripts existentes e consolidação de políticas básicas (Backup, Documentação, IA Context).
- **Fase 2: Novas categorias de receitas** - Introdução de boilerplates oficiais da empresa para Infra como Código (Terraform/Ansible) e novos scripts em Python / Bash.
- **Fase 3: Integração MCP Server** - Criação de endpoints Model Context Protocol para que agentes de IA possam interagir em tempo real com as ferramentas cadastradas no repositório.
- **Fase 4: Dashboard de Métricas** - Implementação de um portal unificado demonstrando o uso das ferramentas, relatórios de postmortems e status dos backups.

## Como Criar uma Nova Categoria

Sempre que a equipe necessitar de uma abordagem inédita (ex: CI/CD, Monitoramento), siga este fluxo:
1. Analise se a necessidade não se enquadra em nenhuma categoria existente.
2. Crie um novo diretório root (Ex: `monitoramento/`).
3. Adicione um `README.md` nessa nova pasta descrevendo o propósito.
4. Alimente a seção **Categorias Planejadas** abaixo se for algo para o futuro, ou altere o status para implementado.
5. Crie a sua receita com o template a seguir.

## Template de Nova Receita

Toda nova receita deve possuir um padrão claro para adoção rápida pelo time. Copie o escopo abaixo ao criar uma nova automação:

```markdown
# 🏷️ Título da Receita

## 📖 Propósito
Descreva rapidamente o problema que esse script/boilerplates resolve.

## 🛠️ Requisitos
- Ferramenta A (versão > 2.0)
- Variáveis de ambiente necessárias (Ex: `<API_KEY_PLACEHOLDER>`)

## 🚀 Passo a Passo (Uso)
1. Instale dependências: `pip install -r requirements.txt`
2. Configure o arquivo `.env`.
3. Rode: `python main.py`

## ⚠️ Pontos de Atenção
- Avisos de segurança
- Limites de chamadas (rate limits)
```

## Categorias Planejadas

As áreas que a equipe tem interesse em adotar e expandir nos próximos ciclos:

| Categoria | Descrição | Status |
|-----------|-----------|--------|
| **Monitoramento** | Receitas de agentes Zabbix, PromQL, Grafana | Pendente |
| **CI/CD** | Templates de GitHub Actions, GitLab CI | Pendente |
| **Segurança** | Automações de auditoria de IAM, checagem de vulnerabilidades | Planejado |
| **IA & MCP** | Prompts extras e bridges do Model Context Protocol | Planejado (Fase 3) |
