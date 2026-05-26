from invoke import task
from datetime import datetime
from dotenv import load_dotenv
import os
import zipfile


# ==========================================================
# GERENCIAMENTO DE AMBIENTE
# ==========================================================
def load_env(env: str):
    """
    Carrega o arquivo .env correspondente ao ambiente.
    Ex: dev, test, prod
    """
    env_file = f".env.{env}"

    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Erro Crítico: O arquivo de ambiente '{env_file}' não foi encontrado.")

    # Usamos o load_dotenv apenas para validar e ler dentro do script se necessário
    load_dotenv(env_file, override=True)
    print(f"[ENV] Ambiente '{env.upper()}' carregado com sucesso a partir de: {env_file}")


# ==========================================================
# INSTALACAO
# ==========================================================
@task
def install(c, dev=True):
    """
    Instala o projeto.
    """
    if dev:
        c.run('pip install -e ".[dev,test]"', echo=True)
    else:
        c.run("pip install .", echo=True)


@task
def uninstall(c):
    """
    Remove o pacote instalado.
    """
    c.run("pip uninstall -y handlink", echo=True)


# ==========================================================
# EXECUCAO
# ==========================================================
@task(help={"seed": "Executa o script de população do banco antes de iniciar (padrão: False)"})
def run(c, seed=False):
    """
    Executa a aplicação Flask forçando as variáveis no terminal.
    Uso: invoke run
    """
    load_env("dev")
    
    if seed:
        print("[SEED] Populando o banco de dados...")
        c.run("python seed.py", echo=True)
        
    print("[RUN] Iniciando o servidor de desenvolvimento...")
    
    # ESTRATÉGIA COMPATÍVEL COM WINDOWS/LINUX:
    # Em vez de confiar no os.environ passar magicamente, nós pegamos os valores atuais
    # que o load_dotenv acabou de ler e montamos um dicionário limpo.
    
    # Buscamos direto do que está na memória agora
    flask_app = os.environ.get("FLASK_APP", "app.py") # mude para "handlink" se for o caso
    flask_debug = os.environ.get("FLASK_DEBUG", "1")
    secret_key = os.environ.get("SECRET_KEY", "")

    # Criamos um ambiente customizado contendo TUDO do sistema + as variáveis atualizadas
    custom_env = dict(os.environ)
    custom_env["FLASK_APP"] = flask_app
    custom_env["FLASK_DEBUG"] = flask_debug
    custom_env["SECRET_KEY"] = secret_key

    # Se mesmo assim o Invoke falhar no Windows, a alternativa abaixo junta os comandos na mesma linha do terminal:
    # No Windows (CMD), para rodar variáveis na mesma linha usamos: set FLASK_DEBUG=1 && set SECRET_KEY=xxx && flask run
    # No Linux/Mac usamos: FLASK_DEBUG=1 SECRET_KEY=xxx flask run
    
    # Vamos usar o parâmetro env do Invoke, mas garantindo que passamos o dicionário completo populado:
    c.run("flask run", env=custom_env, echo=True)


@task
def prod(c):
    """
    Executa a aplicacao em modo producao.
    """
    load_env("prod")
    c.run("flask run")


# ==========================================================
# TESTES
# ==========================================================
@task
def test(c):
    """
    Executa os testes automatizados.
    """
    load_env("test")
    c.run("PYTHONPATH=. pytest -v")


# ==========================================================
# QUALIDADE DE CODIGO
# ==========================================================
@task
def lint(c):
    """
    Verifica qualidade de codigo.
    """
    c.run("flake8")


@task
def format(c):
    """
    Formata o codigo automaticamente.
    """
    c.run("black .")


@task
def seed_dev(c):
    """
    Executa o comando de seed garantindo o ambiente de desenvolvimento.
    """
    load_env("dev")
    os.system("flask seed-dev")


# ==========================================================
# EMPACOTAMENTO
# ==========================================================
@task
def zip(c, name=None):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    zip_filename = name or f"handlink-projeto-{timestamp}.zip"
    zip_path = os.path.abspath(os.path.join("..", zip_filename))

    print(f"→ Criando ZIP: {zip_path}")

    excludes = [
        "venv",
        "__pycache__",
        ".git",
        ".vscode",
        "handlink.egg-info"
    ]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):

            dirs[:] = [d for d in dirs if d not in excludes]

            for file in files:
                if file.endswith((".pyc", ".pyo", ".pyd", ".log", ".db", ".sqlite3")):
                    continue

                filepath = os.path.join(root, file)
                zipf.write(filepath)

    if os.path.exists(zip_path):
        size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"→ ZIP criado com sucesso: {zip_path}")
        print(f"   Tamanho: {size_mb:.2f} MB")