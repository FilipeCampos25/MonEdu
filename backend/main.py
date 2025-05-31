from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os
import logging
from dotenv import load_dotenv
from funcoes import Email_sender
from funcoes.objeto import Usuario, CarteiraVirtual, Progresso, Rank, Gamificacao
import random
from decimal import Decimal
import pickle
import base64

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Flask
cadastro = Flask(__name__, template_folder="../frontend", static_folder="static")
cadastro.secret_key = os.getenv("FLASK_SECRET_KEY", "herekinkajou613")

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    db_path = os.path.join(os.path.dirname(__file__), 'local_database.db')
    engine = create_engine(f"sqlite:///{db_path}", pool_pre_ping=True)

# Função para hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para processar texto com marcações
def process_text(text):
    if not text:
        return text
    text = text.replace('\\n', '\n')
    return text

# Função para serializar objeto para a sessão
def serialize_object(obj):
    return base64.b64encode(pickle.dumps(obj)).decode('utf-8')

# Função para desserializar objeto da sessão
def deserialize_object(serialized):
    return pickle.loads(base64.b64decode(serialized))

# Inicialização do banco de dados
def init_db():
    try:
        with engine.connect() as conn:
            is_postgres = engine.dialect.name == "postgresql"
            id_type = "SERIAL" if is_postgres else "INTEGER"
            auto_increment = "" if is_postgres else "AUTOINCREMENT"
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuarios {id_type} PRIMARY KEY {auto_increment},
                    nome VARCHAR(100),
                    idade INTEGER,
                    email VARCHAR(255) UNIQUE,
                    senha VARCHAR(255),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    moedas DECIMAL(10, 2) DEFAULT 0.00
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS licao (
                    id_licao {id_type} PRIMARY KEY {auto_increment},
                    titulo VARCHAR(255),
                    nivel INTEGER,
                    conteudo TEXT,
                    pontos_recompensa INTEGER
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS perguntas (
                    id_pergunta {id_type} PRIMARY KEY {auto_increment},
                    id_licao INTEGER,
                    enunciado TEXT,
                    resposta_correta VARCHAR(255),
                    opcoes TEXT,
                    FOREIGN KEY (id_licao) REFERENCES licao (id_licao)
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS gamificacao (
                    id_gamificacao {id_type} PRIMARY KEY {auto_increment},
                    id_usuario INTEGER,
                    id_licao INTEGER,
                    tipo VARCHAR(20),
                    valor INTEGER,
                    data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios),
                    FOREIGN KEY (id_licao) REFERENCES licao (id_licao),
                    UNIQUE (id_usuario, id_licao, tipo)
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS progresso (
                    id_progresso {id_type} PRIMARY KEY {auto_increment},
                    id_usuario INTEGER,
                    id_licao INTEGER,
                    status_progresso VARCHAR(20),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    pontos_ganhos INTEGER DEFAULT 0,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios),
                    FOREIGN KEY (id_licao) REFERENCES licao (id_licao),
                    UNIQUE (id_usuario, id_licao)
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id_transacao {id_type} PRIMARY KEY {auto_increment},
                    id_usuario INTEGER,
                    valor DECIMAL(10, 2) NOT NULL,
                    descricao TEXT NOT NULL,
                    tipo_transacao VARCHAR(20),
                    data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios)
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS topicos (
                    id {id_type} PRIMARY KEY {auto_increment},
                    licao_id INTEGER,
                    nome VARCHAR(100) NOT NULL,
                    ordem INTEGER NOT NULL,
                    FOREIGN KEY (licao_id) REFERENCES licao (id_licao)
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS subtopicos (
                    id {id_type} PRIMARY KEY {auto_increment},
                    topico_id INTEGER,
                    numero VARCHAR(10) NOT NULL,
                    nome VARCHAR(100) NOT NULL,
                    ordem INTEGER NOT NULL,
                    FOREIGN KEY (topico_id) REFERENCES topicos (id) ON DELETE CASCADE
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS conteudos (
                    id {id_type} PRIMARY KEY {auto_increment},
                    subtopico_id INTEGER,
                    numero VARCHAR(10) NOT NULL,
                    titulo VARCHAR(200) NOT NULL,
                    texto TEXT NOT NULL,
                    ordem INTEGER NOT NULL,
                    FOREIGN KEY (subtopico_id) REFERENCES subtopicos (id) ON DELETE CASCADE
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS cotas_usuario (
                    id_cota {id_type} PRIMARY KEY {auto_increment},
                    id_usuario INTEGER,
                    quantidade INTEGER NOT NULL,
                    valor_cota DECIMAL(10, 2) NOT NULL,
                    tipo VARCHAR(20),
                    data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuarios)
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS valor_cota_atual (
                    id {id_type} PRIMARY KEY {auto_increment},
                    valor_cota DECIMAL(10, 2) DEFAULT 50.00,
                    volatilidade VARCHAR(20) DEFAULT 'padrao',
                    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS historico_valor_cota (
                    id {id_type} PRIMARY KEY {auto_increment},
                    open_price DECIMAL(10, 2) NOT NULL,
                    high_price DECIMAL(10, 2) NOT NULL,
                    low_price DECIMAL(10, 2) NOT NULL,
                    close_price DECIMAL(10, 2) NOT NULL,
                    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                INSERT INTO valor_cota_atual (valor_cota, volatilidade, ultima_atualizacao)
                SELECT 50.00, 'padrao', CURRENT_TIMESTAMP
                WHERE NOT EXISTS (SELECT 1 FROM valor_cota_atual)
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
    if "user_id" not in session or "usuario_obj" not in session:
        flash("Por favor, faça login para acessar esta página.")
        return redirect(url_for("index"))

    try:
        usuario = deserialize_object(session["usuario_obj"])
        username = usuario.nome
        points = usuario._Usuario__carteira.pontos
        user_info = {
            "nome": usuario.nome,
            "idade": None,
            "email": usuario.email,
            "data_criacao": usuario.data_nascimento,
            "moedas": float(points)
        }

        with engine.connect() as conn:
            query = text("SELECT id, nome, licao_id FROM topicos ORDER BY ordem")
            result = conn.execute(query)
            topicos = result.mappings().all()

            secoes = []
            for topico in topicos:
                query = text("""
                    SELECT s.id, s.numero, s.nome, s.ordem
                    FROM subtopicos s
                    WHERE s.topico_id = :topico_id
                    ORDER BY s.ordem
                """)
                result = conn.execute(query, {"topico_id": topico["id"]})
                subtopicos = result.mappings().all()

                subtopicos_with_status = []
                for index, subtopico in enumerate(subtopicos):
                    status = "nao_iniciado"
                    for progresso in usuario._Usuario__progressos:
                        if progresso.id_licao == topico["licao_id"]:
                            status = progresso.status_progresso
                            break

                    is_locked = False
                    if index > 0:
                        prev_subtopico = subtopicos[index - 1]
                        prev_status = "nao_iniciado"
                        for progresso in usuario._Usuario__progressos:
                            if progresso.id_licao == topico["licao_id"]:
                                prev_status = progresso.status_progresso
                                break
                        is_locked = prev_status != "concluido"

                    subtopicos_with_status.append({
                        "id": subtopico["id"],
                        "numero": subtopico["numero"],
                        "nome": subtopico["nome"],
                        "ordem": subtopico["ordem"],
                        "status": status,
                        "is_locked": is_locked
                    })

                secoes.append({
                    "id": topico["id"],
                    "nome": topico["nome"],
                    "licao_id": topico["licao_id"],
                    "subtopicos": subtopicos_with_status,
                })

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
                username = request.form.get("username")
                password = request.form.get("password")
                if not username or not password:
                    flash("Preencha todos os campos de login.")
                    response = make_response(redirect(url_for("index")))
                    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                    return response

                password_hash = hash_password(password)
                query = text("""
                    SELECT id_usuarios, nome, email, senha, data_criacao, moedas 
                    FROM usuarios 
                    WHERE nome = :username
                """)
                result = conn.execute(query, {"username": username})
                user_data = result.mappings().first()

                if user_data and user_data["senha"] == password_hash:
                    usuario = Usuario(
                        id=user_data["id_usuarios"],
                        nome=user_data["nome"],
                        email=user_data["email"],
                        senha=password,
                        data_nascimento=user_data["data_criacao"].strftime("%Y-%m-%d")
                    )
                    usuario._Usuario__carteira = CarteiraVirtual()
                    usuario._Usuario__carteira.receita(float(user_data["moedas"]))

                    query = text("""
                        SELECT id_progresso, id_licao, status_progresso, pontos_ganhos
                        FROM progresso
                        WHERE id_usuario = :id_usuario
                    """)
                    result = conn.execute(query, {"id_usuario": user_data["id_usuarios"]})
                    for progresso_data in result.mappings():
                        progresso = Progresso(
                            id_progresso=progresso_data["id_progresso"],
                            id_usuario=user_data["id_usuarios"],
                            id_licao=progresso_data["id_licao"],
                            status_progresso=progresso_data["status_progresso"],
                            pontos_ganho=progresso_data["pontos_ganhos"]
                        )
                        usuario._Usuario__progressos.append(progresso)

                    session["user_id"] = user_data["id_usuarios"]
                    session["username"] = user_data["nome"]
                    session["usuario_obj"] = serialize_object(usuario)
                    flash("Login realizado com sucesso!")
                    logging.info(f"Login bem-sucedido para o usuário: {username}")
                    response = make_response(redirect(url_for("tela")))
                    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                    return response
                else:
                    flash("Usuário ou senha inválidos!")
                    logging.warning(f"Tentativa de login falhou para o usuário: {username}")
                    response = make_response(redirect(url_for("index")))
                    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                    return response
            else:
                username = request.form.get("username")
                email = request.form.get("email")
                password = request.form.get("password")
                confirm_password = request.form.get("confirm_password")
                birth_date = request.form.get("birth_date")

                if not all([username, email, password, confirm_password, birth_date]):
                    flash("Preencha todos os campos de cadastro.")
                    logging.warning("Campos do formulário incompletos.")
                    response = make_response(redirect(url_for("index")))
                    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                    return response

                if password != confirm_password:
                    flash("As senhas não coincidem!")
                    logging.warning("Senhas não coincidem.")
                    response = make_response(redirect(url_for("index")))
                    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                    return response

                try:
                    usuario = Usuario(
                        id=None,
                        nome=username,
                        email=email,
                        senha=password,
                        data_nascimento=birth_date
                    )
                except ValueError as e:
                    flash(f"Erro ao criar usuário: {str(e)}")
                    logging.error(f"Erro ao criar objeto Usuario: {str(e)}")
                    response = make_response(redirect(url_for("index")))
                    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                    return response

                birth = datetime.strptime(birth_date, "%Y-%m-%d")
                today = datetime.now()
                idade = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
                password_hash = hash_password(password)

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
                    response = make_response(redirect(url_for("index")))
                    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                    return response

                query = text("""
                    INSERT INTO usuarios (nome, idade, email, senha, data_criacao, moedas)
                    VALUES (:nome, :idade, :email, :senha, :data_criacao, :moedas)
                    RETURNING id_usuarios
                """)
                result = conn.execute(query, {
                    "nome": username,
                    "idade": idade,
                    "email": email,
                    "senha": password_hash,
                    "data_criacao": datetime.now(),
                    "moedas": 0.00
                })
                user_id = result.mappings().first()["id_usuarios"]
                conn.commit()

                usuario._Usuario__id = user_id
                session["user_id"] = user_id
                session["username"] = username
                session["usuario_obj"] = serialize_object(usuario)

                try:
                    Email_sender.e_mail(email, username)
                except Exception as e:
                    logging.error(f"Erro nas funções externas: {e}")
                    flash(f"Cadastro realizado, mas houve um erro ao enviar o e-mail: {e}")

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
                response = make_response(redirect(url_for("tela")))
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                return response

    except Exception as err:
        flash(f"Erro no processamento: {err}")
        logging.error(f"Erro no banco de dados durante submit: {err}")
        response = make_response(redirect(url_for("index")))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

# Rota para obter conteúdos e perguntas de um subtema
@cadastro.route("/get_content/<int:subtopico_id>")
def get_content(subtopico_id):
    if "user_id" not in session:
        logging.error("Tentativa de acessar conteúdo sem usuário autenticado")
        return jsonify({"error": "Usuário não autenticado"}), 401

    try:
        with engine.connect() as conn:
            query = text("SELECT id, topico_id, ordem FROM subtopicos WHERE id = :subtopico_id")
            result = conn.execute(query, {"subtopico_id": subtopico_id})
            subtopico = result.mappings().first()
            if not subtopico:
                logging.error(f"Subtema com ID {subtopico_id} não encontrado")
                return jsonify({"error": "Subtema não encontrado"}), 404

            query = text("""
                SELECT t.licao_id
                FROM subtopicos s
                JOIN topicos t ON s.topico_id = t.id
                WHERE s.id = :subtopico_id
            """)
            result = conn.execute(query, {"subtopico_id": subtopico_id})
            licao = result.mappings().first()
            if not licao:
                logging.error(f"Lição não encontrada para o subtema com ID {subtopico_id}")
                return jsonify({"error": "Lição não encontrada para este subtema"}), 404
            licao_id = licao["licao_id"]

            query = text("""
                SELECT s.id
                FROM subtopicos s
                WHERE s.topico_id = :topico_id AND s.ordem < :ordem
                ORDER BY s.ordem DESC
                LIMIT 1
            """)
            result = conn.execute(query, {
                "topico_id": subtopico["topico_id"],
                "ordem": subtopico["ordem"]
            })
            prev_subtopico = result.mappings().first()

            usuario = deserialize_object(session["usuario_obj"])
            if prev_subtopico:
                prev_status = "nao_iniciado"
                for progresso in usuario._Usuario__progressos:
                    if progresso.id_licao == licao_id:
                        prev_status = progresso.status_progresso
                        break
                if prev_status != "concluido":
                    logging.info(f"Subtema {subtopico_id} bloqueado: subtema anterior não concluído")
                    return jsonify({"error": "Subtema bloqueado. Conclua o subtema anterior primeiro."}), 403

            query_content = text("""
                SELECT numero, titulo, texto
                FROM conteudos
                WHERE subtopico_id = :subtopico_id
                ORDER BY ordem
            """)
            df_content = pd.read_sql(query_content, engine, params={"subtopico_id": subtopico_id})

            if not df_content.empty:
                df_content['texto'] = df_content['texto'].apply(process_text)

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
                logging.debug(f"Resposta enviada: conteudos={len(conteudos)}, perguntas={len(perguntas_list)}, licao_id={licao_id}")
                return jsonify({
                    "conteudos": conteudos,
                    "perguntas": perguntas_list,
                    "licao_id": licao_id
                })
            else:
                logging.debug(f"Resposta enviada: error='Nenhum conteúdo encontrado', perguntas={len(perguntas_list)}, licao_id={licao_id}")
                return jsonify({
                    "error": "Nenhum conteúdo encontrado para este subtema",
                    "perguntas": perguntas_list,
                    "licao_id": licao_id
                }), 404

    except Exception as e:
        logging.error(f"Erro ao obter conteúdos para subtema {subtopico_id}: {e}")
        return jsonify({"error": f"Erro ao acessar o banco de dados: {str(e)}"}), 500

# Rota para salvar progresso e moedas
@cadastro.route("/save_progress", methods=["POST"])
def save_progress():
    if "user_id" not in session or "usuario_obj" not in session:
        logging.error("Tentativa de salvar progresso sem usuário autenticado")
        return jsonify({"error": "Usuário não autenticado"}), 401

    data = request.get_json()
    logging.debug(f"Dados recebidos na requisição: {data}")
    
    if not data:
        logging.error("Nenhum dado recebido na requisição")
        return jsonify({"error": "Nenhum dado enviado"}), 400

    licao_id = data.get("licao_id")
    points = data.get("points")

    if licao_id is None or not isinstance(licao_id, int):
        logging.error(f"Dados inválidos - licao_id: {licao_id}, points: {points}")
        return jsonify({"error": f"Dados inválidos: licao_id={licao_id} deve ser um número inteiro"}), 400
    
    if points is None or not isinstance(points, (int, float)) or points < 0:
        logging.error(f"Dados inválidos - licao_id: {licao_id}, points: {points}")
        return jsonify({"error": f"Dados inválidos: points={points} deve ser um número não negativo"}), 400

    moedas_ganhas = float(points)

    try:
        usuario = deserialize_object(session["usuario_obj"])

        with engine.connect() as conn:
            query = text("""
                SELECT id_licao
                FROM licao
                WHERE id_licao = :id_licao
            """)
            result = conn.execute(query, {"id_licao": licao_id})
            if not result.mappings().first():
                logging.error(f"Lição não encontrada: id_licao={licao_id}")
                return jsonify({"error": "Lição não encontrada"}), 404

            for progresso in usuario._Usuario__progressos:
                if progresso.id_licao == licao_id and progresso.status_progresso == "concluido":
                    logging.info(f"Lição {licao_id} já concluída para usuário {session['user_id']}")
                    return jsonify({"error": "Lição já concluída"}), 400

            progresso_existente = None
            for progresso in usuario._Usuario__progressos:
                if progresso.id_licao == licao_id:
                    progresso_existente = progresso
                    break

            if progresso_existente:
                usuario.atualizar_progresso(progresso_existente.id_progresso, "concluido", moedas_ganhas)
            else:
                query = text("""
                    INSERT INTO progresso (id_usuario, id_licao, status_progresso, data_criacao, pontos_ganhos)
                    VALUES (:id_usuario, :id_licao, :status, :data_criacao, :pontos_ganhos)
                    RETURNING id_progresso
                """)
                result = conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id,
                    "status": "iniciado",
                    "data_criacao": datetime.now(),
                    "pontos_ganhos": 0
                })
                id_progresso = result.mappings().first()["id_progresso"]
                usuario.adicionar_progresso(id_progresso, licao_id)
                usuario.atualizar_progresso(id_progresso, "concluido", moedas_ganhas)

            gamificacao = Gamificacao(
                id_gamificacao=random.randint(1, 1000000),
                id_usuario=session["user_id"],
                tipo="moeda",
                valor=int(moedas_ganhas)
            )
            resultado = gamificacao.aplicar_gamificacao(usuario)

            query = text("""
                SELECT status_progresso
                FROM progresso
                WHERE id_usuario = :id_usuario AND id_licao = :id_licao
            """)
            result = conn.execute(query, {
                "id_usuario": session["user_id"],
                "id_licao": licao_id
            })
            existing_progress = result.mappings().first()

            if existing_progress:
                query = text("""
                    UPDATE progresso
                    SET status_progresso = :status, data_criacao = :data_criacao, pontos_ganhos = :pontos_ganhos
                    WHERE id_usuario = :id_usuario AND id_licao = :id_licao
                """)
                conn.execute(query, {
                    "status": "concluido",
                    "data_criacao": datetime.now(),
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id,
                    "pontos_ganhos": moedas_ganhas
                })
            else:
                query = text("""
                    INSERT INTO progresso (id_usuario, id_licao, status_progresso, data_criacao, pontos_ganhos)
                    VALUES (:id_usuario, :id_licao, :status, :data_criacao, :pontos_ganhos)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id,
                    "status": "concluido",
                    "data_criacao": datetime.now(),
                    "pontos_ganhos": moedas_ganhas
                })

            query = text("""
                UPDATE usuarios
                SET moedas = :moedas
                WHERE id_usuarios = :id_usuario
            """)
            conn.execute(query, {
                "moedas": usuario._Usuario__carteira.pontos,
                "id_usuario": session["user_id"]
            })

            query = text("""
                INSERT INTO transacoes (id_usuario, valor, descricao, tipo_transacao, data_transacao)
                VALUES (:id_usuario, :valor, :descricao, :tipo_transacao, :data_transacao)
            """)
            conn.execute(query, {
                "id_usuario": session["user_id"],
                "valor": moedas_ganhas,
                "descricao": "Exercício concluído",
                "tipo_transacao": "entrada",
                "data_transacao": datetime.now()
            })

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
                new_valor = existing_gamificacao["valor"] + int(moedas_ganhas)
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
                query = text("""
                    INSERT INTO gamificacao (id_usuario, id_licao, tipo, valor, data_recebimento)
                    VALUES (:id_usuario, :id_licao, :tipo, :valor, :data_recebimento)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "id_licao": licao_id,
                    "tipo": "moeda",
                    "valor": int(moedas_ganhas),
                    "data_recebimento": datetime.now()
                })

            conn.commit()
            session["usuario_obj"] = serialize_object(usuario)
            logging.info(f"Progresso salvo com sucesso: licao_id={licao_id}, moedas_ganhas={moedas_ganhas}")
            return jsonify({
                "message": "Progresso salvo com sucesso",
                "points": moedas_ganhas,
                "redirect": url_for("tela"),
            })
    except Exception as e:
        logging.error(f"Erro ao salvar progresso: {e}")
        return jsonify({"error": f"Erro ao salvar progresso: {str(e)}"}), 500

# Rota para obter o ranking dos 10 melhores usuários
@cadastro.route("/get_ranking", methods=["GET"])
def get_ranking():
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id_usuarios, nome, email, senha, data_criacao, moedas 
                FROM usuarios
            """)
            result = conn.execute(query)
            usuarios = []
            for row in result.mappings():
                usuario = Usuario(
                    id=row["id_usuarios"],
                    nome=row["nome"],
                    email=row["email"],
                    senha=row["senha"],
                    data_nascimento=row["data_criacao"].strftime("%Y-%m-%d")
                )
                usuario._Usuario__carteira.receita(float(row["moedas"]))
                usuarios.append(usuario)

            usuario_atual = deserialize_object(session["usuario_obj"])
            rank = Rank(usuarios, usuario_atual)
            rank.insertion_sort()
            
            ranking_list = [
                {"username": usuario.nome, "total_pontos": float(pontuacao)}
                for pontuacao, usuario in rank.ranking[:10]
            ]
            
            posicao_atual = -1
            for i, (_, usuario) in enumerate(rank.ranking):
                if usuario == usuario_atual:
                    posicao_atual = i + 1
                    break

            response = {"ranking": ranking_list}
            if posicao_atual > 10:
                response["user_position"] = {
                    "position": posicao_atual,
                    "username": usuario_atual.nome,
                    "total_pontos": float(usuario_atual._Usuario__carteira.pontos)
                }

            return jsonify(response)
    except Exception as e:
        logging.error(f"Erro ao obter ranking: {e}")
        return jsonify({"error": f"Erro ao obter ranking: {e}"}), 500

# Rota para obter histórico de transações da carteira digital
@cadastro.route("/get_wallet_history", methods=["GET"])
def get_wallet_history():
    if "user_id" not in session or "usuario_obj" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    try:
        usuario = deserialize_object(session["usuario_obj"])
        balance = float(usuario._Usuario__carteira.pontos)

        with engine.connect() as conn:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
            transaction_type = request.args.get("type", "all")
            offset = (page - 1) * per_page

            type_condition = ""
            if transaction_type == "entrada":
                type_condition = "AND tipo_transacao = 'entrada'"
            elif transaction_type == "saida":
                type_condition = "AND tipo_transacao = 'saida'"

            query = text(f"""
                SELECT valor, descricao, tipo_transacao, data_transacao
                FROM transacoes
                WHERE id_usuario = :id_usuario
                {type_condition}
                ORDER BY data_transacao DESC
                LIMIT :per_page OFFSET :offset
            """)
            result = conn.execute(query, {
                "id_usuario": session["user_id"],
                "per_page": per_page,
                "offset": offset
            })
            transactions = result.mappings().all()

            query_count = text(f"""
                SELECT COUNT(*) AS total
                FROM transacoes
                WHERE id_usuario = :id_usuario
                {type_condition}
            """)
            result = conn.execute(query_count, {"id_usuario": session["user_id"]})
            total_transactions = result.mappings().first()["total"]

            transactions_list = [
                {
                    "valor": float(row["valor"]),
                    "descricao": row["descricao"],
                    "data_transacao": row["data_transacao"].strftime("%d/%m/%Y %H:%M:%S"),
                    "tipo": row["tipo_transacao"]
                }
                for row in transactions
            ]

            return jsonify({
                "transactions": transactions_list,
                "total_transactions": total_transactions,
                "balance": balance,
                "pages": (total_transactions + per_page - 1) // per_page
            })
    except Exception as e:
        logging.error(f"Erro ao obter histórico da carteira: {e}")
        return jsonify({"error": f"Erro ao obter histórico: {e}"}), 500

# Rotas do Simulador de Investimento
@cadastro.route("/api/state", methods=["GET"])
def get_state():
    if "user_id" not in session or "usuario_obj" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    try:
        usuario = deserialize_object(session["usuario_obj"])
        balance = float(usuario._Usuario__carteira.pontos)

        with engine.connect() as conn:
            query = text("""
                SELECT COALESCE(SUM(CASE WHEN tipo = 'compra' THEN quantidade ELSE -quantidade END), 0) AS total_cotas
                FROM cotas_usuario
                WHERE id_usuario = :id_usuario
            """)
            result = conn.execute(query, {"id_usuario": session["user_id"]})
            shares = int(result.mappings().first()["total_cotas"])

            query = text("SELECT valor_cota, volatilidade FROM valor_cota_atual ORDER BY id DESC LIMIT 1")
            result = conn.execute(query)
            cota_data = result.mappings().first()
            current_price = float(cota_data["valor_cota"])
            mode = cota_data["volatilidade"]

            query = text("""
                SELECT open_price, close_price, data_registro
                FROM historico_valor_cota
                WHERE data_registro <= CURRENT_TIMESTAMP
                ORDER BY data_registro DESC
                LIMIT 30
            """)
            result = conn.execute(query)
            price_history = [
                {
                    "t": row["data_registro"].strftime("%Y-%m-%d %H:%M:%S"),
                    "o": float(row["open_price"]),
                    "c": float(row["close_price"])
                }
                for row in result.mappings()
            ]

            query = text("""
                SELECT COALESCE(SUM(CASE WHEN tipo = 'compra' THEN quantidade * valor_cota ELSE 0 END), 0) AS total_invested
                FROM cotas_usuario
                WHERE id_usuario = :id_usuario
            """)
            result = conn.execute(query, {"id_usuario": session["user_id"]})
            total_invested = float(result.mappings().first()["total_invested"])

            return jsonify({
                "balance": balance,
                "shares": shares,
                "current_price": current_price,
                "price_history": price_history,
                "initial_price": 50.0,
                "total_invested": total_invested,
                "mode": mode
            })
    except Exception as e:
        logging.error(f"Erro ao obter estado: {str(e)}")
        return jsonify({"error": f"Erro ao obter dados: {str(e)}"}), 500

@cadastro.route("/api/trade", methods=["POST"])
def trade():
    if "user_id" not in session or "usuario_obj" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    data = request.get_json()
    action = data.get("action")
    amount = data.get("amount", 0)

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Quantidade inválida"}), 400

    try:
        usuario = deserialize_object(session["usuario_obj"])
        with engine.connect() as conn:
            query = text("SELECT valor_cota FROM valor_cota_atual ORDER BY id DESC LIMIT 1")
            result = conn.execute(query)
            current_price = float(result.mappings().first()["valor_cota"])

            if action == "buy":
                total_cost = amount * current_price
                if total_cost > usuario._Usuario__carteira.pontos:
                    return jsonify({"error": "Saldo de moedas insuficiente"}), 400

                usuario.retirar_moedas(total_cost)
                query = text("""
                    INSERT INTO cotas_usuario (id_usuario, quantidade, valor_cota, tipo, data_transacao)
                    VALUES (:id_usuario, :quantidade, :valor_cota, 'compra', :data_transacao)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "quantidade": amount,
                    "valor_cota": current_price,
                    "data_transacao": datetime.now()
                })

                query = text("""
                    INSERT INTO transacoes (id_usuario, valor, descricao, tipo_transacao, data_transacao)
                    VALUES (:id_usuario, :valor, :descricao, :tipo_transacao, :data_transacao)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "valor": -total_cost,
                    "descricao": f"Compra de {amount} cota(s)",
                    "tipo_transacao": "saida",
                    "data_transacao": datetime.now()
                })

                query = text("""
                    UPDATE usuarios
                    SET moedas = :moedas
                    WHERE id_usuarios = :id_usuario
                """)
                conn.execute(query, {
                    "moedas": usuario._Usuario__carteira.pontos,
                    "id_usuario": session["user_id"]
                })

                conn.commit()
                session["usuario_obj"] = serialize_object(usuario)
                return jsonify({"message": f"Comprou {amount} cotas por {total_cost:.2f} moedas"})

            elif action == "sell":
                query = text("""
                    SELECT COALESCE(SUM(CASE WHEN tipo = 'compra' THEN quantidade ELSE -quantidade END), 0) AS total_cotas
                    FROM cotas_usuario
                    WHERE id_usuario = :id_usuario
                """)
                result = conn.execute(query, {"id_usuario": session["user_id"]})
                total_cotas = int(result.mappings().first()["total_cotas"])

                if amount > total_cotas:
                    return jsonify({"error": "Cotas insuficientes"}), 400

                total_value = amount * current_price
                usuario.adicionar_moedas(total_value)

                query = text("""
                    INSERT INTO cotas_usuario (id_usuario, quantidade, valor_cota, tipo, data_transacao)
                    VALUES (:id_usuario, :quantidade, :valor_cota, 'venda', :data_transacao)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "quantidade": amount,
                    "valor_cota": current_price,
                    "data_transacao": datetime.now()
                })

                query = text("""
                    INSERT INTO transacoes (id_usuario, valor, descricao, tipo_transacao, data_transacao)
                    VALUES (:id_usuario, :valor, :descricao, :tipo_transacao, :data_transacao)
                """)
                conn.execute(query, {
                    "id_usuario": session["user_id"],
                    "valor": total_value,
                    "descricao": f"Venda de {amount} cota(s)",
                    "tipo_transacao": "entrada",
                    "data_transacao": datetime.now()
                })

                query = text("""
                    UPDATE usuarios
                    SET moedas = :moedas
                    WHERE id_usuarios = :id_usuario
                """)
                conn.execute(query, {
                    "moedas": usuario._Usuario__carteira.pontos,
                    "id_usuario": session["user_id"]
                })

                conn.commit()
                session["usuario_obj"] = serialize_object(usuario)
                return jsonify({"message": f"Vendeu {amount} cotas por {total_value:.2f} moedas"})

            return jsonify({"error": "Ação inválida"}), 400
    except Exception as e:
        logging.error(f"Erro ao realizar transação: {e}")
        return jsonify({"error": f"Erro ao processar transação: {e}"}), 500

@cadastro.route("/api/update_price", methods=["POST"])
def update_price():
    try:
        with engine.connect() as conn:
            data = request.get_json() or {}
            query = text("SELECT volatilidade, valor_cota, ultima_atualizacao FROM valor_cota_atual ORDER BY id DESC LIMIT 1")
            result = conn.execute(query)
            cota_data = result.mappings().first()
            last_price = float(cota_data["valor_cota"])
            mode = cota_data["volatilidade"]
            ultima_atualizacao = cota_data["ultima_atualizacao"]

            current_time = datetime.now()
            time_diff = current_time - ultima_atualizacao
            days_passed = time_diff.total_seconds() / (60 * 60 * 24)

            if days_passed >= 7:
                modes = ['padrao', 'pico_valorizacao', 'pico_desvalorizacao']
                mode = random.choice(modes)
                query = text("""
                    UPDATE valor_cota_atual
                    SET volatilidade = :volatilidade, ultima_atualizacao = :ultima_atualizacao
                    WHERE id = (SELECT id FROM valor_cota_atual ORDER BY id DESC LIMIT 1)
                """)
                conn.execute(query, {
                    "volatilidade": mode,
                    "ultima_atualizacao": current_time
                })
                logging.debug(f"Modo atualizado para: {mode}")

            if days_passed >= 1:
                variation = random.uniform(0.02, 0.05)
                if mode == "pico_valorizacao" and random.random() <= 0.6:
                    variation = variation
                elif mode == "pico_desvalorizacao" and random.random() <= 0.6:
                    variation = -variation
                else:
                    variation = variation if random.random() > 0.5 else -variation

                open_price = last_price
                close_price = last_price * (1 + variation)
                high_price = max(open_price, close_price) * random.uniform(1.02, 1.05)
                low_price = min(open_price, close_price) * random.uniform(0.95, 0.98)
                close_price = round(close_price, 2)
                high_price = round(high_price, 2)
                low_price = round(low_price, 2)

                query = text("""
                    UPDATE valor_cota_atual
                    SET valor_cota = :valor_cota, ultima_atualizacao = :ultima_atualizacao
                    WHERE id = (SELECT id FROM valor_cota_atual ORDER BY id DESC LIMIT 1)
                """)
                conn.execute(query, {
                    "valor_cota": close_price,
                    "ultima_atualizacao": current_time
                })

                query = text("""
                    INSERT INTO historico_valor_cota (open_price, high_price, low_price, close_price, data_registro)
                    VALUES (:open_price, :high_price, :low_price, :close_price, :data_registro)
                """)
                conn.execute(query, {
                    "open_price": open_price,
                    "high_price": high_price,
                    "low_price": low_price,
                    "close_price": close_price,
                    "data_registro": current_time
                })

                logging.debug(f"Preço atualizado: open={open_price}, close={close_price}, high={high_price}, low={low_price}")

            conn.commit()
            return jsonify({"message": "Preço verificado/atualizado"})
    except Exception as e:
        logging.error(f"Erro ao atualizar preço: {e}")
        return jsonify({"error": f"Erro ao atualizar preço: {e}"}), 500

@cadastro.route("/api/set_mode", methods=["POST"])
def set_mode():
    try:
        with engine.connect() as conn:
            data = request.get_json()
            mode = data.get("mode")
            if mode not in ["padrao", "pico_valorizacao", "pico_desvalorizacao"]:
                return jsonify({"error": "Modo inválido"}), 400

            query = text("""
                UPDATE valor_cota_atual
                SET volatilidade = :volatilidade, ultima_atualizacao = :ultima_atualizacao
                WHERE id = (SELECT id FROM valor_cota_atual ORDER BY id DESC LIMIT 1)
            """)
            conn.execute(query, {
                "volatilidade": mode,
                "ultima_atualizacao": datetime.now()
            })
            conn.commit()
            return jsonify({"message": f"Modo alterado para {mode}"})
    except Exception as e:
        logging.error(f"Erro ao definir modo: {e}")
        return jsonify({"error": f"Erro ao definir modo: {e}"}), 500

# Rota para logout
@cadastro.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("usuario_obj", None)
    flash("Logout realizado com sucesso!")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    cadastro.run(debug=True, host="127.0.0.1", port=5000)