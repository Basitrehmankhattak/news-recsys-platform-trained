FROM python:3.10-slim

WORKDIR /app

COPY app ./app
COPY scripts ./scripts

RUN pip install --upgrade pip
RUN pip install fastapi uvicorn psycopg2-binary pandas numpy scikit-learn lightgbm faiss-cpu sentence-transformers sqlalchemy

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
