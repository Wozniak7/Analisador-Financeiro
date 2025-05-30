import streamlit as st
import pandas as pd
import os
import io
import contextlib
import sys
import tempfile
import calendar # Para mapear nomes de meses para números
import matplotlib.pyplot as plt

# Classe para capturar a saída do console (mantida)
class StreamlitConsoleCapture(io.StringIO):
    def __init__(self, target_stream=None):
        super().__init__()
        self.target_stream = target_stream

    def write(self, s):
        super().write(s)
        if self.target_stream:
            self.target_stream.write(s)

    def flush(self):
        super().flush()
        if self.target_stream:
            self.target_stream.flush()

# --- FUNÇÃO 1: Análise de Planilha de Transações (seu código atual, refatorado) ---
# Adicionado num_transacoes_exibir como parâmetro
def analisar_planilha_transacoes(caminho_arquivo, num_transacoes_exibir=10):
    print(f"\nTentando ler arquivo de TRANSAÇÕES: {caminho_arquivo}")
    try:
        if caminho_arquivo.endswith('.xlsx') or caminho_arquivo.endswith('.xls'):
            df = pd.read_excel(caminho_arquivo)
        elif caminho_arquivo.endswith('.csv'):
            try:
                # Tentativa de leitura com separador e decimal específicos
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', decimal=',', thousands='.')
            except Exception as e:
                print(f"Aviso: Falha na leitura avançada do CSV: {e}. Tentando leitura básica...")
                # Tentativa de leitura básica para CSV
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
        else:
            return {"error": "Formato de arquivo não suportado. Por favor, use .xlsx, .xls ou .csv."}

        print("Arquivo de transações lido com sucesso!")

        # Normaliza os nomes das colunas
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

        # --- AJUSTE: Adicionado 'descricao' como coluna esperada separada ---
        colunas_esperadas = {
            'valor': ['valor', 'quantia', 'montante'],
            'data': ['data', 'data_transacao', 'data_pagamento', 'data_recebimento'],
            'tipo': ['tipo', 'categoria', 'natureza'],
            'conta_bancaria': ['conta', 'conta_bancaria', 'banco'],
            'descricao': ['descricao', 'item', 'detalhe', 'observacao', 'finalidade'] # Mais nomes para descrição
        }

        colunas_encontradas = {}
        for esperado, possiveis in colunas_esperadas.items():
            for possivel in possiveis:
                if possivel in df.columns:
                    colunas_encontradas[esperado] = possivel
                    break
            if esperado not in colunas_encontradas:
                print(f"Aviso: Não foi possível encontrar a coluna '{esperado}' (tentou: {', '.join(possiveis)}).")
                if esperado in ['valor', 'data']: # Colunas essenciais
                    return {"error": f"Coluna essencial '{esperado}' não encontrada. Verifique os nomes das colunas na sua planilha."}

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
            return {"error": "Coluna 'valor' não encontrada ou inválida após normalização."}

        # Processamento da coluna 'data'
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
            df.dropna(subset=['data'], inplace=True)
            df['data_br'] = df['data'].dt.strftime('%d/%m/%Y')
        else:
            return {"error": "Coluna 'data' não encontrada ou inválida após normalização."}

        # Processamento da coluna 'descricao' (garante que seja string e trata nulos)
        if 'descricao' in df.columns:
            df['descricao'] = df['descricao'].astype(str).fillna('').str.strip()
        else:
            # Se 'descricao' não for encontrada, cria uma coluna vazia para evitar erros posteriores
            df['descricao'] = '' 

        # Padroniza a coluna 'tipo' ou infere
        if 'tipo' in df.columns:
            df['tipo_original'] = df['tipo'].astype(str).str.lower().str.strip()
            df['tipo_original'] = df['tipo_original'].str.replace(r'[^a-z\s]', '', regex=True).str.strip()

            mapeamento_tipo = {
                'receita': 'Receita', 'entrada': 'Receita', 'ganho': 'Receita',
                'pagamento': 'Despesa', 'despesa': 'Despesa', 'saida': 'Despesa', 'gasto': 'Despesa'
            }
            df['tipo_categorizado'] = df['tipo_original'].map(mapeamento_tipo).fillna('Outros')
            df['tipo'] = df.apply(lambda row: 'Despesa' if row['valor'] < 0 else row['tipo_categorizado'], axis=1)
        else:
            print("Aviso: Coluna 'tipo' não encontrada. Inferindo tipo pelo sinal do 'valor'.")
            df['tipo'] = df['valor'].apply(lambda x: 'Receita' if x >= 0 else 'Despesa')

        if 'tipo_original' in df.columns:
            df.drop(columns=['tipo_original'], inplace=True)
        if 'tipo_categorizado' in df.columns:
            df.drop(columns=['tipo_categorizado'], inplace=True)

        transacoes_receitas = df[df['tipo'] == 'Receita'].copy()
        transacoes_despesas = df[df['tipo'] == 'Despesa'].copy()

        # Selecionar e reordenar colunas para exibição, usando 'data_br'
        colunas_exibicao = ['data_br', 'valor', 'tipo']
        if 'conta_bancaria' in df.columns:
            colunas_exibicao.append('conta_bancaria')
        if 'descricao' in df.columns:
            colunas_exibicao.append('descricao')
        
        # Garante que as colunas existam no dataframe antes de selecionar
        colunas_exibicao_receitas = [col for col in colunas_exibicao if col in transacoes_receitas.columns]
        colunas_exibicao_despesas = [col for col in colunas_exibicao if col in transacoes_despesas.columns]

        transacoes_receitas = transacoes_receitas[colunas_exibicao_receitas].rename(columns={'data_br': 'data'})
        transacoes_despesas = transacoes_despesas[colunas_exibicao_despesas].rename(columns={'data_br': 'data'})


        resultados = {}
        total_receber = transacoes_receitas['valor'].sum()
        total_pagar = transacoes_despesas['valor'].sum()
        saldo_total = total_receber + total_pagar

        resultados['Resumo Geral'] = {
            'Total a Receber': f"R$ {total_receber:,.2f}",
            'Total a Pagar': f"R$ {abs(total_pagar):,.2f}",
            'Saldo Total': f"R$ {saldo_total:,.2f}"
        }
        resultados['Transações por Tipo'] = df.groupby('tipo')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        
        if 'conta_bancaria' in df.columns:
            resultados['Saldo por Conta Bancária'] = df.groupby('conta_bancaria')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        else:
            resultados['Saldo por Conta Bancária'] = "Coluna 'conta_bancaria' não encontrada para agrupamento."

        # --- AJUSTE: Retorna DataFrame completo ou head(num_transacoes_exibir) ---
        if num_transacoes_exibir == 0: # Se 0, exibe todas
            resultados['Detalhes das Transações (Receitas)'] = transacoes_receitas
            resultados['Detalhes das Transações (Despesas)'] = transacoes_despesas
        else:
            resultados['Detalhes das Transações (Receitas)'] = transacoes_receitas.head(num_transacoes_exibir)
            resultados['Detalhes das Transações (Despesas)'] = transacoes_despesas.head(num_transacoes_exibir)

        # --- NOVO: Agrupamento de Despesas por Descrição ---
        if 'descricao' in df.columns and not transacoes_despesas.empty:
            despesas_por_descricao = transacoes_despesas.groupby('descricao')['valor'].sum().abs().sort_values(ascending=False).reset_index()
            despesas_por_descricao['valor'] = despesas_por_descricao['valor'].apply(lambda x: f"R$ {x:,.2f}")
            resultados['Despesas Agrupadas por Descrição'] = despesas_por_descricao
        else:
            resultados['Despesas Agrupadas por Descrição'] = "Coluna 'descricao' não encontrada ou nenhuma despesa para agrupar."


        if 'data' in df.columns:
            df['mes_ano'] = df['data'].dt.to_period('M')
            resultados['Transações por Mês'] = df.groupby('mes_ano')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        else:
            resultados['Transações por Mês'] = "Coluna 'data' não encontrada para agrupamento mensal."

        return resultados

    except Exception as e:
        erro_msg = f"Ocorreu um erro ao processar a planilha de transações: {e}"
        print(erro_msg)
        return {"error": erro_msg}

# --- FUNÇÃO 2: Análise de Planilha de Orçamento (Mantida como estava) ---
def analisar_planilha_orcamento(caminho_arquivo):
    print(f"\nTentando ler arquivo de ORÇAMENTO: {caminho_arquivo}")

    if not (caminho_arquivo.endswith('.xlsx') or caminho_arquivo.endswith('.xls')):
        return {"error": "A Planilha de Orçamento (Mensal) deve ser um arquivo Excel (.xlsx ou .xls). Arquivos CSV não são suportados para este tipo de planilha devido à sua estrutura complexa."}

    try:
        nome_para_numero_mes = {name.lower(): num for num, name in enumerate(calendar.month_name) if num}
        
        df_despesas_raw = pd.read_excel(caminho_arquivo, header=1, skiprows=[0], usecols="A:M")
        df_despesas_raw = df_despesas_raw.rename(columns={df_despesas_raw.columns[0]: 'categoria'})
        df_despesas_raw = df_despesas_raw.dropna(subset=['categoria'])
        df_despesas_raw = df_despesas_raw[~df_despesas_raw['categoria'].str.contains('Total', na=False, case=False)]

        meses_colunas_despesas = df_despesas_raw.columns[1:13].tolist()

        for col in meses_colunas_despesas:
            temp_series = df_despesas_raw[col].astype(str)
            temp_series = temp_series.str.replace('R$', '', regex=False) \
                                     .str.replace('.', '', regex=False) \
                                     .str.replace(',', '.', regex=False) \
                                     .str.strip()
            df_despesas_raw[col] = pd.to_numeric(temp_series, errors='coerce').fillna(0)

        df_despesas_melted = df_despesas_raw.melt(
            id_vars=['categoria'],
            value_vars=meses_colunas_despesas,
            var_name='mes',
            value_name='valor'
        )
        df_despesas_melted['tipo'] = 'Despesa'
        df_despesas_melted['valor'] = df_despesas_melted['valor'] * -1 

        df_receitas_raw = pd.read_excel(caminho_arquivo, header=17, skiprows=range(17), usecols="A:M")
        df_receitas_raw = df_receitas_raw.rename(columns={df_receitas_raw.columns[0]: 'categoria'})
        df_receitas_raw = df_receitas_raw.dropna(subset=['categoria'])
        df_receitas_raw = df_receitas_raw[~df_receitas_raw['categoria'].str.contains('Total', na=False, case=False)]
        
        meses_colunas_receitas = df_receitas_raw.columns[1:13].tolist()

        for col in meses_colunas_receitas:
            temp_series = df_receitas_raw[col].astype(str)
            temp_series = temp_series.str.replace('R$', '', regex=False) \
                                     .str.replace('.', '', regex=False) \
                                     .str.replace(',', '.', regex=False) \
                                     .str.strip()
            df_receitas_raw[col] = pd.to_numeric(temp_series, errors='coerce').fillna(0)

        df_receitas_melted = df_receitas_raw.melt(
            id_vars=['categoria'],
            value_vars=meses_colunas_receitas,
            var_name='mes',
            value_name='valor'
        )
        df_receitas_melted['tipo'] = 'Receita'

        df_final = pd.concat([df_despesas_melted, df_receitas_melted], ignore_index=True)
        df_final.dropna(subset=['valor'], inplace=True) 

        df_final['num_mes'] = df_final['mes'].str.lower().map(nome_para_numero_mes)
        df_final = df_final.dropna(subset=['num_mes'])
        df_final['data'] = pd.to_datetime(df_final['num_mes'].astype(int).astype(str) + '/1/2025', format='%m/%d/%Y')
        df_final['data_br'] = df_final['data'].dt.strftime('%d/%m/%Y')
        df_final['mes_ano'] = df_final['data'].dt.to_period('M')

        transacoes_receitas = df_final[df_final['tipo'] == 'Receita'].copy()
        transacoes_despesas = df_final[df_final['tipo'] == 'Despesa'].copy()

        colunas_exibicao_orcamento = ['data_br', 'categoria', 'valor', 'tipo']
        
        transacoes_receitas_display = transacoes_receitas[colunas_exibicao_orcamento].rename(columns={'data_br': 'data'})
        transacoes_despesas_display = transacoes_despesas[colunas_exibicao_orcamento].rename(columns={'data_br': 'data'})

        resultados = {}
        total_receber = transacoes_receitas['valor'].sum()
        total_pagar = transacoes_despesas['valor'].sum()
        saldo_total = total_receber + total_pagar

        resultados['Resumo Geral'] = {
            'Total a Receber': f"R$ {total_receber:,.2f}",
            'Total a Pagar': f"R$ {abs(total_pagar):,.2f}",
            'Saldo Total': f"R$ {saldo_total:,.2f}"
        }
        
        resultados['Transações por Tipo'] = df_final.groupby('tipo')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()

        resultados['Saldo por Conta Bancária'] = "Não aplicável para Planilha de Orçamento (sem coluna 'conta_bancaria')."

        resultados['Detalhes das Transações (Receitas)'] = transacoes_receitas_display.head(10) # Manter 10 para o orçamento por ser uma "simulação"
        resultados['Detalhes das Transações (Despesas)'] = transacoes_despesas_display.head(10)
        
        resultados['Transações por Mês'] = df_final.groupby('mes_ano')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        
        return resultados

    except Exception as e:
        erro_msg = f"Ocorreu um erro ao processar a planilha de orçamento: {e}"
        print(erro_msg)
        return {"error": erro_msg}


# --- Streamlit UI ---
st.set_page_config(layout="wide")

st.title("📊 Analisador de Finanças")
st.write("Faça upload de sua planilha financeira para obter um resumo detalhado.")

tipo_planilha_selecionado = st.radio(
    "Qual o tipo de planilha você vai enviar?",
    ("Planilha de Transações", "Planilha de Orçamento (Em Desenvolvimento!)")
)

uploaded_file = st.file_uploader("Escolha um arquivo Excel ou CSV", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name

    console_output = StreamlitConsoleCapture(sys.stdout)
    
    # Variável para controlar o número de transações a exibir, inicializada
    num_transacoes_exibir = 0 # Valor padrão para o slider

    with contextlib.redirect_stdout(console_output):
        if tipo_planilha_selecionado == "Planilha de Transações (Extrato)":
            # --- MOVIDO: Slider para o corpo principal, acima dos detalhes das transações ---
            st.subheader("Opções de Visualização de Transações Detalhadas")
            num_transacoes_exibir = st.slider(
                "Número de transações a exibir (0 = Todas):", 
                0, 500, 10, step=10, # Max 500 para evitar carregar demais, ajuste se precisar
                key='slider_transacoes'
            )
            # Passa o valor do slider para a função de análise
            resultados = analisar_planilha_transacoes(temp_path, num_transacoes_exibir=num_transacoes_exibir)
        else: # "Planilha de Orçamento (Mensal)"
            resultados = analisar_planilha_orcamento(temp_path)
    
    captured_text = console_output.getvalue()
    
    if resultados and "error" in resultados:
        st.error(f"**Ocorreu um erro ao processar a planilha:**\n{resultados['error']}")
        if captured_text:
            st.subheader("Detalhes do Console (para depuração):")
            st.code(captured_text)
    elif resultados:
        st.success("Análise concluída com sucesso!")
        
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

        if isinstance(resultados["Transações por Mês"], dict):
            st.subheader("Gráfico: Saldo por Mês")
            df_grafico = pd.DataFrame({
                "Mês": list(resultados["Transações por Mês"].keys()),
                "Valor": [float(v.replace("R$", "").replace(".", "").replace(",", ".")) for v in resultados["Transações por Mês"].values()]
            })

            fig, ax = plt.subplots()
            df_grafico.plot(x="Mês", y="Valor", kind="bar", ax=ax, color="skyblue", legend=False)
            ax.set_ylabel("Valor (R$)")
            ax.set_title("Evolução Financeira Mensal")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        st.header("Detalhes das Transações")
        st.write("As tabelas abaixo mostram as transações detalhadas, limitadas ao número selecionado no slider no começo da página.")
        # --- AJUSTE: Novas abas e título dinâmico para o dataframe ---
        # Adicionado uma terceira aba para "Despesas por Descrição"
        tab1, tab2, tab3 = st.tabs(["Receitas Detalhadas", "Despesas Detalhadas", "Despesas por Descrição"])

        with tab1:
            # Título dinâmico baseado na seleção do slider
            st.subheader(f"Receitas ({'Todas' if (tipo_planilha_selecionado == 'Planilha de Transações (Extrato)' and num_transacoes_exibir == 0) else f'Primeiras {num_transacoes_exibir}' if tipo_planilha_selecionado == 'Planilha de Transações (Extrato)' else 'Primeiras 10'})")
            if not resultados['Detalhes das Transações (Receitas)'].empty:
                st.dataframe(resultados['Detalhes das Transações (Receitas)'])
            else:
                st.info("Nenhuma receita encontrada.")
        with tab2:
            # Título dinâmico baseado na seleção do slider
            st.subheader(f"Despesas ({'Todas' if (tipo_planilha_selecionado == 'Planilha de Transações (Extrato)' and num_transacoes_exibir == 0) else f'Primeiras {num_transacoes_exibir}' if tipo_planilha_selecionado == 'Planilha de Transações (Extrato)' else 'Primeiras 10'})")
            if not resultados['Detalhes das Transações (Despesas)'].empty:
                st.dataframe(resultados['Detalhes das Transações (Despesas)'])
            else:
                st.info("Nenhuma despesa encontrada.")
        with tab3:
            st.subheader("Despesas Agrupadas por Descrição")
            # --- NOVO: Exibe o agrupamento por descrição ---
            if isinstance(resultados['Despesas Agrupadas por Descrição'], pd.DataFrame):
                if not resultados['Despesas Agrupadas por Descrição'].empty:
                    st.dataframe(resultados['Despesas Agrupadas por Descrição'])
                else:
                    st.info("Nenhuma despesa com descrição encontrada para agrupar.")
            else:
                st.info(resultados['Despesas Agrupadas por Descrição']) # Mensagem se 'descricao' não foi encontrada
        
        if captured_text:
            st.subheader("Logs da Análise:")
            st.code(captured_text)
    else:
        st.error("Ocorreu um erro desconhecido durante a análise da planilha.")
        if captured_text:
            st.subheader("Detalhes do Console (para depuração):")
            st.code(captured_text)
    
    os.unlink(temp_path)
    
st.sidebar.markdown("### Créditos")
st.sidebar.write("Este aplicativo foi desenvolvido por Danillo Wozniak Soares.")
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre o Aplicativo")
st.sidebar.write("Este aplicativo permite analisar suas finanças pessoais a partir de uma planilha de transações financeiras.")
st.sidebar.markdown("### Como Usar")
st.sidebar.write("1. Faça upload de uma planilha no formato Excel (.xlsx, .xls) ou CSV (.csv).")
st.sidebar.write("2. **Selecione o tipo de planilha que você está enviando** (Transações ou Orçamento).")
st.sidebar.write("3. O aplicativo irá gerar um resumo detalhado das suas finanças.")
st.sidebar.markdown("### Requisitos da planilha de Transações (Extrato):")
st.sidebar.write("A planilha deve conter as seguintes colunas:")
st.sidebar.write("- **Valor**: Valores das transações (pode ser chamado de 'quantia', 'montante', etc.)")
st.sidebar.write("- **Data**: Data da transação (pode ser chamado de 'data_transacao', 'data_pagamento', etc.)")
st.sidebar.write("- **Tipo**: Tipo da transação (pode ser chamado de 'categoria', 'natureza', etc.)")
st.sidebar.write("- **Conta Bancária**: (opcional) Conta bancária associada à transação (pode ser chamado de 'conta', 'conta_bancaria', etc.)")
st.sidebar.write("- **Descrição**: (opcional) Uma breve descrição da transação.")
st.sidebar.markdown("### Requisitos da planilha de Orçamento (Mensal):")
st.sidebar.write("A planilha **deve ser um arquivo Excel (.xlsx ou .xls)** e seguir o formato de orçamento mensal (categorias em linhas, meses em colunas), com as seções de Despesas e Receitas bem definidas. A coluna dos meses deve conter os nomes dos meses em português.")
st.sidebar.markdown("### Recursos")
st.sidebar.write("- Resumo Geral das Finanças")
st.sidebar.write("- Transações agrupadas por tipo")
st.sidebar.write("- Saldo por Conta Bancária (se disponível e aplicável)")
st.sidebar.write("- Detalhes das Transações (número de linhas configurável)") # Ajustado
st.sidebar.write("- Despesas Agrupadas por Descrição") # Novo
st.sidebar.write("- Transações por Mês")
st.sidebar.markdown("### Contato") 
st.sidebar.write("Para feedback ou sugestões, entre em contato com o desenvolvedor.")
st.sidebar.markdown("### Licença")
st.sidebar.write("Este aplicativo é de código aberto e gratuito para uso pessoal. Consulte o repositório para mais detalhes.")