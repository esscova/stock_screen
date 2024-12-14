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
    
    try: # Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
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
    if 'SMA 20' in df.columns and 'EMA 20' in df.columns:
        return df

    df['SMA 20'] = ta.trend.sma_indicator(close=df['Close'], window=20)
    df['EMA 20'] = ta.trend.ema_indicator(close=df['Close'], window=20)

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
    ticker = st.text_input("Ticker", "AAPL")
    intervalo = st.selectbox('Período', ['1m', '2m', '5m', '15m', '30m', '60m','90m', '1d', '5d', '1wk', '1mo', '3mo'])
    grafico = st.selectbox('Tipo de Gráfico', ['Line', 'Candlestick'])
    indicadores = st.multiselect('Médias móveis', ['SMA 20', 'EMA 20'])
    update = st.button('UPDATE')

    st.subheader("Sobre")
    st.info("Desenvolvido por [escova](https://github.com/esscova) com Streamlit.")

# paineis
if update:
    
    periodo = 'max' if intervalo in ['1d', '5d', '1wk', '1mo', '3mo'] else '1d'
    cotacoes, info = obter_dados(ticker=ticker, intervalo=intervalo, periodo=periodo) 

    if not cotacoes.empty:
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

    fig.update_layout(title=f'{ticker[:-3] if ticker[-3:] == ".SA" else ticker } {intervalo.upper()}')
    st.plotly_chart(fig)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader('Cotações', divider='red')
        st.dataframe(cotacoes)

    with col2:
        if 'Erro' not in info:
            st.subheader(ticker, divider='red')
            st.text(f"Nome: {info['nome']}")
            st.text(f"Setor: {info['setor']}")
            st.text(f"Segmento: {info['segmento']}")
            st.text(f"Dividend Yield: {(info['dividend yield']*100):.2f}%")
            st.text(f"Último Dividendo: {round(info['ultimo dividendo'],2)}")
        else:
            st.error(info['Erro'])