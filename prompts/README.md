# 💬 Prompts de Sistema & Meta-Prompts

Esta pasta contém os prompts de sistema, meta-prompts e templates de instrução utilizados pela equipe para interações com assistentes de IA, automações e pipelines de geração de conteúdo. Nosso objetivo é centralizar as melhores práticas de engenharia de prompts, garantindo consistência, previsibilidade e alto desempenho em todas as nossas integrações com modelos de linguagem.

---

## 📂 Estrutura

```
prompts/
├── README.md
├── sistema/           # Prompts de sistema para assistentes de IA
├── meta/              # Meta-prompts para geração de prompts
└── templates/         # Templates reutilizáveis de instrução
```

---

## 🚀 Como Usar

Siga o passo a passo abaixo para localizar e utilizar os prompts em seus fluxos de trabalho:

1. **Localize o prompt adequado**: Navegue pelas subpastas (`sistema/`, `meta/` ou `templates/`) e selecione o arquivo correspondente ao seu caso de uso.
2. **Copie o conteúdo**: Copie o texto base do arquivo para a sua aplicação, pipeline ou interface do assistente de IA.
3. **Adapte as variáveis e placeholders**: Substitua os placeholders contextuais (como `<CONTEXTO>`, `<ENTRADA>`, `<INSTRUCOES>`) pelas informações reais do seu cenário antes da execução.

---

## ➕ Como Contribuir

Novas contribuições mantêm nossa base sempre atualizada e eficiente. Ao adicionar novos prompts, siga estas diretrizes:

- **Nomenclatura descritiva**: Use nomes de arquivos claros e explicativos em minúsculas com hífens ou underlines (ex.: `resumo-reuniao.md`, `classificador_leads.md`).
- **Cabeçalho de identificação**: Inclua no topo do arquivo um bloco de comentários contendo:
  - **Objetivo / Propósito**: O que o prompt faz e qual problema resolve.
  - **Autor**: Nome ou identificador do criador.
  - **Data**: Data de criação ou última atualização.
- **Uso de placeholders**: Utilize placeholders explícitos (ex.: `<API_KEY>`, `<VARIAVEL>`) para quaisquer dados dinâmicos ou confidenciais.
- **Tom de voz híbrido**: Siga o padrão de escrita e tom de voz estabelecido em `docs/diretrizes_documentacao.md` (introduções empáticas e procedimentos diretos/objetivos).

---

## 🔐 Segurança

> [!IMPORTANT]
> **Nunca inclua chaves de API, credenciais ou tokens reais nos arquivos de prompt.**

- Utilize sempre placeholders explícitos (ex.: `<GEMINI_API_KEY>`, `<MATTERMOST_WEBHOOK_URL>`) ou configure a injeção dessas variáveis via ambiente no momento da execução.
- Revise minuciosamente os arquivos antes de realizar `git commit` e `git push` para evitar vazamentos acidentais no histórico de versão.
