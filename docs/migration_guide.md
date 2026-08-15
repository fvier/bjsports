# 🚀 Guia de Migração & Onboarding

Bem-vindo(a) ao repositório de **Receitas**! Estamos muito felizes em ter você conosco. 

Este guia foi criado para garantir que seus primeiros passos sejam fluidos e livres de frustrações. Aqui você aprenderá como configurar seu ambiente local, clonar o projeto e ficar pronto para executar e contribuir com as nossas receitas de infraestrutura e automação.

---

## 1. Pré-requisitos

Antes de iniciar, certifique-se de ter as seguintes ferramentas instaladas em sua máquina:

1. **Git**: Para controle de versão e clone do repositório.
2. **Python 3.8+**: Utilizado na maioria das nossas automações e boilerplates.
3. **Node.js** *(Opcional)*: Caso pretenda trabalhar com as receitas de frontend/JS.
4. **rclone** *(Opcional)*: Para receitas focadas em backup e sincronização.
5. **GitHub CLI (`gh`)**: Recomendado para interagir com issues e PRs via terminal.

---

## 2. Clonagem do Repositório

Abra seu terminal e execute os comandos abaixo, passo a passo:

```bash
# 1. Navegue até a pasta onde deseja guardar seus projetos
cd ~/Documentos/Code/

# 2. Clone o repositório
git clone https://github.com/dxcdc/Receitas.git

# 3. Acesse a pasta do projeto
cd Receitas
```

---

## 3. Configuração do Ambiente Local

Para que as receitas funcionem corretamente, frequentemente precisaremos definir variáveis de ambiente.

1. **Crie seu arquivo de ambiente local**:
   Muitas pastas (como `api/`) possuem arquivos `.env.example`. Copie-os para criar seu `.env` local.
   
   ```bash
   cp api/.env.example api/.env
   ```

2. **Preencha as variáveis**:
   Abra o arquivo `api/.env` criado e substitua os placeholders pelas chaves reais de desenvolvimento. 
   *(Lembre-se da nossa regra de ouro: arquivos `.env` nunca devem ser commitados e já estão no nosso `.gitignore`.)*

3. **Instale as dependências (Python)**:
   Se for testar alguma receita Python, crie um ambiente virtual e instale as bibliotecas:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r api/requirements.txt
   ```

---

## 4. Configuração do Git

Para uma experiência alinhada com as práticas da equipe, configure as seguintes preferências no seu Git local:

### Identidade do Usuário
Garante que seus commits estarão vinculados corretamente à sua conta:
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@empresa.com"
```

### Alias de Histórico (Git Graph)
Crie o alias recomendado para visualizar a evolução das branches via terminal:
```bash
git config --global alias.graph "log --graph --oneline --all --decorate"
```
*Agora, você pode simplesmente digitar `git graph` no terminal para ver o histórico visual!*

### Extensões Recomendadas (VS Code)
Se você utiliza o VS Code ou Antigravity, instale as extensões:
- **Git Graph** (`mhutchie.git-graph`): Para visualizar o fluxo e integrar visualmente as branches.
- **Markdown Preview Mermaid Support**: Para renderizar nossos diagramas Mermaid localmente.

---

## 5. Verificação Pós-Instalação

Vamos garantir que tudo correu bem? Siga este checklist:

- [ ] Consigo rodar `git graph` sem erros.
- [ ] O repositório está clonado e estou na branch `main` (`git status`).
- [ ] Meu `.env` foi criado e configurado (verifique se ele **não** aparece no `git status`).
- [ ] Se uso Python, meu ambiente virtual (`venv`) ativa corretamente.

---

## 6. Próximos Passos

Agora que você está com o ambiente preparado, recomendamos que você dê uma olhada em:
- [Diretrizes de Documentação](diretrizes_documentacao.md): Entenda nossos padrões e regras de segurança.
- [Estratégia de Execução](estrategia_execucao.md): Saiba como criar branches e enviar contribuições.
- [Ajuda de Infra](ajuda_infra.md): Descubra os comandos rápidos e onde encontrar o que precisa.

**Bom trabalho e boas contribuições!**
