# STOCKS DASHBOARD

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from loguru import logger

from data_utils import DataUtils
from indicadores import add_indicadores

# configuração de logs
logger.add("logs/main.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip")

# configuração do streamlit
st.set_page_config(
    layout="wide", 
    page_title="Stocks Dashboard",
    page_icon=":chart_with_upwards_trend:"
)

# cabeçalho
st.title(":chart_with_upwards_trend: Stocks :red[Dashboard]")
st.write("---")

# menu lateral
with st.sidebar:
    st.header("Filtros")
    ticker = st.text_input("Ticker", "AAPL").strip().upper()
    intervalo = st.selectbox('Período', ['1m', '2m', '5m', '15m', '30m', '60m','90m', '1d', '5d', '1wk', '1mo', '3mo'])
    grafico = st.selectbox('Tipo de Gráfico', ['Line', 'Candlestick'])
    indicadores = st.multiselect('Médias móveis', ['SMA 20', 'EMA 20'])
    update = st.button('UPDATE')

    st.subheader("Sobre")
    st.info("Isto não é uma recomendação de investimentos e sim uma ferramenta de visualização de dados.")

    # links para github e linkedin
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: end;">
            <a href="https://github.com/esscova" target="_blank" style="margin-right: 10px;">
                <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" style='height: 30px;' alt="GitHub">
            </a>
            <a href="https://www.linkedin.com/in/wellington-moreira-santos/" target="_blank">
                <img src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?&style=for-the-badge&logo=linkedin&logoColor=white" style='height: 30px;' alt="LinkedIn">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )


# paineis
if update and ticker:
    
    with st.spinner('Carregando dados...'):
        dados = DataUtils(ticker, intervalo)
        cotacoes = dados.fetch_cotacoes()
        info = dados.fetch_data()
   
    cotacoes = cotacoes.dropna()
    cotacoes = add_indicadores(cotacoes)

    col1, col2 = st.columns([4, 1])
    
    with col1:
        fig = go.Figure()
        st.subheader(f'Cotação: {round(cotacoes['Close'].iloc[-1],2)}')
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
                    name='Candlestick',
                )
            )
    
    
        fig.update_layout(
            title=f'{ticker[:-3] if ticker[-3:] == ".SA" else ticker } {intervalo}',
            xaxis_rangeslider_visible=False,
            xaxis_title='Data',
            yaxis_title='Preço',
            showlegend=True,
            template='plotly_dark'
        )  

        st.plotly_chart(fig,use_container_width=True)
        st.bar_chart(cotacoes['Volume'], height=200)

    with col2:
        if 'Erro' not in info:
            for k, v in info.items():
                st.info(f'{k}: {v}')
        else:
            st.error(info['Erro'])     
