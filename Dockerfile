FROM python:3.12

RUN mkdir /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn main:app --workers 1 --worker-class Uvicorn.workers.UvicornWorker