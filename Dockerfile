FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 # nao gera arquivos .pyc
ENV PYTHONUNBUFFERED=1 # nao buffera a saida

# dependências necessárias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
