# 🔌 Boilerplates de Integração de APIs

Esta pasta reúne boilerplates e receitas prontas para integração com APIs externas. Cada receita é projetada para ser copiada e adaptada com mínimo esforço de configuração, fornecendo uma base sólida de código testado e padronizado para as necessidades do time de desenvolvimento e operações.

---

## 📂 Estrutura

```
api/
├── README.md
├── python/            # Integrações em Python (requests, httpx)
├── javascript/        # Integrações em JavaScript/Node.js (fetch, axios)
└── webhooks/          # Templates de webhooks (Mattermost, Slack, Discord)
```

---

## 🚀 Como Usar

Para integrar rapidamente uma nova API ao seu serviço ou script, adote o fluxo de trabalho **copiar-colar-adaptar**:

1. **Escolha o boilerplate**: Navegue até o diretório correspondente à sua stack (`python/`, `javascript/` ou `webhooks/`) e selecione a receita necessária.
2. **Copie o arquivo para o seu projeto**: Transfira o código ou módulo para o repositório ou pasta do seu serviço.
3. **Configure as variáveis de ambiente**: Crie ou atualize seu arquivo `.env` com as credenciais necessárias e ajuste os parâmetros específicos da sua chamada.

---

## 📋 Receitas Disponíveis

| Receita | Linguagem | API | Descrição |
| :--- | :--- | :--- | :--- |
| _Em breve_ | — | — | — |

---

## 🔐 Segurança

> [!CAUTION]
> **Nunca comite chaves de autenticação, segredos ou tokens de API diretamente no código-fonte.**

- **Variáveis de Ambiente**: Utilize sempre leituras seguras de ambiente (ex.: `os.getenv("API_KEY")` em Python ou `process.env.API_KEY` em Node.js).
- **Placeholders**: Ao documentar ou exemplificar nos arquivos do repositório, utilize placeholders explícitos (ex.: `<API_TOKEN>`, `<MATTERMOST_WEBHOOK_URL>`).
- **Arquivos `.env`**: Mantenha arquivos `.env` e credenciais locais explicitamente ignorados no `.gitignore`.

---

## ➕ Como Contribuir

Para adicionar uma nova receita ou aprimorar uma existente, siga estas diretrizes:

- **Modularidade e Clareza**: Escreva códigos limpos, autocontidos e devidamente comentados, facilitando a reutilização imediata.
- **Tratamento de Erros**: Inclua blocos de tratamento de exceções (try/catch, retry policies, timeouts explícitos).
- **Documentação da Receita**: Adicione um cabeçalho explicando o propósito da integração, bibliotecas necessárias (`requirements.txt` / `package.json`) e exemplos de payload.
- **Atualização da Tabela**: Ao criar uma nova receita, registre-a na seção [📋 Receitas Disponíveis](#-receitas-disponíveis) deste README.
- **Padrão de Tom**: Consulte `docs/diretrizes_documentacao.md` para manter a consistência de tom corporativo-amigável.
