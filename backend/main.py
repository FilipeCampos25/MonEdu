from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime
import hashlib
import os
import logging
from dotenv import load_dotenv
from funcoes import Email_sender, objeto, vincular
import psycopg2

# Carregar variáveis de ambiente
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuração do Flask
cadastro = Flask(__name__, template_folder="../frontend")
cadastro.secret_key = "herekinkajou613"

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuração do banco de dados com SQLAlchemy
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

# Função para hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para processar texto com marcações
def process_text(text):
    if not text:
        return text
    # Substituir \n literal por quebra de linha real
    text = text.replace('\\n', '\n')
    return text

# Inicialização do banco de dados
def init_db():
    try:
        with engine.connect() as conn:
            # Criar a tabela usuarios se não existir
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuarios SERIAL PRIMARY KEY,
                    nome VARCHAR(100),
                    idade INTEGER,
                    email VARCHAR(255) UNIQUE,
                    senha VARCHAR(255),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Criar tabela licao
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS licao (
                    id_licao SERIAL PRIMARY KEY,
                    titulo VARCHAR(255),
                    nivel INTEGER,
                    conteudo TEXT,
                    pontos_recompensa INTEGER
                )
            """))

            # Criar tabela perguntas
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS perguntas (
                    id_pergunta SERIAL PRIMARY KEY,
                    id_licao INTEGER,
                    enunciado TEXT,
                    resposta_correta VARCHAR(255),
                    opcoes TEXT,
                    CONSTRAINT perguntas_fk_id_licao FOREIGN KEY (id_licao) REFERENCES licao (id_licao)
                )
            """))

            # Criar tabela gamificacao com id_licao e constraint UNIQUE
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS gamificacao (
                    id_gamificacao SERIAL PRIMARY KEY,
                    id_usuario INTEGER,
                    id_licao INTEGER,
                    tipo VARCHAR(20) CHECK (tipo IN ('moeda', 'nivel')),
                    valor INTEGER,
                    data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT gamificacao_fk_id_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios),
                    CONSTRAINT gamificacao_fk_id_licao FOREIGN KEY (id_licao) REFERENCES licao (id_licao),
                    CONSTRAINT unique_usuario_licao_tipo UNIQUE (id_usuario, id_licao, tipo)
                )
            """))

            # Criar tabela progresso com constraint UNIQUE
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS progresso (
                    id_progresso SERIAL PRIMARY KEY,
                    id_usuario INTEGER,
                    id_licao INTEGER,
                    status_progresso VARCHAR(20) CHECK (status_progresso IN ('iniciado', 'concluido')),
                    pontos_ganhos INTEGER,
                    CONSTRAINT progresso_fk_id_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios),
                    CONSTRAINT progresso_fk_id_licao FOREIGN KEY (id_licao) REFERENCES licao (id_licao),
                    CONSTRAINT unique_usuario_licao UNIQUE (id_usuario, id_licao)
                )
            """))

            # Criar outras tabelas
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS topicos (
                    id SERIAL PRIMARY KEY,
                    licao_id INTEGER,
                    nome VARCHAR(100) NOT NULL,
                    ordem INTEGER NOT NULL,
                    CONSTRAINT topicos_fk_licao_id FOREIGN KEY (licao_id) REFERENCES licao (id_licao)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS subtopicos (
                    id SERIAL PRIMARY KEY,
                    topico_id INTEGER,
                    numero VARCHAR(10) NOT NULL,
                    nome VARCHAR(100) NOT NULL,
                    ordem INTEGER NOT NULL,
                    CONSTRAINT subtopicos_fk_topico_id FOREIGN KEY (topico_id) REFERENCES topicos (id) ON DELETE CASCADE
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS conteudos (
                    id SERIAL PRIMARY KEY,
                    subtopico_id INTEGER,
                    numero VARCHAR(10) NOT NULL,
                    titulo VARCHAR(200) NOT NULL,
                    texto TEXT NOT NULL,
                    ordem INTEGER NOT NULL,
                    CONSTRAINT conteudos_fk_subtopico_id FOREIGN KEY (subtopico_id) REFERENCES subtopicos (id) ON DELETE CASCADE
                )
            """))

            conn.commit()
            logging.info("Tabelas verificadas/criadas com sucesso.")
    except Exception as err:
        logging.error(f"Erro ao criar tabelas: {err}")
        raise

# Rota principal (página de cadastro/login)
@cadastro.route("/")
def index():
    return render_template("cadastro.html")

# Rota para a tela principal
@cadastro.route("/tela")
def tela():
    if "user_id" not in session:
        flash("Por favor, faça login para acessar esta página.")
        return redirect(url_for("index"))

    try:
        with engine.connect() as conn:
            # Obter dados do usuário (excluindo senha)
            query = text("""
                SELECT nome, idade, email, data_criacao 
                FROM usuarios 
                WHERE id_usuarios = :user_id
            """)
            result = conn.execute(query, {"user_id": session["user_id"]})
            user_data = result.mappings().first()
            if not user_data:
                flash("Usuário não encontrado.")
                session.pop("user_id", None)
                return redirect(url_for("index"))

            username = user_data["nome"]
            user_info = {
                "nome": user_data["nome"],
                "idade": user_data["idade"],
                "email": user_data["email"],
                "data_criacao": user_data["data_criacao"].strftime("%d/%m/%Y %H:%M:%S")
            }

            # Somar os pontos_ganhos da tabela progresso
            query = text("""
                SELECT COALESCE(SUM(pontos_ganhos), 0) AS total_pontos
                FROM progresso
                WHERE id_usuario = :user_id
            """)
            result = conn.execute(query, {"user_id": session["user_id"]})
            points_data = result.mappings().first()
            points = points_data["total_pontos"]

            # Obter tópicos e subtemas
            query = text("SELECT id, nome FROM topicos ORDER BY ordem")
            result = conn.execute(query)
            topicos = result.mappings().all()

            secoes = []
            for topico in topicos:
                query = text("""
                    SELECT id, numero, nome
                    FROM subtopicos
                    WHERE topico_id = :topico_id
                    ORDER BY ordem
                """)
                result = conn.execute(query, {"topico_id": topico["id"]})
                subtopicos = result.mappings().all()
                secoes.append(
                    {
                        "id": topico["id"],
                        "nome": topico["nome"],
                        "subtopicos": subtopicos,
                    }
                )

            return render_template(
                "telaPrincipal.html", 
                username=username, 
                points=points, 
                secoes=secoes,
                user_info=user_info
            )
    except Exception as e:
        flash(f"Erro ao carregar a tela principal: {e}")
        return redirect(url_for("index"))

# Rota para a tela de conteúdo
@cadastro.route("/contentScreen.html")
def content_screen():
    return render_template("contentScreen.html")

# Rota para processar login e cadastro
@cadastro.route("/submit", methods=["POST"])
def submit():
    try:
        with engine.connect() as conn:
            if "confirm_password" not in request.form:
                # Login
                username = request.form.get("username")
                password = request.form.get("password")
                if not username or not password:
                    flash("Preencha todos os campos de login.")
                    return redirect(url_for("index"))

                password_hash = hash_password(password)

                query = text("""
                    SELECT id_usuarios, nome, senha 
                    FROM usuarios 
                    WHERE nome = :username
                """)
                result = conn.execute(query, {"username": username})
                user = result.mappings().first()

                if user and user["senha"] == password_hash:
                    session["user_id"] = user["id_usuarios"]
                    session["username"] = user["nome"]
                    flash("Login realizado com sucesso!")
                    logging.info(f"Login bem-sucedido para o usuário: {username}")
                    return redirect(url_for("tela"))
                else:
                    flash("Usuário ou senha inválidos!")
                    logging.warning(f"Tentativa de login falhou para o usuário: {username}")
                    return redirect(url_for("index"))

            else:
                # Cadastro
                username = request.form.get("username")
                email = request.form.get("email")
                password = request.form.get("password")
                confirm_password = request.form.get("confirm_password")
                birth_date = request.form.get("birth_date")

                # Log dos dados recebidos do formulário
                logging.debug(
                    f"Dados do formulário: username={username}, email={email}, birth_date={birth_date}"
                )

                # Validação dos campos
                if not all([username, email, password, confirm_password, birth_date]):
                    flash("Preencha todos os campos de cadastro.")
                    logging.warning("Campos do formulário incompletos.")
                    return redirect(url_for("index"))

                if password != confirm_password:
                    flash("As senhas não coincidem!")
                    logging.warning("Senhas não coincidem.")
                    return redirect(url_for("index"))

                # Validar formato da data de nascimento
                try:
                    datetime.strptime(birth_date, "%Y-%m-%d")
                except ValueError:
                    flash("Formato de data de nascimento inválido. Use AAAA-MM-DD.")
                    logging.error(f"Formato de birth_date inválido: {birth_date}")
                    return redirect(url_for("index"))

                # Criar objeto Usuario, passando id como None
                try:
                    usuario = objeto.Usuario(
                        id=None,
                        nome=username,
                        email=email,
                        senha=password,
                        data_nascimento=birth_date,
                    )
                    logging.info(
                        f"Objeto Usuario criado: id={usuario.id}, nome={usuario.nome}, email={usuario.email}, data_nascimento={usuario.data_nascimento}"
                    )
                except ValueError as e:
                    flash(f"Erro ao criar usuário: {str(e)}")
                    logging.error(f"Erro ao criar objeto Usuario: {str(e)}")
                    return redirect(url_for("index"))

                # Calcular idade
                birth = datetime.strptime(birth_date, "%Y-%m-%d")
                today = datetime.now()
                idade = today.year - birth.year - (
                    (today.month, today.day) < (birth.month, birth.day)
                )
                password_hash = hash_password(password)

                # Verificar se o usuário ou email já existe
                query = text("SELECT * FROM usuarios WHERE nome = :username OR email = :email")
                result = conn.execute(query, {"username": username, "email": email})
                existing_user = result.mappings().first()
                if existing_user:
                    if existing_user["nome"] == username:
                        flash("Usuário já existe!")
                        logging.warning(f"Usuário já existe: {username}")
                    elif existing_user["email"] == email:
                        flash("E-mail já está registrado!")
                        logging.warning(f"E-mail já registrado: {email}")
                    return redirect(url_for("index"))

                # Inserir usuário no banco
                try:
                    query = text("""
                        INSERT INTO usuarios (nome, idade, email, senha, data_criacao)
                        VALUES (:nome, :idade, :email, :senha, :data_criacao)
                        RETURNING id_usuarios
                    """)
                    result = conn.execute(query, {
                        "nome": username,
                        "idade": idade,
                        "email": email,
                        "senha": password_hash,
                        "data_criacao": datetime.now()
                    })
                    user_id = result.mappings().first()["id_usuarios"]
                except psycopg2.errors.UniqueViolation as e:
                    flash("E-mail já está registrado!")
                    logging.error(f"Erro de unicidade no cadastro: {e}")
                    return redirect(url_for("index"))

                conn.commit()

                session["user_id"] = user_id
                session["username"] = username

                # Funções externas
                try:
                    vincular.vinc(email)
                    Email_sender.e_mail(email, username)
                except Exception as e:
                    logging.error(f"Erro nas funções externas: {e}")
                    flash(f"Cadastro realizado, mas houve um erro ao enviar o e-mail: {e}")

                # Criar backup dos usuários
                try:
                    df = pd.read_sql("SELECT * FROM usuarios", engine)
                    logging.info("Dados da tabela 'usuarios' após cadastro:")
                    logging.info(df)
                    backup_path = os.path.join(os.getcwd(), "usuarios_backup.csv")
                    df.to_csv(backup_path, index=False)
                    logging.info(f"Backup salvo em: {backup_path}")
                except Exception as e:
                    logging.error(f"Erro ao criar backup: {e}")
                    flash(f"Cadastro realizado, mas houve um erro ao criar o backup: {e}")

                flash("Cadastro realizado com sucesso!")
                return redirect(url_for("tela"))

    except Exception as err:
        flash(f"Erro no processamento: {err}")
        logging.error(f"Erro no banco de dados durante submit: {err}")
        return redirect(url_for("index"))

# Rota para obter conteúdos e perguntas de um subtema
@cadastro.route("/get_content/<int:subtopico_id>")
def get_content(subtopico_id):
    try:
        with engine.connect() as conn:
            # Obter o id_licao a partir do subtopico_id
            query = text("""
                SELECT t.licao_id
                FROM subtopicos s
                JOIN topicos t ON s.topico_id = t.id
                WHERE s.id = :subtopico_id
            """)
            result = conn.execute(query, {"subtopico_id": subtopico_id})
            licao = result.mappings().first()
            if not licao:
                return jsonify({"error": "Lição não encontrada para este subtema"}), 404
            licao_id = licao["licao_id"]

            # Obter conteúdos
            query_content = text("""
                SELECT numero, titulo, texto
                FROM conteudos
                WHERE subtopico_id = :subtopico_id
                ORDER BY ordem
            """)
            df_content = pd.read_sql(query_content, engine, params={"subtopico_id": subtopico_id})

            # Processar o texto de cada conteúdo
            if not df_content.empty:
                df_content['texto'] = df_content['texto'].apply(process_text)

            # Obter perguntas
            query = text("""
                SELECT id_pergunta, enunciado, resposta_correta, opcoes
                FROM perguntas
                WHERE id_licao = :licao_id
            """)
            result = conn.execute(query, {"licao_id": licao_id})
            perguntas = result.mappings().all()
            perguntas_list = [dict(row) for row in perguntas]

            if not df_content.empty:
                conteudos = df_content.to_dict(orient="records")
                return jsonify(
                    {"conteudos": conteudos, "perguntas": perguntas_list, "licao_id": licao_id}
                )
            else:
                return (
                    jsonify(
                        {
                            "error": "Nenhum conteúdo encontrado para este subtema",
                            "perguntas": perguntas_list,
                            "licao_id": licao_id,
                        }
                    ),
                    404,
                )

    except Exception as e:
        logging.error(f"Erro no banco de dados: {e}")
        return jsonify({"error": f"Erro no banco de dados: {e}"}), 500

# Rota para salvar progresso e pontos
@cadastro.route("/save_progress", methods=["POST"])
def save_progress():
    if "user_id" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    data = request.get_json()
    licao_id = data.get("licao_id")
    points = data.get("points")

    if not licao_id or points is None:
        return jsonify({"error": "Dados inválidos"}), 400

    try:
        with engine.connect() as conn:
            # Verificar se já existe um registro na tabela progresso
            query = text("""
                SELECT pontos_ganhos
                FROM progresso
                WHERE id_usuario = :id_usuario AND id_licao = :id_licao
            """)
            result = conn.execute(query, {
                "id_usuario": session["user_id"],
                "id_licao": licao_id
            })
            existing_progress = result.mappings().first()

            if existing_progress:
                # Se existe, somar os novos pontos aos pontos existentes
                new_points = existing_progress["pontos_ganhos"] + points
                query = text("""
                    UPDATE progresso
                    SET pontos_ganhos = :new_points, status_progresso = :status
                    WHERE id_usuario = :id_usuario AND id_licao = :id_licao
                """)
                conn.execute(query, {
                    "new_points": new_points,
                    "status": "concluido",
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id
                })
            else:
                # Se não existe, inserir um novo registro
                query = text("""
                    INSERT INTO progresso (id_usuario, id_licao, status_progresso, pontos_ganhos)
                    VALUES (:id_usuario, :id_licao, :status, :pontos)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id,
                    "status": "concluido",
                    "pontos": points
                })

            # Verificar se já existe um registro na tabela gamificacao
            query = text("""
                SELECT valor
                FROM gamificacao
                WHERE id_usuario = :id_usuario AND id_licao = :id_licao AND tipo = :tipo
            """)
            result = conn.execute(query, {
                "id_usuario": session["user_id"],
                "id_licao": licao_id,
                "tipo": "moeda"
            })
            existing_gamificacao = result.mappings().first()

            if existing_gamificacao:
                # Se existe, somar os novos pontos aos pontos existentes
                new_valor = existing_gamificacao["valor"] + points
                query = text("""
                    UPDATE gamificacao
                    SET valor = :new_valor, data_recebimento = :data_recebimento
                    WHERE id_usuario = :id_usuario AND id_licao = :id_licao AND tipo = :tipo
                """)
                conn.execute(query, {
                    "new_valor": new_valor,
                    "data_recebimento": datetime.now(),
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id,
                    "tipo": "moeda"
                })
            else:
                # Se não existe, inserir um novo registro
                query = text("""
                    INSERT INTO gamificacao (id_usuario, id_licao, tipo, valor, data_recebimento)
                    VALUES (:id_usuario, :id_licao, :tipo, :valor, :data_recebimento)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id,
                    "tipo": "moeda",
                    "valor": points,
                    "data_recebimento": datetime.now()
                })

            conn.commit()
            return jsonify({
                "message": "Progresso salvo com sucesso",
                "points": points,
                "redirect": url_for("tela"),
            })
    except Exception as e:
        logging.error(f"Erro ao salvar progresso: {e}")
        return jsonify({"error": f"Erro ao salvar progresso: {e}"}), 500

# Rota para obter o ranking dos 10 melhores usuários
@cadastro.route("/get_ranking", methods=["GET"])
def get_ranking():
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT u.nome AS username, COALESCE(SUM(p.pontos_ganhos), 0) AS total_pontos
                FROM usuarios u
                LEFT JOIN progresso p ON u.id_usuarios = p.id_usuario
                GROUP BY u.id_usuarios, u.nome
                ORDER BY total_pontos DESC
                LIMIT 10
            """)
            result = conn.execute(query)
            ranking = result.mappings().all()
            ranking_list = [dict(row) for row in ranking]
            return jsonify({"ranking": ranking_list})
    except Exception as e:
        logging.error(f"Erro ao obter ranking: {e}")
        return jsonify({"error": f"Erro ao obter ranking: {e}"}), 500

if __name__ == "__main__":
    init_db()
    cadastro.run(debug=True, host="127.0.0.1", port=5000)