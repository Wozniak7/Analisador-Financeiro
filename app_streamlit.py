import streamlit as st
from pymongo import MongoClient
import bcrypt # Para hashing de senhas

st.set_page_config(page_title="Analisador Financeiro - Login", layout="centered")

hide_sidebar_css = """
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
"""

# --- Configuração do MongoDB ---
# INSTRUÇÕES:
# 1. Se você estiver usando MongoDB Atlas, cole sua string de conexão aqui.
#    Ex: "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority"
# 2. Se estiver usando MongoDB localmente, use "mongodb://localhost:27017/"
MONGO_CONNECTION_STRING = "mongodb+srv://danillowsoares:spxMUrvtdzRW3iRP@cluster0.mhruzz7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" # <-- COLOQUE SUA STRING DE CONEXÃO AQUI!

DB_NAME = "streamlit_users_db"
COLLECTION_NAME = "users"

@st.cache_resource # Cacheia a conexão com o banco de dados para evitar reconexões a cada re-run
def get_database():
    """
    Estabelece e retorna a conexão com o banco de dados MongoDB.
    """
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client[DB_NAME]
        # st.success("✅ Conectado ao MongoDB!") # Removido para não poluir a tela de login
        return db
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao MongoDB: {e}")
        st.info("Por favor, verifique sua string de conexão e se o MongoDB está rodando.")
        return None

db = get_database()

# --- Funções de Hashing de Senha ---
def hash_password(password):
    """
    Gera um hash da senha usando bcrypt.
    """
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password

def check_password(password, hashed_password):
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# --- Funções de Usuário (CRUD Básico) ---
def register_user(username, password):
    """
    Registra um novo usuário no banco de dados.
    """
    if db is None:
        st.error("Conexão com o banco de dados não estabelecida.")
        return False

    users_collection = db[COLLECTION_NAME]
    
    if users_collection.find_one({"username": username}):
        st.warning("Nome de usuário já existe. Por favor, escolha outro.")
        return False
    
    hashed_pwd = hash_password(password)
    
    user_data = {
        "username": username,
        "password": hashed_pwd
    }
    
    users_collection.insert_one(user_data)
    st.success("🎉 Usuário registrado com sucesso!")
    return True

def authenticate_user(username, password):
    """
    Autentica um usuário.
    """
    if db is None:
        st.error("Conexão com o banco de dados não estabelecida.")
        return False

    users_collection = db[COLLECTION_NAME]
    user = users_collection.find_one({"username": username})
    
    if user:
        if check_password(password, user["password"]):
            return True
        else:
            st.error("Senha incorreta.")
            return False
    else:
        st.error("Nome de usuário não encontrado.")
        return False

# --- Gerenciamento de Sessão do Streamlit ---
# Inicializa o estado de login se não existir
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- Lógica Principal do Aplicativo ---
if not st.session_state.logged_in:
    # Se o usuário NÃO está logado, mostra a tela de login/cadastro
    st.markdown(hide_sidebar_css, unsafe_allow_html=True)
    st.title("🔐 Acesso Restrito")
    st.markdown("Por favor, faça login ou cadastre-se para acessar as ferramentas.")

    auth_option = st.radio("Selecione uma opção:", ("Login", "Cadastrar Novo Usuário"), key="auth_option_main")

    if auth_option == "Login":
        with st.form("login_form_main"):
            login_username = st.text_input("Nome de Usuário", key="login_username_main")
            login_password = st.text_input("Senha", type="password", key="login_password_main")
            login_button = st.form_submit_button("Entrar")

            if login_button:
                if authenticate_user(login_username, login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.rerun() # Re-executa o app para mostrar o conteúdo logado
    
    elif auth_option == "Cadastrar Novo Usuário":
        with st.form("register_form_main"):
            reg_username = st.text_input("Nome de Usuário (min. 3 caracteres)", key="reg_username_main")
            reg_password = st.text_input("Senha (min. 6 caracteres)", type="password", key="reg_password_main")
            confirm_password = st.text_input("Confirme a Senha", type="password", key="confirm_password_main")
            register_button = st.form_submit_button("Cadastrar")

            if register_button:
                if len(reg_username) < 3:
                    st.error("Nome de usuário deve ter pelo menos 3 caracteres.")
                elif len(reg_password) < 6:
                    st.error("Senha deve ter pelo menos 6 caracteres.")
                elif reg_password != confirm_password:
                    st.error("As senhas não coincidem.")
                else:
                    if register_user(reg_username, reg_password):
                        st.session_state.logged_in = True
                        st.session_state.username = reg_username
                        st.rerun() # Re-executa o app para mostrar o conteúdo logado

else:
    # Se o usuário ESTÁ logado, exibe a mensagem de boas-vindas e o botão de logout
    # O Streamlit automaticamente exibirá as páginas da pasta 'pages' na barra lateral.
    st.sidebar.success(f"Login efetuado como: {st.session_state.username}!")
    
    # Adicione aqui qualquer conteúdo que você queira na página "Home" (se houver)
    # quando o usuário está logado. Por exemplo:
    st.title(f"Bem-vindo, {st.session_state.username}!")
    st.markdown("Use a barra lateral para navegar entre as ferramentas disponíveis.")

    if st.sidebar.button("Sair (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun() # Re-executa o app para voltar à tela de login

