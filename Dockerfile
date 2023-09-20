FROM python:3.10.2-slim-bullseye
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "daphne" , "config.asgi:application"]

EXPOSE 8000