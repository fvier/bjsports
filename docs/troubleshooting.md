# 🛠️ Troubleshooting — Solução de Problemas Comuns

Olá! Se você chegou até aqui, provavelmente encontrou um erro no meio do caminho. Fique tranquilo, estamos juntos nessa! Este documento é um guia vivo, construído pela equipe para registrar os problemas mais comuns que enfrentamos e como solucioná-los rapidamente. Caso você resolva um problema novo, não se esqueça de documentá-lo!

> [!IMPORTANT]
> **Regra de Alimentação Incremental:** Novas entradas devem ser inseridas sempre **no topo** de suas respectivas seções. Nunca apague registros antigos. O histórico completo é essencial para auditoria e aprendizado contínuo.

---

### Git & GitHub
<details>
  <summary><b>Problema: Permission denied on push</b></summary>
  
  **Solução:**
  1. Verifique se você está autenticado corretamente.
  2. Confirme que sua chave SSH ou Personal Access Token (PAT) tem as permissões adequadas de leitura/escrita.
  3. Você pode checar a conexão SSH com `ssh -T git@github.com`.
</details>

<details>
  <summary><b>Problema: Merge conflicts</b></summary>
  
  **Solução:**
  1. Identifique os arquivos conflitantes usando `git status`.
  2. Abra os arquivos no editor de sua preferência (VS Code, por exemplo) e resolva os blocos indicados por `<<<<<<<`, `=======` e `>>>>>>>`.
  3. Adicione os arquivos resolvidos e finalize o commit: `git add .` seguido de `git commit`.
</details>

<details>
  <summary><b>Problema: gh CLI not authenticated</b></summary>
  
  **Solução:**
  1. Execute o comando `gh auth login`.
  2. Siga as instruções interativas para autenticar via browser ou através de um token (`gh auth login --with-token`).
</details>

---

### Python / Pip
<details>
  <summary><b>Problema: ModuleNotFoundError</b></summary>
  
  **Solução:**
  1. Verifique se o módulo realmente está no `requirements.txt`.
  2. Certifique-se de que o ambiente virtual está ativo (`source venv/bin/activate`).
  3. Execute `pip install -r requirements.txt`.
</details>

<details>
  <summary><b>Problema: venv not activating</b></summary>
  
  **Solução:**
  1. Se estiver usando Bash/Zsh, certifique-se de usar `source venv/bin/activate`.
  2. No Windows (PowerShell), se houver problema de permissão, execute `Set-ExecutionPolicy Unrestricted -Scope CurrentUser` e tente rodar `.\venv\Scripts\Activate.ps1`.
</details>

---

### Infraestrutura (rclone, backup)
<details>
  <summary><b>Problema: rclone config not found</b></summary>
  
  **Solução:**
  1. O arquivo de configuração pode não estar criado. Rode `rclone config` para configurá-lo.
  2. Para validar o caminho do arquivo, use o comando `rclone config file`.
</details>

<details>
  <summary><b>Problema: Backup failing silently</b></summary>
  
  **Solução:**
  1. Cheque se os cron jobs estão gravando logs de execução. Direcione o output para um log usando `>> /caminho/backup.log 2>&1`.
  2. Adicione flags de verbosidade no rclone: `--verbose` ou `--log-level DEBUG` para identificar onde a tarefa para.
</details>

---

### Variáveis de Ambiente
<details>
  <summary><b>Problema: KeyError on os.getenv</b></summary>
  
  **Solução:**
  1. Em Python, tentar acessar uma variável inexistente em `os.environ` gera `KeyError`. Em vez disso, use sempre `os.getenv("MINHA_VAR", "padrao")` para retornar o valor padrão caso a variável não exista, ou lance uma exceção customizada caso a variável seja obrigatória.
</details>

<details>
  <summary><b>Problema: .env not loading</b></summary>
  
  **Solução:**
  1. Certifique-se de usar ferramentas como `python-dotenv` no seu script (chamando `load_dotenv()`).
  2. Confirme se o arquivo está na raiz do projeto e corretamente nomeado `.env` (sem prefixos e no mesmo local de execução do script).
</details>

---
