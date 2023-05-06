FROM python:3.9

WORKDIR /app
COPY autopicker/ autopicker/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./autopicker/main.py"]
