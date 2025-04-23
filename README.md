# Projeto PI - Sistema de Cadastro e Login

## Descrição
Sistema web simples com Flask para cadastro e login de usuários, integrado ao MySQL. Inclui hashing de senhas, envio de email, backup em CSV e logging.

## Estrutura do Código
- **Configuração**: Flask (`cadastro`), MySQL (`db_config`), logging.
- **Banco de Dados**: Função `get_db_connection()` testa e retorna conexão; `init_db()` cria tabela `usuarios`.
- **Rotas**:
  - `/`: Página inicial (`cadastro.html`).
  - `/tela`: Tela principal após login.
  - `/submit`: Processa login (valida usuário/senha) e cadastro (insere no BD, envia email, faz backup).
- **Funções Auxiliares**: `hash_password()` para segurança; integração com `Email_sender` e `objeto.Usuario`.

## Pré-requisitos
- Python 3.x
- MySQL Server
- Bibliotecas: `mysql-connector-python`, `pandas`, `flask`

## Instalação
1. Clone o repositório.
2. Instale dependências: `pip install -r requirements.txt`.
3. Configure `db_config` com suas credenciais MySQL.

## Uso
- Rode: `python app.py`.
- Acesse: `http://127.0.0.1:5000`.

## Funcionalidades
- Cadastro com validação.
- Login seguro.
- Backup em CSV.
- Email de confirmação.
- Logging para depuração.

## Contribuição
Abra issues ou pull requests para sugestões!

## localizar main

Linha 12: Configuração do Flask com secret key
Linha 15: Configuração de logging (nível DEBUG)
Linha 17: Configuração do banco de dados MySQL (host, user, senha, database, porta)
Linha 27: Função get_db_connection para conectar ao banco MySQL
Linha 37: Função hash_password para criptografar senhas com SHA-256
Linha 44: Função init_db para criar tabelas do banco (usuarios, licao, perguntas, etc.)
Linha 125: Rota principal (/) renderiza cadastro.html
Linha 130: Rota /tela renderiza telaPrincipal.html com dados do usuário
Linha 187: Rota /contentScreen.html renderiza contentScreen.html
Linha 192: Rota /submit processa login e cadastro
Linha 297: Rota /get_content/<subtopico_id> retorna conteúdos e perguntas (JSON)
Linha 347: Rota /save_progress salva progresso e pontos do usuário
Linha 384: Inicializa banco e roda aplicação Flask (debug, host, porta 5000)