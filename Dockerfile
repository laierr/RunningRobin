FROM python:3.8-slim

WORKDIR /app

COPY src/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src/ .

CMD ["python", "app.py"]
