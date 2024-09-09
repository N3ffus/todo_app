FROM python:3.12

RUN mkdir /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN alembic upgrade head

CMD gunicorn -w 1 -k uvicorn.workers.UvicornWorker src.main:app