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
def obter_dados(ticker, intervalo):
    try: # Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
        ativo = yf.Ticker(ticker)
        if not ativo:
            logger.error('Falha em obter dados')
            raise 

        cotacoes = ativo.history(period='max', interval = intervalo)
        logger.info('Dados de cotações obtidos com sucesso.')

        info = {
            'nome':ativo.info['longName'],
            'setor': ativo.info['sector'],
            'segmento': ativo.info['industry'],
            'dividend yield': ativo.info['dividendYield'],
            'ultimo dividendo': ativo.info['lastDividendValue']
        }
        logger.info('Dados do ativo obtidos com sucesso.')
        return cotacoes, info
    
    except:
        raise


##########################################################################################
## PARTE 2: PAINEL DO STREAMLIT ##
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
    ticker = st.text_input("Ticker", "AAPL")
    intervalo = st.selectbox('Período', ['1m', '2m', '5m', '15m', '30m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'])
    grafico = st.selectbox('Tipo de Gráfico', ['Line', 'Candlestick'])
    indicadores = st.multiselect('Médias móveis', ['SMA 20', 'EMA 20'])
    update = st.button('UPDATE')

    st.subheader("Sobre")
    st.info("Desenvolvido por [escova](https://github.com/esscova) com Streamlit.")


if update:
    cotacoes, info = obter_dados(ticker=ticker, intervalo=intervalo) 

    col1, col2 = st.columns(2)

    with col1:
        st.write('Cotações')
        st.dataframe(cotacoes)
    
    with col2:
        st.write('Informações')
        st.text(info['nome'])


    