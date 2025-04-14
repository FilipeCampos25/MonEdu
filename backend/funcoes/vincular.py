import mysql.connector
from datetime import datetime

def vinc(email):
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'lipe250505',
        'database': 'projeto_pi',
        'port': 3306
    }

    def get_db_connection():
        try:
            return mysql.connector.connect(**db_config)
        except mysql.connector.Error as err:
            print(f"Erro na conexão: {err}")
            return None
        
    # Conectar ao banco de dados
    conn = get_db_connection()
    if not conn or not conn.is_connected():
        return "Falha na conexão com o banco de dados"

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            return "Usuário não encontrado"

        usuario_id = result[0]
        
        # Inserções em uma única transação
        cursor.execute('''INSERT INTO gamificacao (id_usuario, tipo, valor, data_criacao) 
                         VALUES (%s, %s, %s, %s)''', 
                      (usuario_id, "moeda", 0, datetime.now()))
        
        cursor.execute('''INSERT INTO progresso (id_usuario, id_licao, status_progresso, pontos_ganhos) 
                         VALUES (%s, %s, %s, %s)''', 
                      (usuario_id, 1, "iniciado", 0))
        
        conn.commit()
        return "Registro inserido com sucesso"

    except mysql.connector.Error as err:
        conn.rollback()
        return f"Erro ao executar operação: {err}"

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
