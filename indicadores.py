from loguru import logger

logger.add("logs/indicadores.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip")

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

        logger.info("Indicadores técnicos adicionados com sucesso.")

        return df

    except Exception as e:
        logger.error(f"Erro ao adicionar indicadores técnicos: {e}")
        return df