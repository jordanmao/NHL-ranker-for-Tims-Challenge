FROM python:3.9

COPY autopicker/ autopicker/
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "./autopicker/main.py"]
