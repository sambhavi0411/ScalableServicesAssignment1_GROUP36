FROM python:3.9-slim

WORKDIR /app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "record.py"]