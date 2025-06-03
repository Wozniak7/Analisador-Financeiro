import streamlit as st
import random
import string

st.set_page_config(page_title="Gerador de Senha Forte", layout="centered")

st.title("🔒 Gerador de Senha Forte")
st.markdown("Crie senhas seguras e aleatórias para proteger suas contas online.")

# --- Configurações da Senha ---
st.subheader("Configurações da Senha")

# Slider para o comprimento da senha
password_length = st.slider("Comprimento da Senha", min_value=8, max_value=64, value=12, step=1)

# Checkboxes para os tipos de caracteres
include_uppercase = st.checkbox("Incluir Letras Maiúsculas (A-Z)", value=True)
include_numbers = st.checkbox("Incluir Números (0-9)", value=True)
include_symbols = st.checkbox("Incluir Símbolos (!@#$%)", value=True)

# --- Lógica de Geração da Senha ---
def generate_password(length, use_uppercase, use_numbers, use_symbols):
    """
    Gera uma senha aleatória com base nos critérios fornecidos.
    """
    characters = string.ascii_lowercase # Sempre inclui letras minúsculas

    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    if not characters: # Evita erro se nenhuma opção for selecionada (embora minúsculas sejam padrão)
        return "Por favor, selecione pelo menos um tipo de caractere."

    # Garante que pelo menos um caractere de cada tipo selecionado esteja presente
    password_chars = []
    if use_uppercase:
        password_chars.append(random.choice(string.ascii_uppercase))
    if use_numbers:
        password_chars.append(random.choice(string.digits))
    if use_symbols:
        password_chars.append(random.choice(string.punctuation))
    
    # Preenche o restante da senha com caracteres aleatórios dos tipos selecionados
    remaining_length = length - len(password_chars)
    if remaining_length < 0: # Caso o comprimento seja menor que o número de tipos obrigatórios
        remaining_length = 0

    password_chars.extend(random.choices(characters, k=remaining_length))
    
    # Embaralha a lista para garantir aleatoriedade na posição dos caracteres obrigatórios
    random.shuffle(password_chars)
    
    return "".join(password_chars)

# --- Botão Gerar Senha ---
generated_password = ""
if st.button("Gerar Senha"):
    if not (include_uppercase or include_numbers or include_symbols):
        st.warning("Por favor, selecione pelo menos uma opção para incluir letras maiúsculas, números ou símbolos (letras minúsculas são sempre incluídas).")
    else:
        generated_password = generate_password(password_length, include_uppercase, include_numbers, include_symbols)

# --- Exibição e Copiar para Área de Transferência ---
st.markdown("---")
st.subheader("Sua Senha Gerada")

if generated_password:
    # Exibe a senha gerada em um st.text_input para facilitar a cópia manual
    # O 'type="default"' mostra o texto, 'disabled=True' impede edição,
    # e 'label_visibility="collapsed"' esconde o rótulo padrão "Senha Gerada".
    st.text_input("Senha Gerada", generated_password, type="default", label_visibility="collapsed")
    
    # Adiciona uma instrução para o usuário copiar manualmente
    st.info("Clique na caixa de texto acima para selecionar e copiar a senha manualmente.")

else:
    st.info("Clique em 'Gerar Senha' para criar uma nova senha.")

st.markdown("---")
st.markdown("Lembre-se de usar senhas únicas e fortes para cada serviço!")

st.sidebar.markdown("### Créditos")
st.sidebar.write("Este aplicativo foi desenvolvido por Danillo Wozniak Soares.")
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre o Aplicativo")
st.sidebar.write("Este gerador de senha forte permite criar senhas seguras e aleatórias com base em suas preferências. "
                  "Você pode escolher o comprimento da senha e quais tipos de caracteres incluir.")
st.sidebar.markdown("### Como Usar")
st.sidebar.write("1. Ajuste o comprimento da senha usando o controle deslizante.\n"
                  "2. Selecione as opções para incluir letras maiúsculas, números e símbolos.\n"
                  "3. Clique em 'Gerar Senha' para criar sua senha forte.")
st.sidebar.markdown("### Dicas de Segurança")
st.sidebar.write("1. Use senhas únicas para cada conta.\n"
                  "2. Considere usar um gerenciador de senhas para armazenar suas senhas com segurança.\n"
                  "3. Atualize suas senhas regularmente para manter sua segurança online.")
                  
