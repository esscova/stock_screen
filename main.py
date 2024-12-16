# STOCKS DASHBOARD

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import ta
from loguru import logger

# configuração de logs
logger.add("logs/debug.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip")

##########################################################################################
## PARTE 1: FUNÇÕES PARA OBTER E TRATAR DADOS ##
##########################################################################################
def obter_dados(ticker, intervalo, periodo = 'max'):
    erro = {"Erro": f"Ticker {ticker} não encontrado."}
    
    try: 
        # Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
        # Valid periods: ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

        ativo = yf.Ticker(ticker)
        if not ativo:
            logger.error(f'Ativo {ticker} nao encontrado.')
            return pd.DataFrame(), erro

        cotacoes = ativo.history(period=periodo, interval = intervalo)
        if cotacoes.empty:
            logger.error(f'Nenhuma cotacao encontrada para o ativo {ticker} no intervalo {intervalo}.')
            return pd.DataFrame(), erro

        logger.info('Dados de cotações obtidos com sucesso.')

        info = {
            'nome':ativo.info.get('longName', 'N/A'),
            'setor': ativo.info.get('sector', 'N/A'),
            'segmento': ativo.info.get('industry', 'N/A'),
            'dividend yield': ativo.info.get('dividendYield', 'N/A'),
            'ultimo dividendo': ativo.info.get('lastDividendValue', 'N/A')
        }
        logger.info('Dados do ativo obtidos com sucesso.')
        return cotacoes, info
    
    except Exception as e:
        logger.error(f"Erro inesperado ao obter dados: {e}.")
        return pd.DataFrame(), erro

def add_indicadores(df):
    """
    Adiciona médias móveis simples (SMA) e exponenciais (EMA) ao DataFrame.
    """
    try:
        if 'Close' not in df.columns:
            logger.error("Coluna 'Close' nao encontrada no DataFrame.")
            return df

        df['SMA 20'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['EMA 20'] = df['Close'].ewm(span=20, adjust=False).mean()
        

        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

        logger.info("Indicadores técnicos adicionados com sucesso.")

        return df

    except Exception as e:
        logger.error(f"Erro ao adicionar indicadores técnicos: {e}")
        return df


##########################################################################################
## PARTE 2: DASHBOARD ##
##########################################################################################

# configuração do streamlit
st.set_page_config(layout="wide", 
    page_title="Stocks Dashboard",
    page_icon=":chart_with_upwards_trend:")

# cabeçalho
st.title("Stocks Dashboard")

# menu lateral
with st.sidebar:
    st.header("Filtros")
    ticker = st.text_input("Ticker", "AAPL").strip().upper()
    intervalo = st.selectbox('Período', ['1m', '2m', '5m', '15m', '30m', '60m','90m', '1d', '5d', '1wk', '1mo', '3mo'])
    grafico = st.selectbox('Tipo de Gráfico', ['Line', 'Candlestick'])
    indicadores = st.multiselect('Médias móveis', ['SMA 20', 'EMA 20'])
    update = st.button('UPDATE')

    st.subheader("Sobre")
    st.info("Desenvolvido por [escova](https://github.com/esscova) com Streamlit.")

# paineis
if update and ticker:
    
    periodo = 'max' if intervalo in ['1d', '5d', '1wk', '1mo', '3mo'] else '1d'
    with st.spinner('Carregando dados...'):
        cotacoes, info = obter_dados(ticker=ticker, intervalo=intervalo, periodo=periodo) 

    if cotacoes.empty:
        st.error('Nenhuma cotação encontrada.')

    cotacoes = add_indicadores(cotacoes)
    
    fig = go.Figure()

    for indicador in indicadores:
        fig.add_trace(go.Scatter(x=cotacoes.index, y=cotacoes[indicador], name=indicador))
       
    if cotacoes.empty:
        st.error('Nenhuma cotação encontrada.')

    if grafico == 'Line':
        fig.add_trace(
            go.Scatter(x=cotacoes.index, y=cotacoes['Close'], name='Close')
        )

    elif grafico == 'Candlestick':
        fig.add_trace(
            go.Candlestick(
                x=cotacoes.index, 
                open=cotacoes['Open'], 
                high=cotacoes['High'], 
                low=cotacoes['Low'], 
                close=cotacoes['Close'], 
                name='Candlestick'
            )
        )

    fig.update_layout(
        title=f'{ticker[:-3] if ticker[-3:] == ".SA" else ticker } {intervalo.upper()}',
        xaxis_title='Data',
        yaxis_title='Preço',
        showlegend=True,
        template='plotly_dark'
    )  

    st.plotly_chart(fig,use_container_width=True)
    st.bar_chart(cotacoes['Volume'], height=200)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader('Cotações', divider='red')
        st.dataframe(cotacoes)

    with col2:
        if 'Erro' not in info:
            st.subheader(ticker, divider='red')
            for k, v in info.items():
                st.info(f'{k}: {v}')
        else:
            st.error(info['Erro'])