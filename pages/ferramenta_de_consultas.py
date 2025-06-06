import streamlit as st
import requests
import json
import pandas as pd
import yfinance as yf
import plotly.express as px
import io
import env # Para manipulação de imagens (ícones do clima, pôsteres)
import random # Importado para gerar números aleatórios

st.set_page_config(page_title="Meu Portfólio de APIs", layout="wide")

st.title("🚀 Meu Portfólio de Aplicativos de API")
st.markdown("Explore diferentes ferramentas de consulta de dados em tempo real.")

# --- Configurações das Chaves de API ---
# INSTRUÇÕES IMPORTANTES:
# Para que este aplicativo funcione, você precisará obter e colar suas chaves de API nos campos abaixo.
# Mantenha suas chaves de API seguras e nunca as compartilhe em repositórios públicos!

# 1. OpenWeatherMap API Key (para Consulta de Clima)
#    Obtenha em: https://openweathermap.org/api
OPENWEATHER_API_KEY = env.OPENWEATHER_API_KEY if hasattr(env, 'OPENWEATHER_API_KEY') else "SUA_CHAVE_OPENWEATHER_AQUI"

# 2. ExchangeRate-API Key (para Conversor de Moedas)
EXCHANGERATE_API_KEY = env.EXCHANGERATE_API_KEY if hasattr(env, 'EXCHANGERATE_API_KEY') else "SUA_CHAVE_EXCHANGERATE_AQUI"

# 3. OMDb API Key (para Buscador de Filmes/Séries)
OMDB_API_KEY = env.OMDB_API_KEY if hasattr(env, 'OMDB_API_KEY') else "SUA_CHAVE_OMDB_AQUI"

# --- Navegação na Barra Lateral ---
st.sidebar.title("Escolha uma Ferramenta")
app_mode = st.sidebar.radio(
    "Navegação:",
    ["☀️ Consulta de Clima",
     "💱 Conversor de Moedas",
     "📈 Cotação de Ações/Criptomoedas",
     "💡 Fatos/Citações/Piadas Aleatórias",
     "🎬 Buscador de Filmes/Séries"]
)

# --- Seção: Consulta de Clima ---
if app_mode == "☀️ Consulta de Clima":
    st.header("☀️ Consulta de Clima")
    st.markdown("Obtenha informações do clima em tempo real para qualquer cidade do mundo.")

    city = st.text_input("Nome da Cidade:", "São Paulo", key="weather_city_input")

    @st.cache_data(ttl=3600) # Cache por 1 hora para dados de clima
    def get_weather_data(city_name, api_key):
        BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city_name,
            "appid": api_key,
            "units": "metric", # Celsius
            "lang": "pt_br"   # Português
        }
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401: st.error("Erro na API: Chave de API OpenWeatherMap inválida ou ausente.")
            elif response.status_code == 404: st.error(f"Erro: Cidade '{city_name}' não encontrada.")
            else: st.error(f"Erro HTTP inesperado: {http_err}")
            return None
        except requests.exceptions.RequestException as e: st.error(f"Ocorreu um erro na requisição: {e}"); return None

    if st.button("Consultar Clima", key="weather_button"):
        if OPENWEATHER_API_KEY == "SUA_CHAVE_OPENWEATHER_AQUI" or not OPENWEATHER_API_KEY:
            st.warning("Por favor, insira sua chave de API do OpenWeatherMap no código.")
        elif city:
            with st.spinner(f"Buscando clima para {city}..."):
                weather_data = get_weather_data(city, OPENWEATHER_API_KEY)
                if weather_data:
                    st.subheader(f"Clima em {weather_data['name']}, {weather_data['sys']['country']}")
                    col1, col2, col3 = st.columns(3)
                    with col1: st.metric("Temperatura", f"{weather_data['main']['temp']:.1f}°C")
                    with col2: st.metric("Sensação Térmica", f"{weather_data['main']['feels_like']:.1f}°C")
                    with col3: st.metric("Umidade", f"{weather_data['main']['humidity']}%")
                    st.write(f"**Condição:** {weather_data['weather'][0]['description'].capitalize()}")
                    st.write(f"**Velocidade do Vento:** {weather_data['wind']['speed']:.1f} m/s")
                    icon_code = weather_data['weather'][0]['icon']
                    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                    st.image(icon_url, width=100)
        else: st.warning("Por favor, digite o nome de uma cidade.")

# --- Seção: Conversor de Moedas ---
elif app_mode == "💱 Conversor de Moedas":
    st.header("💱 Conversor de Moedas em Tempo Real")
    st.markdown("Converta valores entre diferentes moedas com taxas de câmbio atualizadas.")

    # Lista de moedas comuns (pode ser expandida)
    common_currencies = ["USD", "EUR", "BRL", "GBP", "JPY", "CAD", "AUD", "CHF"]
    
    amount = st.number_input("Valor a Converter:", min_value=0.01, value=1.0, step=0.01, key="currency_amount")
    from_currency = st.selectbox("De:", options=common_currencies, index=0, key="from_currency") # USD
    to_currency = st.selectbox("Para:", options=common_currencies, index=2, key="to_currency") # BRL

    @st.cache_data(ttl=3600) # Cache por 1 hora para taxas de câmbio
    def get_exchange_rate(from_curr, to_curr, api_key):
        if not api_key or api_key == "SUA_CHAVE_EXCHANGERATE_AQUI":
            st.error("Chave de API ExchangeRate-API inválida ou ausente.")
            return None
        API_URL = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}"
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            if data["result"] == "success":
                return data["conversion_rate"]
            else:
                st.error(f"Erro na API de Câmbio: {data.get('error-type', 'Erro desconhecido')}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Ocorreu um erro na requisição de câmbio: {e}")
            return None

    if st.button("Converter", key="convert_button"):
        if EXCHANGERATE_API_KEY == "SUA_CHAVE_EXCHANGERATE_AQUI" or not EXCHANGERATE_API_KEY:
            st.warning("Por favor, insira sua chave de API do ExchangeRate-API no código.")
        else:
            with st.spinner("Convertendo..."):
                rate = get_exchange_rate(from_currency, to_currency, EXCHANGERATE_API_KEY)
                if rate:
                    converted_amount = amount * rate
                    st.success(f"{amount:.2f} {from_currency} = **{converted_amount:.2f} {to_currency}**")
                    st.info(f"Taxa de Câmbio: 1 {from_currency} = {rate:.4f} {to_currency}")

# --- Seção: Cotação de Ações/Criptomoedas ---
elif app_mode == "📈 Cotação de Ações/Criptomoedas":
    st.header("📈 Cotação de Ações e Criptomoedas")
    st.markdown("Obtenha cotações em tempo real e gráficos de histórico de preços.")

    symbol = st.text_input("Símbolo (Ex: AAPL, PETR4.SA, BTC-USD):", "AAPL", key="stock_symbol")

    @st.cache_data(ttl=600) # Cache por 10 minutos para cotações
    def get_stock_data(symbol_name):
        try:
            ticker = yf.Ticker(symbol_name)
            info = ticker.info
            if not info or 'regularMarketPrice' not in info:
                return None, None # Retorna None se não encontrar dados
            hist = ticker.history(period="7d")
            return info, hist
        except Exception as e:
            st.error(f"Erro ao buscar dados para '{symbol_name}': {e}")
            return None, None

    if st.button("Consultar Cotação", key="stock_button"):
        if symbol:
            with st.spinner(f"Buscando dados para {symbol}..."):
                info, hist = get_stock_data(symbol)
                
                if info:
                    st.subheader(f"Cotação de {info.get('longName', symbol)}")
                    
                    price = info.get('regularMarketPrice')
                    previous_close = info.get('previousClose')
                    
                    if price and previous_close:
                        change = price - previous_close
                        change_percent = (change / previous_close) * 100
                        
                        st.metric(
                            label="Preço Atual",
                            value=f"{price:.2f}",
                            delta=f"{change:.2f} ({change_percent:.2f}%)"
                        )
                    else:
                        st.write(f"Preço Atual: {price:.2f}")

                    st.write(f"**Volume:** {info.get('regularMarketVolume', 'N/A'):,}")
                    st.write(f"**Máxima do Dia:** {info.get('regularMarketDayHigh', 'N/A'):.2f}")
                    st.write(f"**Mínima do Dia:** {info.get('regularMarketDayLow', 'N/A'):.2f}")
                    
                    # Gráfico de histórico (últimos 7 dias)
                    if hist is not None and not hist.empty:
                        st.subheader("Histórico de Preços (Últimos 7 Dias)")
                        fig = px.line(hist, y="Close", title=f"Preço de Fechamento de {symbol}")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Histórico de preços não disponível para o símbolo selecionado.")

                else:
                    st.error(f"Símbolo '{symbol}' não encontrado ou dados indisponíveis.")
                    st.info("Verifique o símbolo (ex: AAPL, PETR4.SA para B3, BTC-USD para cripto).")
        else: st.warning("Por favor, digite um símbolo de ação ou criptomoeda.")

# --- Seção: Fatos/Citações/Piadas Aleatórias ---
elif app_mode == "💡 Fatos/Citações/Piadas Aleatórias":
    st.header("💡 Fatos, Citações e Piadas Aleatórias")
    st.markdown("Receba um pouco de inspiração ou humor!")

    content_type = st.radio(
        "O que você quer gerar?",
        ("Fato Aleatório", "Citação Aleatória", "Piada Aleatória"),
        key="random_content_type"
    )

    # ATENÇÃO: Usamos um argumento de "sal" aleatório para forçar a invalidação do cache.
    @st.cache_data(ttl=None) # ttl=None significa que ele não expira automaticamente
    def get_random_content(content_type_selected, cache_buster): # Adiciona cache_buster como um argumento
        if content_type_selected == "Fato Aleatório":
            API_URL = "http://numbersapi.com/random/trivia"
            try:
                response = requests.get(API_URL)
                response.raise_for_status()
                return response.text # Numbers API retorna texto puro (em inglês)
            except requests.exceptions.RequestException as e: 
                st.error(f"Erro ao buscar fato: {e}")
                st.info("Verifique sua conexão com a internet. O conteúdo de fatos é em inglês e não há uma alternativa simples e gratuita em português para esta API.")
                return None
        
        elif content_type_selected == "Citação Aleatória":
            API_URL = "https://api.quotable.io/random"
            try:
                response = requests.get(API_URL)
                response.raise_for_status()
                data = response.json()
                return f"“{data['content']}” — {data['author']}"
            except requests.exceptions.ConnectionError:
                st.error("Erro de conexão: Não foi possível conectar ao servidor de citações. Verifique sua conexão com a internet ou tente novamente mais tarde.")
                return None
            except requests.exceptions.Timeout:
                st.error("Tempo limite da requisição excedido ao buscar citação. Tente novamente.")
                return None
            except requests.exceptions.RequestException as e: 
                st.error(f"Erro ao buscar citação: {e}")
                st.info("Ocorreu um problema ao buscar a citação. Verifique sua conexão com a internet ou tente novamente mais tarde.")
                return None
        
        elif content_type_selected == "Piada Aleatória":
            # Nova API para piadas que suporta português
            API_URL = "https://v2.jokeapi.dev/joke/Any"
            params = {"lang": "pt", "blacklistFlags": "nsfw,religious,political,racist,sexist,explicit"}
            try:
                response = requests.get(API_URL, params=params)
                response.raise_for_status()
                data = response.json()
                if data["type"] == "single":
                    return data["joke"]
                elif data["type"] == "twopart":
                    return f"{data['setup']}\n\n{data['delivery']}"
                else:
                    return "Não foi possível obter uma piada."
            except requests.exceptions.RequestException as e: 
                st.error(f"Erro ao buscar piada: {e}")
                st.info("Verifique sua conexão com a internet ou tente novamente mais tarde.")
                return None
        return None

    if st.button("Gerar Conteúdo", key="generate_random_content"):
        # Gera um número aleatório para ser o 'cache_buster'.
        # Isso garante que a função 'get_random_content' seja sempre chamada com um argumento diferente,
        # forçando o Streamlit a re-executar a função e buscar um novo conteúdo.
        random_salt = random.random() 
        with st.spinner("Gerando..."):
            content = get_random_content(content_type, random_salt) # Passa o 'sal' aleatório
            if content:
                st.info(content)
                if content_type == "Fato Aleatório":
                    st.caption("Nota: Fatos aleatórios são fornecidos em inglês pela API (Numbers API) e não há uma alternativa simples e gratuita em português para esta funcionalidade.")

# --- Seção: Buscador de Filmes/Séries ---
elif app_mode == "🎬 Buscador de Filmes/Séries":
    st.header("🎬 Buscador de Filmes e Séries")
    st.markdown("Encontre informações detalhadas sobre seus filmes e séries favoritos.")

    search_query = st.text_input("Nome do Filme/Série:", "Inception", key="movie_search_query")

    @st.cache_data(ttl=86400) # Cache por 24 horas para dados de filmes
    def search_movie_omdb(query, api_key):
        if not api_key or api_key == "SUA_CHAVE_OMDB_AQUI":
            st.error("Chave de API OMDb inválida ou ausente.")
            return None
        BASE_URL = "http://www.omdbapi.com/"
        params = {
            "apikey": api_key,
            "t": query, # Busca por título exato
            "plot": "full", # Traz a sinopse completa
            "r": "json" # Retorna em JSON
        }
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("Response") == "True":
                return data
            else:
                st.error(f"Filme/Série '{query}' não encontrado(a).")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Ocorreu um erro na requisição: {e}")
            return None

    if st.button("Buscar", key="movie_search_button"):
        if OMDB_API_KEY == "SUA_CHAVE_OMDB_AQUI" or not OMDB_API_KEY:
            st.warning("Por favor, insira sua chave de API do OMDb no código.")
        elif search_query:
            with st.spinner(f"Buscando {search_query}..."):
                movie_data = search_movie_omdb(search_query, OMDB_API_KEY)
                if movie_data:
                    st.subheader(f"{movie_data.get('Title')} ({movie_data.get('Year')})")
                    
                    col_img, col_details = st.columns([1, 2])
                    
                    with col_img:
                        poster_url = movie_data.get('Poster')
                        if poster_url and poster_url != "N/A":
                            st.image(poster_url, caption=movie_data.get('Title'), use_container_width=True)
                        else:
                            st.info("Pôster não disponível.")
                    
                    with col_details:
                        st.write(f"**Gênero:** {movie_data.get('Genre')}")
                        st.write(f"**Diretor:** {movie_data.get('Director')}")
                        st.write(f"**Atores:** {movie_data.get('Actors')}")
                        st.write(f"**Avaliação IMDb:** {movie_data.get('imdbRating')}")
                        st.write(f"**Enredo:** {movie_data.get('Plot')}")
                        st.write(f"**Prêmios:** {movie_data.get('Awards')}")
        else: st.warning("Por favor, digite o nome de um filme ou série.")

st.markdown("---")
st.markdown("Este portfólio demonstra a integração com diversas APIs externas.")

st.sidebar.markdown("### Créditos")
st.sidebar.write("Este aplicativo foi desenvolvido por Danillo Wozniak Soares.")
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre o Aplicativo")
st.sidebar.write("Este portfólio contém várias ferramentas de consulta de dados em tempo real, "
                 "incluindo clima, conversão de moedas, cotações de ações/criptomoedas, "
                 "fatos/citações/piadas aleatórias e busca de filmes/séries.")
st.sidebar.markdown("### Como Usar")
st.sidebar.write("1. Insira o nome da cidade na caixa de entrada.\n"
                 "2. Clique em 'Consultar Clima' para obter as informações do clima.\n"
                 "3. Certifique-se de ter uma chave de API válida do OpenWeatherMap para que o aplicativo funcione corretamente.")
st.sidebar.markdown("### Requisitos")
st.sidebar.write("Para usar este aplicativo, você precisa de uma chave de API do OpenWeatherMap. "
                 "Você pode obter uma gratuitamente em [OpenWeatherMap](https://openweathermap.org/api).")
st.sidebar.markdown("### Observações")
st.sidebar.write("Este aplicativo é um exemplo de como integrar APIs externas em aplicativos Streamlit. "
                 "Certifique-se de respeitar os termos de uso da API e não exceder os limites de requisições.")
