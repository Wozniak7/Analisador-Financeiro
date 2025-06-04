import streamlit as st
import qrcode
from PIL import Image
import io

st.set_page_config(page_title="Gerador de QR Code Personalizado", layout="centered")

st.title("📸 Gerador de QR Code Personalizado")
st.markdown("Insira qualquer texto ou URL para gerar seu QR Code.")

# --- Entrada de Dados ---
st.subheader("Dados para o QR Code")
input_data = st.text_area("Digite o texto ou URL para o QR Code:", "https://www.streamlit.io")

# --- Opções de Personalização ---
st.subheader("Opções de Personalização")

# Nível de correção de erro
error_correction_level = st.selectbox(
    "Nível de Correção de Erro (Resiliência a Danos):",
    options=["Baixo (L)", "Médio (M)", "Quartil (Q)", "Alto (H)"],
    index=2, # Padrão para Quartil (Q)
    help="Define a capacidade do QR Code de ser lido mesmo com danos. Níveis mais altos resultam em QR Codes maiores."
)

# Mapeia a seleção para as constantes do qrcode
error_correction_map = {
    "Baixo (L)": qrcode.constants.ERROR_CORRECT_L,
    "Médio (M)": qrcode.constants.ERROR_CORRECT_M,
    "Quartil (Q)": qrcode.constants.ERROR_CORRECT_Q,
    "Alto (H)": qrcode.constants.ERROR_CORRECT_H,
}
selected_error_correction = error_correction_map[error_correction_level]

# Tamanho da caixa (pixels por "caixa" do QR Code)
box_size = st.slider("Tamanho da Caixa (pixels por módulo)", min_value=1, max_value=20, value=10, step=1,
                     help="Aumenta ou diminui o tamanho de cada 'quadradinho' do QR Code.")

# Margem (número de caixas de borda)
border = st.slider("Margem (módulos de borda)", min_value=1, max_value=10, value=4, step=1,
                   help="Define a largura da borda branca ao redor do QR Code.")

# --- Botão Gerar QR Code ---
if st.button("Gerar QR Code"):
    if input_data:
        try:
            # Cria uma instância do gerador de QR Code
            qr = qrcode.QRCode(
                version=1, # Versão 1 é o menor QR Code. O módulo ajustará automaticamente se necessário.
                error_correction=selected_error_correction,
                box_size=box_size,
                border=border,
            )
            
            # Adiciona os dados ao QR Code
            qr.add_data(input_data)
            qr.make(fit=True) # Ajusta o tamanho do QR Code para os dados

            # Cria a imagem do QR Code
            # fill_color e back_color podem ser alterados para personalizar as cores
            img = qr.make_image(fill_color="black", back_color="white")

            st.success("✅ QR Code gerado com sucesso!")
            st.subheader("Seu QR Code:")
            
            # Exibe a imagem do QR Code no Streamlit
            # Converte a imagem PIL para bytes para exibição
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            # ATUALIZAÇÃO: Usando use_container_width em vez de use_column_width
            st.image(byte_im, caption="QR Code Gerado", use_container_width=True) 

            # --- Opção de Download ---
            st.download_button(
                label="Baixar QR Code (PNG)",
                data=byte_im,
                file_name="qrcode_personalizado.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"❌ Ocorreu um erro ao gerar o QR Code: {e}")
            st.info("Verifique se os dados inseridos são válidos.")
    else:
        st.warning("Por favor, digite algum texto ou URL para gerar o QR Code.")

st.markdown("---")
st.markdown("Este aplicativo usa a biblioteca `qrcode` para Python.")

st.sidebar.markdown("### Créditos")
st.sidebar.write("Este aplicativo foi desenvolvido por Danillo Wozniak Soares.")
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre o Aplicativo")
st.sidebar.write("Este gerador de QR Code permite criar códigos personalizados a partir de qualquer texto ou URL. "
                 "Você pode ajustar o nível de correção de erro, o tamanho da caixa e a margem do QR Code.")
st.sidebar.markdown("### Como Usar")
st.sidebar.write("1. Insira o texto ou URL desejado na caixa de entrada.\n"
                 "2. Ajuste as opções de personalização conforme necessário.\n"
                 "3. Clique em 'Gerar QR Code' para criar seu código.\n"
                 "4. Baixe a imagem do QR Code gerado.")
st.sidebar.markdown("### Licença")
st.sidebar.write("Este aplicativo é de código aberto e pode ser usado livremente. Consulte o repositório para mais detalhes.")
