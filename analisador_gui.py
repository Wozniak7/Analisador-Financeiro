# -*- coding: utf-8 -*-
"""
Este script Python lê uma planilha de transações financeiras,
interpreta os dados, e os agrupa de forma dinâmica e intuitiva
para o usuário.

Requisitos:
- Python 3.x
- Bibliotecas: pandas, openpyxl, tabulate (já instaladas)
- Tkinter (já vem com o Python)
"""

import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# --- FUNÇÕES DE ANÁLISE (DO SEU SCRIPT EXISTENTE) ---

def analisar_planilha_financeira(caminho_arquivo):
    """
    Lê uma planilha de transações financeiras, categoriza e agrupa os dados.
    (Conteúdo da sua função analisar_planilha_financeira atualizado)
    """
    print(f"\nTentando ler o arquivo: {caminho_arquivo}")

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return None

    try:
        # Tenta ler o arquivo Excel ou CSV
        if caminho_arquivo.endswith('.xlsx') or caminho_arquivo.endswith('.xls'):
            df = pd.read_excel(caminho_arquivo)
        elif caminho_arquivo.endswith('.csv'):
            try:
                # Tenta ler com ';' como separador e inferir o decimal/milhar (como fizemos para corrigir)
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', decimal=',', thousands='.')
            except Exception as e:
                print(f"Aviso: Falha na leitura avançada do CSV: {e}. Tentando leitura básica...")
                df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8')
        else:
            print("Erro: Formato de arquivo não suportado. Por favor, use .xlsx, .xls ou .csv.")
            return None

        print("Arquivo lido com sucesso!")
        # Não precisa mais do print das primeiras linhas aqui, a GUI vai mostrar
        # print("\nPrimeiras 5 linhas da planilha:")
        # print(df.head().to_markdown(index=False))

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
                return None

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
            return None

        # Processamento da coluna 'data'
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
            df.dropna(subset=['data'], inplace=True)
        else:
            print("Erro: Coluna 'data' não encontrada ou inválida após normalização.")
            return None

        # Padroniza a coluna 'tipo' ou infere
        if 'tipo' in df.columns:
            df['tipo_original'] = df['tipo'].astype(str).str.lower().str.strip()
            df['tipo_original'] = df['tipo_original'].str.replace(r'[^a-z\s]', '', regex=True).str.strip()

            mapeamento_tipo = {
                'receita': 'Receita', 'entrada': 'Receita', 'ganho': 'Receita',
                'pagamento': 'Despesa', 'despesa': 'Despesa', 'saida': 'Despesa', 'gasto': 'Despesa'
            }
            df['tipo_categorizado'] = df['tipo_original'].map(mapeamento_tipo).fillna('Outros')
            
            # Correção final: Se o valor for negativo, force como Despesa
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

        resultados['Detalhes das Transações (Receitas - Primeiras 10)'] = \
            transacoes_receitas.head(10).to_markdown(index=False)
        resultados['Detalhes das Transações (Despesas - Primeiras 10)'] = \
            transacoes_despesas.head(10).to_markdown(index=False)

        if 'data' in df.columns:
            df['mes_ano'] = df['data'].dt.to_period('M')
            resultados['Transações por Mês'] = df.groupby('mes_ano')['valor'].sum().apply(lambda x: f"R$ {x:,.2f}").to_dict()
        else:
            resultados['Transações por Mês'] = "Coluna 'data' não encontrada para agrupamento mensal."

        return resultados

    except Exception as e:
        print(f"Ocorreu um erro ao processar a planilha: {e}")
        return None

# --- FUNÇÃO DA INTERFACE GRÁFICA ---

def criar_gui():
    def selecionar_arquivo():
        filepath = filedialog.askopenfilename(
            title="Selecione a planilha financeira",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Arquivos CSV", "*.csv")]
        )
        if filepath:
            entrada_caminho_arquivo.delete(0, tk.END)
            entrada_caminho_arquivo.insert(0, filepath)

    def analisar():
        caminho_arquivo = entrada_caminho_arquivo.get()
        if not caminho_arquivo:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo de planilha.")
            return

        resultados_text.delete(1.0, tk.END) # Limpa a área de texto anterior
        resultados_text.insert(tk.END, "Analisando planilha...\n")

        dados_analisados = analisar_planilha_financeira(caminho_arquivo)

        if dados_analisados:
            relatorio_str = formatar_resultados_para_gui(dados_analisados)
            resultados_text.insert(tk.END, relatorio_str)
            messagebox.showinfo("Sucesso", "Análise concluída com sucesso!")
        else:
            resultados_text.insert(tk.END, "Ocorreu um erro durante a análise. Verifique o console para mais detalhes.")
            messagebox.showerror("Erro", "Falha na análise da planilha. Verifique o console.")

    def formatar_resultados_para_gui(resultados):
        output = []
        output.append("="*50)
        output.append("           RELATÓRIO FINANCEIRO           ")
        output.append("="*50)

        for titulo, conteudo in resultados.items():
            output.append(f"\n--- {titulo} ---")
            if isinstance(conteudo, dict):
                for chave, valor in conteudo.items():
                    output.append(f"- {chave}: {valor}")
            elif isinstance(conteudo, str) and conteudo.startswith('|'): # Provavelmente um markdown table
                output.append(conteudo)
            else:
                output.append(str(conteudo)) # Converte para string para garantir
        output.append("\n" + "="*50)
        output.append("           Análise Concluída!           ")
        output.append("="*50)
        return "\n".join(output)

    # Configuração da janela principal
    root = tk.Tk()
    root.title("Analisador de Finanças")
    root.geometry("800x600") # Largura x Altura

    # Frame para seleção de arquivo
    frame_selecao = tk.Frame(root, padx=10, pady=10)
    frame_selecao.pack(pady=10)

    label_caminho = tk.Label(frame_selecao, text="Caminho da Planilha:")
    label_caminho.pack(side=tk.LEFT)

    entrada_caminho_arquivo = tk.Entry(frame_selecao, width=60)
    entrada_caminho_arquivo.pack(side=tk.LEFT, padx=5)

    botao_selecionar = tk.Button(frame_selecao, text="Selecionar Arquivo", command=selecionar_arquivo)
    botao_selecionar.pack(side=tk.LEFT)

    # Botão de Análise
    botao_analisar = tk.Button(root, text="Analisar Planilha", command=analisar, font=("Arial", 12, "bold"))
    botao_analisar.pack(pady=10)

    # Área para exibir resultados
    resultados_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=25, font=("Courier New", 10))
    resultados_text.pack(pady=10)

    # Inicia o loop principal da interface
    root.mainloop()

# --- Execução do Script ---
if __name__ == "__main__":
    criar_gui()