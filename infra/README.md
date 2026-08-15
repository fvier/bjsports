# ⚙️ Configurações de Infraestrutura

Esta pasta centraliza configurações de infraestrutura, scripts de backup, configurações de DNS, cofres de segredos e utilitários de automação da equipe. Nosso objetivo é manter a infraestrutura como código (IaC) e as rotinas operacionais documentadas, reproduzíveis e seguras em todos os ambientes.

---

## 📂 Estrutura

```
infra/
├── README.md
├── backup/            # Scripts e configurações de backup (rclone)
├── dns/               # Configurações e templates de DNS
├── cofre/             # Padrões de cofre de segredos e variáveis
└── scripts/           # Scripts utilitários de automação
```

---

## 🚀 Como Usar

Siga o procedimento padrão para executar ou provisionar recursos de infraestrutura:

1. **Selecione o recurso desejado**: Localize a pasta correspondente à necessidade operacional (`backup/`, `dns/`, `cofre/` ou `scripts/`).
2. **Revise os pré-requisitos**: Verifique as dependências necessárias (ex.: ferramentas de CLI instaladas, permissões de acesso ao provedor de nuvem).
3. **Configure as variáveis de execução**: Defina as variáveis de ambiente necessárias ou preencha os arquivos `.env` locais com base nos templates fornecidos.
4. **Execute com segurança**: Execute os scripts ou aplique as configurações inicialmente em ambiente de homologação (`staging`) antes de promover para produção.

---

## 📋 Recursos Disponíveis

| Recurso | Tipo | Descrição |
| :--- | :--- | :--- |
| _Em breve_ | — | — |

---

## 🔐 Segurança

> [!CAUTION]
> **É estritamente proibido comitar chaves privadas, certificados e arquivos de credenciais no repositório.**

- **Arquivos Sensíveis**: Nunca adicione arquivos `.pem`, `.key`, `.p12`, `.crt`, `.id_rsa` ou arquivos de credenciais gerados (ex.: `credentials.json`, `service-account.json`) ao Git.
- **Validação de Ignored Files**: Certifique-se de que esses padrões estejam devidamente contemplados no `.gitignore`.
- **Cofre de Segredos**: Para armazenamento e rotação de credenciais, utilize os padrões e integrações documentados no diretório `cofre/`.
- **Auditoria Pré-Commit**: Verifique o `git status` e `git diff` antes de submeter alterações de infraestrutura.

---

## ➕ Como Contribuir

Ao submeter novas configurações ou scripts de infraestrutura, atente-se às seguintes orientações:

- **Idempotência**: Garanta que scripts e configurações possam ser executados múltiplas vezes sem gerar inconsistências ou duplicações de recursos.
- **Parametrização**: Torne os scripts reutilizáveis por meio de parâmetros de entrada, flags de CLI ou variáveis de ambiente.
- **Documentação Clara**: Inclua comentários detalhados e um arquivo `README.md` específico na subpasta explicando escopo, variáveis requeridas e passos de rollback.
- **Atualização da Tabela**: Registre os novos utilitários na seção [📋 Recursos Disponíveis](#-recursos-disponíveis) deste documento.
- **Diretrizes Gerais**: Siga as boas práticas e o tom de voz híbrido descritos em `docs/diretrizes_documentacao.md`.
