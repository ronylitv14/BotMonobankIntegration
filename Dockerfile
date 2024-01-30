FROM python:3-alpine3.11

WORKDIR /src/app

COPY ./requirements.txt /src/app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/app/requirements.txt

COPY . /src/app

RUN alembic upgrade heads

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
