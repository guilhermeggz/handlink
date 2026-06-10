# HandLink

HandLink e uma aplicacao Flask para conectar clientes a profissionais que oferecem servicos residenciais, como limpeza, eletricidade, encanamento, montagem, pintura e frete.

## Requisitos

- Python 3.9 ou superior
- pip
- PowerShell, se estiver usando Windows

## Configuracao inicial

Voce pode criar o ambiente virtual automaticamente com:

```powershell
py make_env.py
```

Esse comando cria a pasta `venv`, ajusta a permissao de execucao do PowerShell e instala dependencias iniciais como `invoke` e `dotenv`.

Se preferir fazer manualmente, crie e ative o ambiente virtual:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Atualize o pip:

```powershell
python -m pip install --upgrade pip
```

Instale o projeto com as dependencias de desenvolvimento e teste:

```powershell
pip install -e ".[dev,test]"
```

O arquivo `tasks.py` usa `invoke`. Se ele nao for instalado pelo comando acima, instale manualmente:

```powershell
pip install invoke
```

## Variaveis de ambiente

Crie um arquivo `.env.dev` na raiz do projeto:

```env
FLASK_APP=app.py
FLASK_DEBUG=1
SECRET_KEY=troque-esta-chave
```

O projeto carrega o ambiente de desenvolvimento por padrao em `handlink/ext/config/__init__.py`.

## Rodando o projeto

Com o ambiente virtual ativo, rode:

```powershell
flask run
```

Ou use o Invoke:

```powershell
invoke run
```

Depois acesse:

```text
http://127.0.0.1:5000
```
