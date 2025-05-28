## Link do Render: https://monedu.onrender.com

# Projeto PI - Sistema de Cadastro e Gamificação

## **Descrição**

Sistema web educacional desenvolvido com **Flask**, integrando funcionalidades de cadastro, login, gamificação e simulador de investimentos. Suporta bancos de dados **PostgreSQL** (Neon/Render) ou **SQLite**, com hashing de senhas, envio de e-mails, backup em **CSV**, logging e um sistema de aprendizado gamificado com moedas e cotas.

## **Estrutura do Código**

- **Configuração**:
  - **Flask** (`cadastro`) com templates e arquivos estáticos.
  - Suporte a **PostgreSQL** (Render/Neon) ou **SQLite** local.
  - Logging configurado no nível **DEBUG**.
  - Variáveis de ambiente via **dotenv**.
- **Banco de Dados**:
  - Função `init_db()` cria tabelas: `usuarios`, `licao`, `perguntas`, `gamificacao`, `progresso`, `transacoes`, `topicos`, `subtopicos`, `conteudos`, `cotas_usuario`, `valor_cota_atual`, `historico_valor_cota`.
  - Suporte a chaves estrangeiras e unicidade.
- **Rotas**:
  - `/`: Página inicial (`cadastro.html`).
  - `/tela`: Tela principal com informações do usuário e tópicos.
  - `/contentScreen.html`: Exibe conteúdos educacionais.
  - `/submit`: Processa login e cadastro com validação.
  - `/get_content/<subtopico_id>`: Retorna conteúdos e perguntas em **JSON**.
  - `/save_progress`: Salva progresso e moedas do usuário.
  - `/get_ranking`: Retorna ranking dos 10 melhores usuários por moedas.
  - `/get_wallet_history`: Histórico de transações da carteira digital.
  - Rotas do simulador de investimento: `/api/state`, `/api/trade`, `/api/update_price`, `/api/set_mode`.
- **Funções Auxiliares**:
  - `hash_password()`: Criptografia de senhas com **SHA-256**.
  - `process_text()`: Processa texto com marcações.
  - Integração com **Email_sender** para envio de e-mails de confirmação.
  - `objeto.Usuario` para validação de dados do usuário.

## **Pré-requisitos**

- **Python** 3.x
- Bibliotecas: **flask**, **sqlalchemy**, **pandas**, **python-dotenv**
- Banco de dados **PostgreSQL** (Neon/Render) ou **SQLite**
- Servidor de e-mail configurado para **Email_sender** (opcional)

## **Instalação**

1. Clone o repositório:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente no arquivo `.env`:

   ```
   FLASK_SECRET_KEY=<sua_chave_secreta>
   DATABASE_URL=<url_do_banco_postgresql_ou_sqlite>
   ```

   Exemplo para **SQLite**:

   ```
   DATABASE_URL=sqlite:///local_database.db
   ```

   Exemplo para **PostgreSQL**:

   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

## **Uso**

1. Execute o aplicativo:

   ```bash
   python app.py
   ```

2. Acesse no navegador: `http://127.0.0.1:5000`.

## **Funcionalidades**

- **Cadastro e Login**: Validação de usuário, e-mail e senha com hashing **SHA-256**.
- **Sistema de Aprendizado**: Estrutura hierárquica de tópicos, subtemas e conteúdos educacionais.
- **Gamificação**: Usuários ganham moedas ao completar lições, registradas na tabela `progresso` e `gamificacao`.
- **Simulador de Investimento**: Compra e venda de cotas com preços dinâmicos e volatilidade ajustável.
- **Carteira Digital**: Histórico de transações com paginação e filtragem.
- **Ranking**: Exibe os 10 usuários com mais moedas.
- **Backup**: Dados de usuários exportados para `usuarios_backup.csv`.
- **E-mail**: Envio de e-mail de confirmação após cadastro.
- **Logging**: Registro detalhado de eventos para depuração.

## **Estrutura do Banco de Dados**

- `usuarios`: Informações do usuário (nome, idade, e-mail, senha, moedas, etc.).
- `licao`: Lições educacionais com título, nível, conteúdo e pontos de recompensa.
- `perguntas`: Questões associadas às lições.
- `gamificacao`: Registro de moedas e recompensas por usuário e lição.
- `progresso`: Acompanhamento do progresso do usuário nas lições.
- `transacoes`: Histórico de transações financeiras (entradas/saídas).
- `topicos`, `subtopicos`, `conteudos`: Estrutura hierárquica de conteúdo educacional.
- `cotas_usuario`: Registro de cotas compradas/vendidas por usuário.
- `valor_cota_atual`: Valor atual da cota com volatilidade.
- `historico_valor_cota`: Histórico de preços das cotas.

## **Simulador de Investimento**

- **Estado**: `/api/state` retorna saldo, número de cotas, preço atual e histórico.
- **Transações**: `/api/trade` permite compra/venda de cotas.
- **Atualização de Preço**: `/api/update_price` simula variação de preço com base na volatilidade.
- **Modos de Volatilidade**: `/api/set_mode` ajusta entre `padrao`, `pico_valorizacao` e `pico_desvalorizacao`.

## **Localizar Main**

- **Linha 14**: Configuração do **Flask** com chave secreta.
- **Linha 15**: Configuração de **logging** (nível **DEBUG**).
- **Linha 21**: Configuração do banco de dados (**PostgreSQL** ou **SQLite**).
- **Linha 39**: Função `hash_password` para criptografia de senhas.
- **Linha 46**: Função process_text para processar texto com marcações, substituindo \\n por quebras de linha.
- **Linha 53**: Função `init_db` para criação das tabelas.
- **Linha 165**: Rota principal (`/`) renderiza `cadastro.html`.
- **Linha 170**: Rota `/tela` renderiza `telaPrincipal.html` com dados do usuário.
- **Linha 229**: Rota `/contentScreen.html` renderiza tela de conteúdos.
- **Linha 234**: Rota `/submit` processa login e cadastro.
- **Linha 346**: Rota `/get_content/<subtopico_id>` retorna conteúdos e perguntas.
- **Linha 457**: Rota `/save_progress` salva progresso e moedas.
- **Linha 525**: Rota `/get_ranking` retorna ranking dos usuários.
- **Linha 544**: Rota `/get_wallet_history` retorna histórico de transações.
- **Linha 583**: Rotas do simulador de investimento (`/api/state`, `/api/trade`, etc.).
- **Linha 779**: Inicialização do banco e execução do **Flask**.

## **Notas**

- O sistema usa **session** para gerenciar autenticação, com cabeçalhos `Cache-Control` para segurança.
- O backup em **CSV** é salvo automaticamente após cada cadastro.
- O simulador de investimento atualiza preços a cada 24 horas e volatilidade a cada 7 dias.
- Certifique-se de configurar corretamente as variáveis de ambiente para o banco de dados e e-mail.