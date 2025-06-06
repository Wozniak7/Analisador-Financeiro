import streamlit as st
import random

st.set_page_config(page_title="Gerador de CPF e CNPJ", layout="centered")

st.title("🔢 Gerador de CPF e CNPJ Válidos")
st.markdown("Gere números de CPF e CNPJ sintéticos e válidos para testes ou demonstrações.")

# --- Funções de Geração ---

def gerar_cpf():
    """
    Gera um número de CPF válido.
    Algoritmo: https://www.macoratti.net/alg_cpf.htm
    """
    # Gera os 9 primeiros dígitos aleatoriamente
    cpf_base = [random.randint(0, 9) for _ in range(9)]

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += cpf_base[i] * (10 - i)
    primeiro_digito = 11 - (soma % 11)
    if primeiro_digito >= 10:
        primeiro_digito = 0
    
    cpf_com_primeiro_digito = cpf_base + [primeiro_digito]

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += cpf_com_primeiro_digito[i] * (11 - i)
    segundo_digito = 11 - (soma % 11)
    if segundo_digito >= 10:
        segundo_digito = 0

    cpf_completo = cpf_com_primeiro_digito + [segundo_digito]

    # Formata o CPF
    cpf_formatado = f"{''.join(map(str, cpf_completo[:3]))}." \
                    f"{''.join(map(str, cpf_completo[3:6]))}." \
                    f"{''.join(map(str, cpf_completo[6:9]))}-" \
                    f"{''.join(map(str, cpf_completo[9:]))}"
    
    return cpf_formatado

def gerar_cnpj():
    """
    Gera um número de CNPJ válido.
    Algoritmo: Adaptado de: https://www.macoratti.net/alg_cnpj.htm
    """
    # Gera os 12 primeiros dígitos aleatoriamente
    # CNPJ base tem 8 dígitos, filial 4 dígitos (0001), e 2 verificadores.
    # Ex: AA.AAA.AAA/BBBB-CC
    cnpj_base = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1] # Fixo 0001 para filial padrão

    # Pesos para o primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    soma = 0
    for i in range(12):
        soma += cnpj_base[i] * pesos1[i]
    
    primeiro_digito = 11 - (soma % 11)
    if primeiro_digito >= 10:
        primeiro_digito = 0
    
    cnpj_com_primeiro_digito = cnpj_base + [primeiro_digito]

    # Pesos para o segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    soma = 0
    for i in range(13):
        soma += cnpj_com_primeiro_digito[i] * pesos2[i]
    
    segundo_digito = 11 - (soma % 11)
    if segundo_digito >= 10:
        segundo_digito = 0
    
    cnpj_completo = cnpj_com_primeiro_digito + [segundo_digito]

    # Formata o CNPJ
    cnpj_formatado = f"{''.join(map(str, cnpj_completo[:2]))}." \
                     f"{''.join(map(str, cnpj_completo[2:5]))}." \
                     f"{''.join(map(str, cnpj_completo[5:8]))}/" \
                     f"{''.join(map(str, cnpj_completo[8:12]))}-" \
                     f"{''.join(map(str, cnpj_completo[12:]))}"
    
    return cnpj_formatado

# --- Interface Streamlit ---

st.subheader("Selecione o Tipo de Geração")
generation_type = st.radio("Gerar:", ("CPF", "CNPJ"), key="generation_type")

generated_number = ""

if st.button(f"Gerar {generation_type}", key="generate_button"):
    if generation_type == "CPF":
        generated_number = gerar_cpf()
    else: # CNPJ
        generated_number = gerar_cnpj()
    st.success(f"✅ {generation_type} gerado com sucesso!")

st.markdown("---")
st.subheader(f"{generation_type} Gerado")

if generated_number:
    # Exibe o número gerado em um st.text_input para facilitar a cópia
    st.text_input(f"{generation_type} gerado:", generated_number, type="default", disabled=False, label_visibility="collapsed")
    st.info("Clique na caixa de texto acima para selecionar e copiar o número.")
else:
    st.info(f"Clique em 'Gerar {generation_type}' para criar um novo número.")

st.markdown("---")
st.markdown("Este aplicativo gera números aleatórios que são *matematicamente válidos*, mas **não correspondem a CPFs/CNPJs reais existentes**.")
st.markdown("Útil para testes de sistemas e desenvolvimento.")
