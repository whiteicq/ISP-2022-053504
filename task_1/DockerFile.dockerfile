FROM python:3.8-slim-buster

WORKDIR /task1

COPY . .


CMD ["python", "./app.py"]