FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY model ./model
COPY files ./files
COPY base_model ./base_model
COPY agent ./agent
COPY database ./database
COPY libs ./libs
COPY tool ./tool

COPY main.py .
COPY start.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
