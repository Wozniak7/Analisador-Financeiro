import streamlit as st
import pandas as pd
import os
import io
import contextlib
import sys # Importa sys para redirecionamento de stdout
import tempfile # Importa tempfile para lidar com arquivos temporários

# Classe para capturar a saída do console
class StreamlitConsoleCapture(io.StringIO):
    def __init__(self, target_stream=None):
        super().__init__()
        self.target_stream = target_stream # Onde a saída deveria ir originalmente (e.g., sys.stdout)

    def write(self, s):
        super().write(s)
        if self.target_stream:
            self.target_stream.write(s) # Mantém a saída indo para o console real

    def flush(self):
        super().flush()
        if self.target_stream:
            self.target_stream.flush()
            
# --- FUNÇÃO DE ANÁLISE COMPLETA E ATUALIZADA ---
def analisar_planilha_financeira(caminho_arquivo):
    """
    Lê uma planilha de transações financeiras, categoriza e agrupa os dados.
    Esta é a sua função 'analisar_planilha_financeira' final e corrigida.
    """
    print(f"\nTentando ler o arquivo: {caminho_arquivo}")

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return {"error": f"O arquivo '{caminho_arquivo}' não foi encontrado."}

    try:
        # Tenta ler o arquivo Excel ou CSV
        if caminho_arquivo.endswith('.xlsx') or caminho_arquivo.endswith('.xls'):
            df = pd.read_excel(caminho_arquivo)
        elif caminho_arquivo.endswith('.csv'):
            try:
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', decimal=',', thousands='.')
            except Exception as e:
                print(f"Aviso: Falha na leitura avançada do CSV: {e}. Tentando leitura básica...")
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
        else:
            print("Erro: Formato de arquivo não suportado. Por favor, use .xlsx, .xls ou .csv.")
            return {"error": "Formato de arquivo não suportado. Por favor, use .xlsx, .xls ou .csv."}

        print("Arquivo lido com sucesso!")
        
        # Normaliza os nomes das colunas
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

        colunas_esperadas = {
            'valor': ['valor', 'quantia', 'montante'],
            'data': ['data', 'data_transacao', 'data_pagamento', 'data_recebimento'],
            'tipo': ['tipo', 'categoria', 'natureza'],
            'conta_bancaria': ['conta', 'conta_bancaria', 'banco']
        }

        colunas_encontradas = {}
        for esperado, possiveis in colunas_esperadas.items():
            for possivel in possiveis:
                if possivel in df.columns:
                    colunas_encontradas[esperado] = possivel
                    break
            if esperado not in colunas_encontradas:
                print(f"Aviso: Não foi possível encontrar a coluna '{esperado}' (tentou: {', '.join(possiveis)}).")
                # Se uma coluna essencial como 'valor' ou 'data' não for encontrada, retorne erro.
                if esperado in ['valor', 'data']:
                    return {"error": f"Coluna essencial '{esperado}' não encontrada. Verifique os nomes das colunas na sua planilha."}
                # Para outras colunas, continue, mas elas não serão usadas nos agrupamentos correspondentes.


        df = df.rename(columns={v: k for k, v in colunas_encontradas.items()})

        # Processamento da coluna 'valor'
        if 'valor' in df.columns:
            df['valor'] = df['valor'].astype(str)
            df['valor'] = df['valor'].str.replace('R$', '', regex=False) \
                                     .str.replace('.', '', regex=False) \
                                     .str.replace(',', '.', regex=False) \
                                     .str.strip()
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            df.dropna(subset=['valor'], inplace=True)
        else:
            print("Erro: Coluna 'valor' não encontrada ou inválida após normalização.")
            return {"error": "Coluna 'valor' não encontrada ou inválida após normalização."}

        # Processamento da coluna 'data'
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
            df.dropna(subset=['data'], inplace=True)
            # --- NOVO: Formatar a coluna 'data' para exibição em formato BR (DD/MM/AAAA) ---
            df['data_br'] = df['data'].dt.strftime('%d/%m/%Y')
        else:
            print("Erro: Coluna 'data' não encontrada ou inválida após normalização.")
            return {"error": "Coluna 'data' não encontrada ou inválida após normalização."}

        # Padroniza a coluna 'tipo' ou infere
        if 'tipo' in df.columns:
            df['tipo_original'] = df['tipo'].astype(str).str.lower().str.strip()
            # Limpeza mais agressiva para caracteres não alfanuméricos
            df['tipo_original'] = df['tipo_original'].str.replace(r'[^a-z\s]', '', regex=True).str.strip()

            mapeamento_tipo = {
                'receita': 'Receita', 'entrada': 'Receita', 'ganho': 'Receita',
                'pagamento': 'Despesa', 'despesa': 'Despesa', 'saida': 'Despesa', 'gasto': 'Despesa'
            }
            df['tipo_categorizado'] = df['tipo_original'].map(mapeamento_tipo).fillna('Outros')
            
            # Correção final: Se o valor for negativo, force como Despesa
            # Usa o 'tipo_categorizado' como fallback se o valor não for negativo
            df['tipo'] = df.apply(lambda row: 'Despesa' if row['valor'] < 0 else row['tipo_categorizado'], axis=1)
            
        else:
            print("Aviso: Coluna 'tipo' não encontrada. Inferindo tipo pelo sinal do 'valor'.")
            df['tipo'] = df['valor'].apply(lambda x: 'Receita' if x >= 0 else 'Despesa')

        # Remove colunas auxiliares se elas foram criadas
        if 'tipo_original' in df.columns:
            df.drop(columns=['tipo_original'], inplace=True)
        if 'tipo_categorizado' in df.columns:
            df.drop(columns=['tipo_categorizado'], inplace=True)

        # Usar a coluna formatada para as transações de detalhes
        # Criar uma cópia para evitar SettingWithCopyWarning
        transacoes_receitas = df[df['tipo'] == 'Receita'].copy()
        transacoes_despesas = df[df['tipo'] == 'Despesa'].copy()

        # Selecionar e reordenar colunas para exibição, usando 'data_br'
        if 'data_br' in df.columns:
            colunas_exibicao = ['data_br', 'valor', 'tipo', 'conta_bancaria', 'descricao']
            # Garante que 'descricao' e 'conta_bancaria' existam antes de selecionar
            colunas_exibicao = [col for col in colunas_exibicao if col in df.columns]

            transacoes_receitas = transacoes_receitas[colunas_exibicao].rename(columns={'data_br': 'data'})
            transacoes_despesas = transacoes_despesas[colunas_exibicao].rename(columns={'data_br': 'data'})
        # else: se data_br não existe, as colunas padrão serão usadas pelo dataframe, sem a formatação BR


        resultados = {}

        total_receber = transacoes_receitas['valor'].sum()
        total_pagar = transacoes_despesas['valor'].sum() # Esta soma será negativa se as despesas forem negativas
        saldo_total = total_receber + total_pagar

        resultados['Resumo Geral'] = {
            'Total a Receber': f"R$ {total_receber:,.2f}",
            'Total a Pagar': f"R$ {abs(total_pagar):,.2f}", # Usa abs para mostrar valor positivo
            'Saldo Total': f"R$ {saldo_total:,.2f}"
        }

        # Transações Agrupadas por Tipo
        resultados['Transações por Tipo'] = df.groupby('tipo')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()

        # Transações Agrupadas por Conta Bancária
        if 'conta_bancaria' in df.columns:
            resultados['Saldo por Conta Bancária'] = df.groupby('conta_bancaria')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        else:
            resultados['Saldo por Conta Bancária'] = "Coluna 'conta_bancaria' não encontrada para agrupamento."

        # Detalhes das Transações (primeiras 10 de cada tipo)
        resultados['Detalhes das Transações (Receitas - Primeiras 10)'] = \
            transacoes_receitas.head(10)
        resultados['Detalhes das Transações (Despesas - Primeiras 10)'] = \
            transacoes_despesas.head(10)

        # Transações por Mês (se houver coluna de data)
        if 'data' in df.columns:
            df['mes_ano'] = df['data'].dt.to_period('M')
            resultados['Transações por Mês'] = df.groupby('mes_ano')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        else:
            resultados['Transações por Mês'] = "Coluna 'data' não encontrada para agrupamento mensal."

        return resultados

    except Exception as e:
        erro_msg = f"Ocorreu um erro ao processar a planilha: {e}"
        print(erro_msg) # Continua imprimindo no console de execução do streamlit
        return {"error": erro_msg} # Retorna um dicionário com a mensagem de erro
# --- FIM DA FUNÇÃO DE ANÁLISE ---

st.set_page_config(layout="wide") # Para usar a largura máxima da tela

st.title("📊 Analisador de Finanças")
st.write("Faça upload de sua planilha de transações financeiras para obter um resumo detalhado.")

uploaded_file = st.file_uploader("Escolha um arquivo Excel ou CSV", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
    st.write(file_details)

    # Usar um tempfile para garantir que o arquivo seja lido corretamente pelo pandas
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name

    # --- NOVA LÓGICA DE CAPTURA DE SAÍDA E TRATAMENTO DE ERROS ---
    console_output = StreamlitConsoleCapture(sys.stdout)
    
    # Redireciona stdout temporariamente para a nossa classe de captura
    with contextlib.redirect_stdout(console_output):
        resultados = analisar_planilha_financeira(temp_path)
    
    captured_text = console_output.getvalue() # Pega tudo que foi "printado"
    
    if resultados and "error" in resultados: # Se a função retornou um dicionário de erro
        st.error(f"**Ocorreu um erro ao processar a planilha:**\n{resultados['error']}")
        if captured_text:
            st.subheader("Detalhes do Console (para depuração):")
            st.code(captured_text) # Mostra a saída do console no Streamlit
    elif resultados: # Se a análise foi bem-sucedida (não é None e não tem chave 'error')
        st.success("Análise concluída com sucesso!")
        
        # --- SEÇÕES DO RELATÓRIO NO STREAMLIT (SEU CÓDIGO ATUAL) ---
        st.header("Sumário Geral")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total a Receber", resultados['Resumo Geral']['Total a Receber'])
        with col2:
            st.metric("Total a Pagar", resultados['Resumo Geral']['Total a Pagar'])
        with col3:
            st.metric("Saldo Total", resultados['Resumo Geral']['Saldo Total'])

        st.header("Transações por Tipo")
        df_tipo = pd.DataFrame(list(resultados['Transações por Tipo'].items()), columns=['Tipo', 'Total'])
        st.table(df_tipo)

        if isinstance(resultados['Saldo por Conta Bancária'], dict):
            st.header("Saldo por Conta Bancária")
            df_contas = pd.DataFrame(list(resultados['Saldo por Conta Bancária'].items()), columns=['Conta', 'Saldo'])
            st.table(df_contas)
        else:
            st.info(resultados['Saldo por Conta Bancária'])

        st.header("Transações por Mês")
        if isinstance(resultados['Transações por Mês'], dict):
            df_mes = pd.DataFrame(list(resultados['Transações por Mês'].items()), columns=['Mês/Ano', 'Total'])
            st.table(df_mes)
        else:
            st.info(resultados['Transações por Mês'])

        st.header("Detalhes das Transações")
        tab1, tab2 = st.tabs(["Receitas", "Despesas"])
        with tab1:
            st.subheader("Receitas (Primeiras 10)")
            if not resultados['Detalhes das Transações (Receitas - Primeiras 10)'].empty:
                st.dataframe(resultados['Detalhes das Transações (Receitas - Primeiras 10)'])
            else:
                st.info("Nenhuma receita encontrada.")
        with tab2:
            st.subheader("Despesas (Primeiras 10)")
            if not resultados['Detalhes das Transações (Despesas - Primeiras 10)'].empty:
                st.dataframe(resultados['Detalhes das Transações (Despesas - Primeiras 10)'])
            else:
                st.info("Nenhuma despesa encontrada.")
        # --- FIM DAS SEÇÕES DO RELATÓRIO ---

        if captured_text: # Mostra a saída do console se houver algo
            st.subheader("Logs da Análise:")
            st.code(captured_text)
    else: # Caso a função retorne None ou algo inesperado
        st.error("Ocorreu um erro desconhecido durante a análise da planilha.")
        if captured_text:
            st.subheader("Detalhes do Console (para depuração):")
            st.code(captured_text)
    
    os.unlink(temp_path) # Limpa o arquivo temporário
    
st.sidebar.markdown("### Créditos")
st.sidebar.write("Este aplicativo foi desenvolvido por Danillo Wozniak Soares.")
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre o Aplicativo")
st.sidebar.write("Este aplicativo permite analisar suas finanças pessoais a partir de uma planilha de transações financeiras.")
st.sidebar.markdown("### Como Usar")
st.sidebar.write("1. Faça upload de uma planilha no formato Excel (.xlsx, .xls) ou CSV (.csv).")
st.sidebar.write("2. O aplicativo irá gerar um resumo detalhado das suas finanças, incluindo totais a receber, a pagar e saldo total.")
st.sidebar.markdown("### Requisitos da planilha")
st.sidebar.write("A planilha deve conter as seguintes colunas:")
st.sidebar.write("- **Valor**: Valores das transações (pode ser chamado de 'quantia', 'montante', etc.)")
st.sidebar.write("- **Data**: Data da transação (pode ser chamado de 'data_transacao', 'data_pagamento', etc.)")
st.sidebar.write("- **Tipo**: Tipo da transação (pode ser chamado de 'categoria', 'natureza', etc.)")
st.sidebar.write("- **Conta Bancária**: (opcional) Conta bancária associada à transação (pode ser chamado de 'conta', 'conta_bancaria', etc.)")
st.sidebar.markdown("### Recursos")
st.sidebar.write("- Resumo Geral das Finanças")
st.sidebar.write("- Transações agrupadas por tipo")
st.sidebar.write("- Saldo por Conta Bancária (se disponível)")
st.sidebar.write("- Detalhes das Transações (primeiras 10 de cada tipo)")
st.sidebar.markdown("### Contato") 
st.sidebar.write("Para feedback ou sugestões, entre em contato com o desenvolvedor.")