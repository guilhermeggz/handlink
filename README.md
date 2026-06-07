# HandyLink

HandyLink é uma plataforma web MVP para conectar clientes a trabalhadores manuais.

O usuário pode acessar a aplicação, escolher uma categoria de serviço, visualizar trabalhadores disponíveis e solicitar atendimento.

## Tecnologias

- Python
- Flask
- Jinja2
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Bulma CSS
- SQLite
- PyTest

## Funcionalidades do MVP

- Login de cliente
- Home Page com categorias de serviço
- Perfil simples do cliente
- Listagem de serviços por categoria
- Detalhe de serviço/trabalhador
- Solicitação de serviço com data
- Logout
- Testes automatizados principais

## Estrutura esperada

```txt
handylink/
├── ext/
├── models/
├── views/
├── forms/
├── templates/
└── static/
```

## Como rodar

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

Ative no Linux/macOS:

```bash
source .venv/bin/activate
```

Instale o projeto/dependências:

```bash
pip install -e .
```

Configure variáveis de ambiente, se necessário:

```bash
set FLASK_APP=app.py
set FLASK_DEBUG=1
set DATABASE_URL=sqlite:///app.db
```

No Linux/macOS:

```bash
export FLASK_APP=app.py
export FLASK_DEBUG=1
export DATABASE_URL=sqlite:///app.db
```

Execute:

```bash
flask run
```

## Como rodar testes

```bash
pytest
```

## Documentação de apoio

- `docs/SDD.md`
- `docs/resumo-praticas-professor.md`
- `AGENTS.md`
