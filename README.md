# BJ Sports — Centro de Treinamento

Aplicação Flask para o portal de alunos e a administração de planos, mensalidades, presenças e reservas.

## Execução local

Requer Python 3.11 ou superior.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
flask --app app run --debug
```

Acesse `http://127.0.0.1:5000`. O banco padrão fica em `instance/bjsports.db` e não deve ser adicionado ao Git. Em uma instalação vazia, crie o primeiro instrutor de forma interativa:

```bash
flask --app app create-admin
```

## Papéis

- `aluno`: portal, mensalidades próprias, presença, treinoteca e perfil.
- `monitor`: permissões de aluno, confirmação de presenças e criação de aulas especiais no calendário.
- `instrutor`: todas as anteriores, gestão de planos e privilégios.

Rotas protegidas conferem sessão e papel no servidor. Formulários e APIs mutáveis exigem token CSRF.

## Banco e atualização

As tabelas principais são `user`, `plan`, `monthly_payment`, `attendance` e `booking`. Na primeira inicialização atualizada, os estados do JSON legado são copiados para competências anuais em `monthly_payment`.

Faça backup antes de atualizar uma instalação:

```bash
cp instance/bjsports.db "instance/bjsports-$(date +%Y%m%d-%H%M%S).db.backup"
```

## Testes

```bash
venv/bin/python -m unittest discover -s tests -v
venv/bin/python -m py_compile app.py
node --check static/js/main.js
```

Os testes usam SQLite em memória e não alteram o banco local.

## Calendário pessoal e notificações

O arquivo `.ics` de cada usuário inclui somente suas matrículas ativas. Para assinatura automática no Google Agenda, configure `PUBLIC_BASE_URL` com o endereço HTTPS público.

O push usa VAPID e exige `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY` e `VAPID_SUBJECT`. Depois de configurar o agendador da hospedagem, execute a cada 10 minutos:

```bash
flask --app app send-calendar-reminders --minutes-ahead 60
```

O comando evita repetir o mesmo lembrete para uma inscrição e considera somente as turmas ativas do usuário.

## Produção

Defina obrigatoriamente `SECRET_KEY`, configure `DATABASE_URL`, use HTTPS e execute atrás de um servidor WSGI. `FLASK_ENV=production` ativa cookie seguro e impede inicialização sem segredo. Não use o servidor de desenvolvimento nem `debug=True`.

O SQLite, `.env`, backups, chaves e certificados são ignorados. Versões antigas rastrearam banco e dados demonstrativos; antes de tornar o repositório público, limpe o histórico e troque credenciais expostas.
