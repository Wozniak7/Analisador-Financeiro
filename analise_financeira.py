# -*- coding: utf-8 -*-
"""
Este script Python lê uma planilha de transações financeiras,
interpreta os dados, e os agrupa de forma dinâmica e intuitiva
para o usuário.

Requisitos:
- Python 3.x
- Bibliotecas: pandas, openpyxl

Para instalar as bibliotecas, execute no terminal (com o ambiente virtual ativado):
pip install pandas openpyxl
"""

import pandas as pd
import os

def analisar_planilha_financeira(caminho_arquivo):
    """
    Lê uma planilha de transações financeiras, categoriza e agrupa os dados.

    Args:
        caminho_arquivo (str): O caminho completo para o arquivo da planilha (ex: 'minhas_financas.xlsx').

    Returns:
        dict: Um dicionário contendo os dados financeiros agrupados e resumidos,
              ou None se houver um erro.
    """
    print(f"\nTentando ler o arquivo: {caminho_arquivo}")

    # Verifica se o arquivo existe
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return None

    try:
        # Tenta ler o arquivo Excel ou CSV
        if caminho_arquivo.endswith('.xlsx') or caminho_arquivo.endswith('.xls'):
            df = pd.read_excel(caminho_arquivo)
        elif caminho_arquivo.endswith('.csv'):
            df = pd.read_csv(caminho_arquivo, sep=';')
        else:
            print("Erro: Formato de arquivo não suportado. Por favor, use .xlsx, .xls ou .csv.")
            return None

        print("Arquivo lido com sucesso!")
        print("\nPrimeiras 5 linhas da planilha:")
        print(df.head().to_markdown(index=False)) # Exibe as primeiras linhas para o usuário

        # Normaliza os nomes das colunas para facilitar o acesso
        # Converte para minúsculas e substitui espaços por underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

        # Mapeamento de nomes de colunas esperados para os nomes normalizados
        # O usuário pode precisar ajustar isso conforme a planilha dele
        colunas_esperadas = {
            'valor': ['valor', 'quantia', 'montante'],
            'data': ['data', 'data_transacao', 'data_pagamento', 'data_recebimento'],
            'tipo': ['tipo', 'categoria', 'natureza'],
            'conta_bancaria': ['conta', 'conta_bancaria', 'banco']
        }

        # Encontra as colunas no DataFrame
        colunas_encontradas = {}
        for esperado, possiveis in colunas_esperadas.items():
            for possivel in possiveis:
                if possivel in df.columns:
                    colunas_encontradas[esperado] = possivel
                    break
            if esperado not in colunas_encontradas:
                print(f"Aviso: Não foi possível encontrar a coluna '{esperado}' (tentou: {', '.join(possiveis)}).")
                print("Por favor, verifique os nomes das colunas na sua planilha ou ajuste o mapeamento no script.")
                return None # Retorna None se uma coluna essencial não for encontrada

        # Renomeia as colunas para nomes padronizados no script
        df = df.rename(columns={v: k for k, v in colunas_encontradas.items()})

        # Converte a coluna 'data' para o formato datetime
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            df.dropna(subset=['data'], inplace=True) # Remove linhas com datas inválidas
        else:
            print("Erro: Coluna 'data' não encontrada ou inválida após normalização.")
            return None


        # Garante que a coluna 'valor' é numérica
        if 'valor' in df.columns:
            # 1. Converte para string para garantir que podemos aplicar métodos de string
            df['valor'] = df['valor'].astype(str)
            # 2. Remove "R$", espaços, pontos de milhar e substitui vírgula por ponto decimal
            df['valor'] = df['valor'].str.replace('R$', '', regex=False) \
                                    .str.replace('.', '', regex=False) \
                                    .str.replace(',', '.', regex=False) \
                                    .str.strip() # Remove espaços extras
            # 3. Converte para numérico. Se não conseguir, coloca NaN
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            # 4. Remove linhas onde a conversão falhou
            df.dropna(subset=['valor'], inplace=True)
        else:
            print("Erro: Coluna 'valor' não encontrada ou inválida após normalização.")
            return None

        # Identifica e categoriza 'valores a receber' e 'valores a pagar'
        # Assumimos que existe uma coluna 'tipo' que indica se é 'receita', 'despesa', etc.
        # Ou, se não houver, podemos inferir pelo sinal do valor (se for o caso)
        if 'tipo' in df.columns:
            df['tipo'] = df['tipo'].astype(str).str.lower().str.strip()
            df['tipo'] = df['tipo'].str.replace(r'[^a-z\s]', '', regex=True).str.strip()
            mapeamento_tipo = {
                'receita': 'Receita', 'entrada': 'Receita', 'ganho': 'Receita',
                'pagamento': 'Despesa', 'despesa': 'Despesa', 'saida': 'Despesa', 'gasto': 'Despesa'
            }
            df['tipo'] = df['tipo'].map(mapeamento_tipo).fillna('Outros')
        else:
            # Se 'tipo' não existir, infere baseando-se no valor (positivo=Receita, negativo=Despesa)
            print("Aviso: Coluna 'tipo' não encontrada. Inferindo tipo pelo sinal do 'valor'.")
            df['tipo'] = df['valor'].apply(lambda x: 'Receita' if x >= 0 else 'Despesa')

        # Separa transações em 'receitas' e 'despesas' baseadas no tipo inferido/mapeado
        transacoes_receitas = df[df['tipo'] == 'Receita'].copy()
        transacoes_despesas = df[df['tipo'] == 'Despesa'].copy()

        resultados = {}

        # 1. Resumo Geral
        total_receber = transacoes_receitas['valor'].sum()
        # Para o total a pagar, somamos os valores negativos das despesas.
        # O `abs()` será usado apenas na exibição.
        total_pagar = transacoes_despesas['valor'].sum()
        saldo_total = total_receber + total_pagar

        resultados['Resumo Geral'] = {
            'Total a Receber': f"R$ {total_receber:,.2f}",
            'Total a Pagar': f"R$ {abs(total_pagar):,.2f}", # Usa abs para mostrar valor positivo
            'Saldo Total': f"R$ {saldo_total:,.2f}"
        }

        # 2. Transações Agrupadas por Tipo
        resultados['Transações por Tipo'] = df.groupby('tipo')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()

        # 3. Transações Agrupadas por Conta Bancária
        if 'conta_bancaria' in df.columns:
            resultados['Saldo por Conta Bancária'] = df.groupby('conta_bancaria')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        else:
            resultados['Saldo por Conta Bancária'] = "Coluna 'conta_bancaria' não encontrada para agrupamento."

        # 4. Detalhes das Transações (primeiras 10 de cada tipo)
        resultados['Detalhes das Transações (Receitas - Primeiras 10)'] = \
            transacoes_receitas.head(10).to_markdown(index=False)
        resultados['Detalhes das Transações (Despesas - Primeiras 10)'] = \
            transacoes_despesas.head(10).to_markdown(index=False)

        # 5. Transações por Mês (se houver coluna de data)
        if 'data' in df.columns:
            df['mes_ano'] = df['data'].dt.to_period('M')
            resultados['Transações por Mês'] = df.groupby('mes_ano')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        else:
            resultados['Transações por Mês'] = "Coluna 'data' não encontrada para agrupamento mensal."

        return resultados

    except Exception as e:
        print(f"Ocorreu um erro ao processar a planilha: {e}")
        return None

def exibir_resultados(resultados):
    """
    Exibe os resultados da análise de forma intuitiva.
    """
    if not resultados:
        print("\nNenhum resultado para exibir.")
        return

    print("\n" + "="*50)
    print("           RELATÓRIO FINANCEIRO           ")
    print("="*50)

    for titulo, conteudo in resultados.items():
        print(f"\n--- {titulo} ---")
        if isinstance(conteudo, dict):
            for chave, valor in conteudo.items():
                print(f"- {chave}: {valor}")
        elif isinstance(conteudo, str) and conteudo.startswith('|'): # Provavelmente um markdown table
            print(conteudo)
        else:
            print(conteudo)
    print("\n" + "="*50)
    print("           Análise Concluída!           ")
    print("="*50)

if __name__ == "__main__":
    print("Bem-vindo ao Analisador de Planilhas Financeiras!")
    print("Este script irá ajudá-lo a organizar seus dados financeiros.")

    # Solicita o caminho do arquivo ao usuário
    caminho_planilha = input("\nPor favor, digite o caminho completo da sua planilha (ex: C:\\Users\\SeuUsuario\\Documentos\\minhas_financas.xlsx): ")

    # Chama a função para analisar a planilha
    dados_analisados = analisar_planilha_financeira(caminho_planilha)

    # Exibe os resultados
    exibir_resultados(dados_analisados)

    print("\nPressione Enter para sair...")
    input() # Mantém a janela do console aberta até o usuário pressionar Enter
