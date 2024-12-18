import yfinance as yf
import pandas as pd
from loguru import logger

logger.add("logs/data_utils.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip")

class DataUtils:
    def __init__(self, ticker, intervalo):
        self.ativo = yf.Ticker(ticker)
        self.intervalo = intervalo

    def fetch_cotacoes(self):

        try:

            if not self.ativo:
                logger.error(f'Ativo {self.ticker} nao encontrado.')
                return pd.DataFrame()

            dados_de_cotacoes = self.ativo.history(period='max', interval = self.intervalo)

            if dados_de_cotacoes.empty:
                logger.error('Nenhuma cotacao encontrada para o ativo.')
                return pd.DataFrame()

            logger.info('Dados de cotações obtidos com sucesso.')
            return dados_de_cotacoes

        except Exception as e:
            logger.error(f'Erro ao obter dados de cotações do ativo: {e}')
            return pd.DataFrame()
        
    def fetch_data(self):
        try:
            if not self.ativo:
                logger.error('Ativo nao encontrado.')
                return pd.DataFrame()

            info = {
                'nome':self.ativo.info.get('longName', 'N/A'),
                'setor': self.ativo.info.get('sector', 'N/A'),
                'segmento': self.ativo.info.get('industry', 'N/A'),
                'dividend yield': self.ativo.info.get('dividendYield', 'N/A'),
                'ultimo dividendo': self.ativo.info.get('lastDividendValue', 'N/A')
            }
            logger.info('Dados do ativo obtidos com sucesso.')
            return info

        except Exception as e:
            logger.error(f'Erro ao obter dados do ativo: {e}')
            return pd.DataFrame()
        
