# 📊 Analisador de Finanças Pessoais
🚀 Visão Geral do Projeto
Este projeto é um aplicativo web interativo, desenvolvido com Streamlit, que permite aos usuários analisar suas finanças pessoais de forma rápida e intuitiva. Basta fazer o upload de uma planilha (de transações diárias ou de orçamento mensal) para obter um resumo detalhado, insights sobre seus gastos e receitas, e visualizar o desempenho financeiro ao longo do tempo.

Ideal para quem busca uma ferramenta simples e eficaz para o controle orçamentário e a saúde financeira!

---

# ✨ Funcionalidades Principais
Resumo Geral Instantâneo: Visualize rapidamente o Total a Receber, Total a Pagar e o Saldo Total.
Análise por Tipo: Veja a distribuição de suas transações entre Receitas e Despesas.
Desempenho Mensal: Acompanhe o fluxo financeiro mês a mês.
Saldo por Conta Bancária: (Disponível para planilhas de transações) Obtenha o saldo consolidado por cada conta.
Detalhes das Transações: Visualize as primeiras linhas das suas transações de Receitas e Despesas.
Suporte a Múltiplos Formatos: Processa tanto extratos de transações quanto planilhas de orçamento mensal.

---

# 📝 Como Usar
**É muito simples começar a analisar suas finanças!**

Acesse o Aplicativo: Se o aplicativo estiver online (no Streamlit Community Cloud, por exemplo), acesse a URL. Se estiver rodando localmente, siga as instruções de instalação abaixo.
Faça o Upload da Sua Planilha: No campo "Escolha um arquivo Excel ou CSV", faça o upload do seu arquivo financeiro.
Selecione o Tipo de Planilha:
Se for um Extrato de Transações (Extrato), selecione a opção correspondente.
Se for uma Planilha de Orçamento (Mensal), selecione essa opção.
Visualize a Análise: O aplicativo processará seus dados e exibirá os resumos e gráficos automaticamente.

---

# 📊 Formatos de Planilha Suportados
**Para garantir uma análise precisa, suas planilhas devem seguir as seguintes estruturas:**

[1.] Planilha de Transações (Extrato)
Este formato é ideal para extratos bancários ou listas de transações diárias.

Formatos Aceitos: .xlsx, .xls (Excel) ou .csv (CSV).
Para CSV, o aplicativo espera o separador ; (ponto e vírgula), decimal , (vírgula) e milhar . (ponto).
Colunas Esperadas (nomes alternativos aceitos):
Valor (ou quantia, montante)
Data (ou data_transacao, data_pagamento, data_recebimento)
Tipo (ou categoria, natureza)
Conta Bancária (opcional, ou conta, conta_bancaria, banco, descricao)
Descrição (opcional)

[2.] Planilha de Orçamento (Mensal)
Este formato é para orçamentos planejados com categorias em linhas e meses em colunas.

*⚠️ IMPORTANTE: Deve ser um arquivo Excel (.xlsx ou .xls). Arquivos CSV não são suportados para este tipo de planilha devido à sua estrutura complexa (células mescladas, múltiplas seções, etc.).*

**Estrutura Esperada:**
Deve conter seções claras para Despesas e Receitas.
As categorias (e.g., Moradia, Salário) devem estar em colunas específicas.
Os meses (e.g., Janeiro, Fevereiro, Março) devem ser colunas distintas para cada período.
A planilha deve ser organizada de forma que o cabeçalho dos meses e as categorias de despesas/receitas possam ser identificados, similar ao modelo mostrado na imagem image_bc6c35.png (se você tiver essa imagem no seu repositório).

---

# 🛠️ Instalação (para rodar localmente)
Para executar este projeto em sua máquina local, siga os passos abaixo:

Clone o Repositório:

**Bash**

- `git clone https://github.com/Wozniak7/Analisador-Financeiro.git`
- `cd SeuRepositorio`

Crie e Ative um Ambiente Virtual (Recomendado):

**Bash**

- `python -m venv venv`

# No Windows:
- `.\venv\Scripts\activate`
# No macOS/Linux:
- `source venv/bin/activate`

Instale as Dependências:

**Bash**

- `pip install -r requirements.txt`
*Crie um arquivo requirements.txt na raiz do seu projeto com o seguinte conteúdo:*

- `streamlit`
- `pandas`
- `openpyxl`

*Execute o Aplicativo Streamlit:*

**Bash**

- `streamlit run app_streamlit.py`
Isso abrirá o aplicativo em seu navegador padrão.

---

# 🤝 Contribuição
**Contribuições são bem-vindas! Sinta-se à vontade para abrir issues para bugs ou sugestões, ou enviar pull requests.**

# 👨‍💻 Desenvolvedor
Este aplicativo foi desenvolvido por:

**Danillo Wozniak Soares**