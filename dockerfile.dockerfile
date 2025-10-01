dockerfile
FROM python:3.10-slim
COPY app.py requirements.txt ./
RUN pip install -r requirements.txt
CMD uvicorn app:app --host 0.0.0.0 --port 7860