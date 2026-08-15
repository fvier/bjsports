# 🏗️ Ajuda de Infraestrutura — Arquitetura & Comandos Rápidos

Bem-vindo(a) ao guia de infraestrutura do repositório de Receitas! Este documento serve como o seu mapa e manual de referência rápida. 

Aqui você vai encontrar uma visão clara de como as nossas pastas estão organizadas, quais comandos resolvem os problemas mais comuns do dia a dia e quais variáveis de ambiente são utilizadas como padrão em nossos scripts. O objetivo é que você não precise decorar nada — apenas consulte esta página quando precisar.

---

## 1. Arquitetura do Repositório

Nossas receitas estão organizadas por contexto e domínio, garantindo que o conhecimento esteja sempre no lugar mais lógico possível.

```text
Receitas/
├── .github/                   # Automações de CI/CD, actions e workflows
├── api/                       # Boilerplates e exemplos de consumo de APIs externas
├── docs/                      # Guias de governança, estratégia e troubleshooting (aqui!)
├── infra/                     # Configurações de servidores, IaC, backups e redes
├── prompts/                   # Coletânea de meta-prompts úteis para assistentes de IA
└── README.md                  # Ponto de entrada do repositório
```

**Por que essa estrutura?**
- Manter scripts separados de textos explicativos.
- Isolar dependências (um script de infraestrutura não deve se misturar com um boilerplate de frontend).
- Facilitar buscas e refatorações no futuro.

---

## 2. Comandos Rápidos

Evite perder tempo buscando no Google. Abaixo, uma tabela com os comandos mais utilizados no nosso ecossistema:

| Ferramenta | Comando | O que faz |
| :--- | :--- | :--- |
| **Git** | `git graph` | Exibe a árvore de branches no terminal (requer configuração do alias). |
| **Git** | `git fetch --all --prune` | Sincroniza e limpa referências de branches locais deletadas remotamente. |
| **GitHub CLI** | `gh pr create --web` | Abre o navegador para criar rapidamente um Pull Request na branch atual. |
| **Python** | `python3 -m venv venv` | Cria um ambiente virtual local isolado para dependências. |
| **Python** | `pip freeze > requirements.txt`| Salva as dependências atuais no arquivo de requirements. |
| **rclone** | `rclone config` | Abre o menu de configuração interativo para conexões em nuvem. |
| **rclone** | `rclone sync local/ remoto:bucket/` | Sincroniza uma pasta local com um bucket (cuidado: apaga o destino para igualar à origem). |

---

## 3. Ferramentas Utilizadas

Nossos scripts e infraestrutura são construídos sobre um conjunto consolidado de ferramentas:

- **GitHub Actions**: Motor de CI/CD para automação de issues e verificações de estilo.
- **Python**: Linguagem padrão para automação de tarefas repetitivas e manipulação de dados em receitas `api/` e `infra/`.
- **rclone**: Canivete suíço para gerenciamento de armazenamentos em nuvem (S3, GDrive, Azure).
- **Mermaid**: Linguagem de diagramação baseada em texto, renderizada diretamente nos nossos Markdowns.

---

## 4. Variáveis de Ambiente Comuns

Para manter a segurança e a portabilidade, nossos scripts esperam as seguintes variáveis padrão.
> **Lembrete de Segurança:** Utilize sempre um arquivo `.env` ignorado pelo Git para testar localmente.

| Variável | Contexto de Uso | Exemplo Seguro (Placeholder) |
| :--- | :--- | :--- |
| `API_PORT` | Porta padrão para rodar serviços da pasta `/api` | `8080` |
| `GEMINI_API_KEY` | Chave de autenticação para scripts e prompts baseados em IA | `<SUA_CHAVE_GEMINI_AQUI>` |
| `MATTERMOST_WEBHOOK_URL`| Endpoint para envio de notificações automatizadas | `https://chat.empresa.com/hooks/<ID>` |
| `AWS_ACCESS_KEY_ID` | Identificador de acesso para scripts em `/infra` | `<SEU_AWS_ACCESS_KEY>` |

---

## 5. Links Úteis

Se você precisar de aprofundamento ou consulta direta nas fontes originais, use as referências abaixo:

- [Documentação Oficial do Git](https://git-scm.com/doc)
- [Documentação do GitHub CLI (gh)](https://cli.github.com/manual/)
- [Site Oficial e Guias do rclone](https://rclone.org/docs/)
- [Sintaxe do Mermaid.js](https://mermaid.js.org/intro/)
