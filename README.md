# 📊 Analisador de Finanças Pessoais + Central de Utilidades

🚀 **Visão Geral do Projeto**  
Este projeto é um aplicativo web interativo, desenvolvido com **Streamlit**, que começou como uma ferramenta de análise de finanças pessoais, mas evoluiu para uma **central multifuncional**. Agora, além de analisar planilhas financeiras, ele também oferece diversas funcionalidades úteis do dia a dia: clima, cotações, geradores e muito mais!

Ideal para quem busca uma **plataforma simples, poderosa e versátil** para controle financeiro e utilidades rápidas.

🔗 **Acesse aqui:**  
**https://simplifinancas.streamlit.app/**

---

## ✨ Funcionalidades Principais

### 📈 Finanças Pessoais
- **Resumo Geral Instantâneo:** Total a Receber, Total a Pagar e Saldo Total.
- **Análise por Tipo:** Distribuição entre Receitas e Despesas.
- **Desempenho Mensal:** Acompanhamento financeiro mês a mês.
- **Saldo por Conta Bancária:** (para planilhas de transações).
- **Detalhamento das Transações:** Visualize as primeiras linhas de suas movimentações.
- **Suporte a Múltiplos Formatos:** Planilhas de extratos e orçamentos mensais.

### 🔍 Consultas e Utilidades Extras
- **🌤️ Clima Atual:** Veja a previsão do tempo por cidade.
- **💱 Cotação de Moedas:** Dólar, Euro e outras moedas em tempo real.
- **📉 Cotações de Ações & Criptomoedas:** Acompanhe o mercado financeiro.
- **😂 Geração de Conteúdo Aleatório:** Piadas, contos e frases motivacionais.
- **🎬 Filmes & Séries:** Busque por títulos, resumos e avaliações.
- **🧾 Geradores Diversos:**
  - CPF e CNPJ válidos
  - Senhas fortes
  - QR Codes personalizados

---

## 📝 Como Usar

1. **Acesse o Aplicativo:** Use o link acima ou rode localmente (veja a seção de instalação).
2. **Escolha a Funcionalidade no Menu Lateral.**
3. **Para Análise Financeira:**
   - Faça o upload da sua planilha (Extrato ou Orçamento).
   - O sistema processa os dados automaticamente e exibe os gráficos.
4. **Para Utilidades:**  
   - Preencha os dados solicitados (ex.: cidade, moeda, texto) e veja os resultados na tela.

---

## 📊 Formatos de Planilha Suportados

### 📄 Planilha de Transações (Extrato)
- **Formatos:** `.xlsx`, `.xls`, `.csv`
- **Separador CSV:** `;` (ponto e vírgula)
- **Colunas esperadas:**  
  - `Valor` (ou: quantia, montante)  
  - `Data` (ou: data_transacao, data_pagamento, data_recebimento)  
  - `Tipo` (ou: categoria, natureza)  
  - `Conta Bancária` (opcional)  
  - `Descrição` (opcional)

### 📑 Planilha de Orçamento (Mensal)
- **Formato:** Apenas `.xlsx` ou `.xls`
- **Estrutura Esperada:**
  - Seções distintas para **Receitas** e **Despesas**
  - Categorias nas linhas (Ex.: Moradia, Lazer)
  - Meses como colunas (Ex.: Janeiro, Fevereiro)

---

## 🛠️ Instalação Local

```bash
# Clone o repositório
git clone https://github.com/Wozniak7/Analisador-Financeiro.git
cd Analisador-Financeiro

# Crie e ative o ambiente virtual
python -m venv venv

# Ative o ambiente:
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

```
---

## 📦 requirements.txt

- `streamlit`
- `pandas`
- `openpyxl`
- `requests`
- `qrcode`

## 🚀 Execute o app:

- `streamlit run app_streamlit.py`

---

## 🤝 Contribuição
Contribuições são muito bem-vindas!
Sinta-se à vontade para:

Abrir issues com sugestões ou bugs

Enviar pull requests com novas ideias e melhorias

## 👨‍💻 Desenvolvedor
**Danillo Wozniak Soares**
*🔗 GitHub: @Wozniak7*