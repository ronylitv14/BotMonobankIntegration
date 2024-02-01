FROM python:3.11-alpine3.17


WORKDIR /src/app

COPY ./requirements.txt /src/app/requirements.txt

RUN apk add --no-cache postgresql-dev rust cargo \
    && pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r /src/app/requirements.txt

COPY . /src/app

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8088"]
