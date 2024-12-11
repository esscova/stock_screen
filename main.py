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
## PARTE 1: FUNÇÕES PARA OBTER DADOS ##
##########################################################################################

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
    periodo = st.selectbox('Período', ['1m','5m', '15m', '30m', '1h', '1d', '5d', '1wk', '1mo', '3mo', 'Max'])
    grafico = st.selectbox('Tipo de Gráfico', ['Line', 'Candlestick'])
    indicadores = st.multiselect('Médias móveis', ['SMA 20', 'EMA 20'])

    if st.button('UPDATE'):
        st.write('Atualizando...')
    
    st.subheader("Sobre")
    st.info("Desenvolvido por [escova](https://github.com/esscova) com Streamlit.")