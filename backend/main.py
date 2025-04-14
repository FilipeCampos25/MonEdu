from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mysql.connector
import pandas as pd
from datetime import datetime
import hashlib
import os
import logging
from funcoes import Email_sender, objeto, vincular

# Configuração do Flask
cadastro = Flask(__name__, template_folder='../frontend')
cadastro.secret_key = 'herekinkajou613'

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do banco de dados
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'lipe250505',
    'database': 'projeto_pi',
    'port': 3306
}

# Função para conectar ao banco de dados
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            logging.info("Conexão ao banco de dados estabelecida com sucesso.")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Inicialização do banco de dados
def init_db():
    conn = get_db_connection()
    if conn is None:
        logging.error("Não foi possível inicializar o banco de dados.")
        return
    
    try:
        cursor = conn.cursor()

        # Criar a tabela usuarios se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuarios INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                idade INT,
                email VARCHAR(255),
                senha VARCHAR(255) NOT NULL,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Criar tabela licao
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licao (
                id_licao INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                nivel INT,
                conteudo TEXT,
                pontos_recompensa INT
            )
        ''')

        # Criar tabela perguntas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS perguntas (
                id_pergunta INT AUTO_INCREMENT PRIMARY KEY,
                id_licao INT,
                enunciado TEXT NOT NULL,
                resposta_correta VARCHAR(255) NOT NULL,
                opcoes TEXT NOT NULL,
                FOREIGN KEY (id_licao) REFERENCES licao(id_licao)
            )
        ''')

        # Criar tabela gamificacao
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gamificacao (
                id_gamificacao INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT,
                tipo ENUM('moeda','nivel') NOT NULL,
                valor INT NOT NULL,
                data_recebimento DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuarios)
            )
        ''')

        # Criar tabela progresso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progresso (
                id_progresso INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT,
                id_licao INT,
                status_progresso ENUM('iniciado','concluido'),
                pontos_ganhos INT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuarios),
                FOREIGN KEY (id_licao) REFERENCES licao(id_licao)
            )
        ''')

        # Criar outras tabelas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topicos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                licao_id INT,
                nome VARCHAR(100) NOT NULL,
                ordem INT NOT NULL,
                FOREIGN KEY (licao_id) REFERENCES licao(id_licao)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subtopicos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topico_id INT,
                numero VARCHAR(10) NOT NULL,
                nome VARCHAR(100) NOT NULL,
                ordem INT NOT NULL,
                FOREIGN KEY (topico_id) REFERENCES topicos(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conteudos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subtopico_id INT,
                numero VARCHAR(10) NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                texto TEXT NOT NULL,
                ordem INT NOT NULL,
                FOREIGN KEY (subtopico_id) REFERENCES subtopicos(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        logging.info("Tabelas verificadas/criadas com sucesso.")
    except mysql.connector.Error as err:
        logging.error(f"Erro ao criar tabelas: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            logging.info("Conexão ao banco de dados fechada após inicialização.")

# Rota principal (página de cadastro/login)
@cadastro.route('/')
def index():
    return render_template('cadastro.html')

# Rota para a tela principal
@cadastro.route('/tela')
def tela():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    if conn is None:
        flash('Erro: Não foi possível conectar ao banco de dados.')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)

        # Obter nome do usuário
        cursor.execute("SELECT nome FROM usuarios WHERE id_usuarios = %s", (session['user_id'],))
        user_data = cursor.fetchone()
        if not user_data:
            flash('Usuário não encontrado.')
            session.pop('user_id', None)
            return redirect(url_for('index'))

        username = user_data['nome']

        # Somar os pontos_ganhos da tabela progresso
        cursor.execute("""
            SELECT COALESCE(SUM(pontos_ganhos), 0) AS total_pontos
            FROM progresso
            WHERE id_usuario = %s
        """, (session['user_id'],))
        points_data = cursor.fetchone()
        points = points_data['total_pontos']

        # Obter tópicos e subtemas
        cursor.execute("SELECT id, nome FROM topicos ORDER BY ordem")
        topicos = cursor.fetchall()

        secoes = []
        for topico in topicos:
            cursor.execute("""
                SELECT id, numero, nome 
                FROM subtopicos 
                WHERE topico_id = %s 
                ORDER BY ordem
            """, (topico['id'],))
            subtopicos = cursor.fetchall()
            secoes.append({
                'id': topico['id'],
                'nome': topico['nome'],
                'subtopicos': subtopicos
            })

        return render_template('telaPrincipal.html',
                             username=username,
                             points=points,
                             secoes=secoes)
    except mysql.connector.Error as e:
        flash(f"Erro ao carregar a tela principal: {e}")
        return redirect(url_for('index'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Rota para a tela de conteúdo
@cadastro.route('/contentScreen.html')
def content_screen():
    return render_template('contentScreen.html')

# Rota para processar login e cadastro
@cadastro.route('/submit', methods=['POST'])
def submit():
    conn = get_db_connection()
    if conn is None:
        flash('Erro: Não foi possível conectar ao banco de dados.')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()

        if 'confirm_password' not in request.form:
            # Login
            username = request.form.get('username')
            password = hash_password(request.form.get('password', ''))

            if not username or not password:
                flash('Preencha todos os campos de login.')
                return redirect(url_for('index'))

            cursor.execute('SELECT id_usuarios, nome, senha FROM usuarios WHERE nome = %s', (username,))
            user = cursor.fetchone()

            if user and user[2] == password:
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash('Login realizado com sucesso!')
                logging.info(f"Login bem-sucedido para o usuário: {username}")
                return redirect(url_for('tela'))
            else:
                flash('Usuário ou senha inválidos!')
                logging.warning(f"Tentativa de login falhou para o usuário: {username}")

        else:
            # Cadastro
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            birth_date = request.form.get('birth_date')

            if not all([username, password, confirm_password, birth_date]):
                flash('Preencha todos os campos de cadastro.')
                return redirect(url_for('index'))

            if password != confirm_password:
                flash('As senhas não coincidem!')
                return redirect(url_for('index'))

            try:
                usuario = objeto.Usuario(username, email, password, birth_date)
                logging.info(f"Objeto Usuario criado: nome={usuario.nome}, email={usuario.email}, birth_date={birth_date}")
            except ValueError as e:
                flash(str(e))
                return redirect(url_for('index'))

            birth = datetime.strptime(birth_date, '%Y-%m-%d')
            today = datetime.now()
            idade = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            password_hash = hash_password(password)

            cursor.execute('SELECT * FROM usuarios WHERE nome = %s', (username,))
            if cursor.fetchone():
                flash('Usuário já existe!')
                return redirect(url_for('index'))

            cursor.execute('''
                INSERT INTO usuarios (nome, idade, email, senha, data_criacao)
                VALUES (%s, %s, %s, %s, %s)
            ''', (username, idade, email, password_hash, datetime.now()))
            
            conn.commit()

            cursor.execute("SELECT id_usuarios FROM usuarios WHERE nome = %s", (username,))
            user_id = cursor.fetchone()[0]

            session['user_id'] = user_id
            session['username'] = username

            vincular.vinc(email)
            Email_sender.e_mail(email, username)

            cursor.execute('''
                INSERT INTO gamificacao (id_usuario, tipo, valor, data_recebimento) 
                VALUES (%s, %s, %s, %s)
            ''', (user_id, "moeda", 0, datetime.now()))
            
            conn.commit()

            df = pd.read_sql_query("SELECT * FROM usuarios", conn)
            logging.info("Dados da tabela 'usuarios' após cadastro:")
            logging.info(df)

            backup_path = os.path.join(os.getcwd(), 'usuarios_backup.csv')
            df.to_csv(backup_path, index=False)
            logging.info(f"Backup salvo em: {backup_path}")

            flash('Cadastro realizado com sucesso!')
            return redirect(url_for('tela'))

    except mysql.connector.Error as err:
        flash(f'Erro no processamento: {err}')
        logging.error(f"Erro no banco de dados durante submit: {err}")
    except Exception as e:
        flash(f'Ocorreu um erro inesperado: {e}')
        logging.error(f"Erro inesperado: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            logging.info("Conexão ao banco de dados fechada após operação.")

    return redirect(url_for('index'))

# Rota para obter conteúdos e perguntas de um subtema
@cadastro.route('/get_content/<int:subtopico_id>')
def get_content(subtopico_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Não foi possível conectar ao banco de dados'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)

        # Obter o id_licao a partir do subtopico_id
        cursor.execute("""
            SELECT t.licao_id 
            FROM subtopicos s 
            JOIN topicos t ON s.topico_id = t.id 
            WHERE s.id = %s
        """, (subtopico_id,))
        licao = cursor.fetchone()
        if not licao:
            return jsonify({'error': 'Lição não encontrada para este subtema'}), 404
        licao_id = licao['licao_id']

        # Obter conteúdos
        query_content = """
            SELECT numero, titulo, texto 
            FROM conteudos 
            WHERE subtopico_id = %s 
            ORDER BY ordem
        """
        df_content = pd.read_sql(query_content, conn, params=(subtopico_id,))
        
        # Obter perguntas
        cursor.execute("""
            SELECT id_pergunta, enunciado, resposta_correta, opcoes
            FROM perguntas 
            WHERE id_licao = %s
        """, (licao_id,))
        perguntas = cursor.fetchall()

        if not df_content.empty:
            conteudos = df_content.to_dict(orient='records')
            return jsonify({
                'conteudos': conteudos,
                'perguntas': perguntas,
                'licao_id': licao_id
            })
        else:
            return jsonify({
                'error': 'Nenhum conteúdo encontrado para este subtema',
                'perguntas': perguntas,
                'licao_id': licao_id
            }), 404
            
    except mysql.connector.Error as e:
        return jsonify({'error': f'Erro no banco de dados: {e}'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# Rota para salvar progresso e pontos
@cadastro.route('/save_progress', methods=['POST'])
def save_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    data = request.get_json()
    licao_id = data.get('licao_id')
    points = data.get('points')

    if not licao_id or points is None:
        return jsonify({'error': 'Dados inválidos'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Não foi possível conectar ao banco de dados'}), 500

    try:
        cursor = conn.cursor()

        # Inserir ou atualizar progresso
        cursor.execute("""
            INSERT INTO progresso (id_usuario, id_licao, status_progresso, pontos_ganhos)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status_progresso = %s,
                pontos_ganhos = %s
        """, (
            session['user_id'], licao_id, 'concluido', points,
            'concluido', points
        ))

        # Inserir registro na gamificação
        cursor.execute("""
            INSERT INTO gamificacao (id_usuario, tipo, valor, data_recebimento)
            VALUES (%s, %s, %s, %s)
        """, (
            session['user_id'], 'moeda', points, datetime.now()
        ))

        conn.commit()
        return jsonify({
            'message': 'Progresso salvo com sucesso',
            'points': points,
            'redirect': url_for('tela')
        })
    except mysql.connector.Error as e:
        conn.rollback()
        logging.error(f"Erro ao salvar progresso: {e}")
        return jsonify({'error': f'Erro ao salvar progresso: {e}'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    init_db()
    cadastro.run(debug=True, host='127.0.0.1', port=5000)