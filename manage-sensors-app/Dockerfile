FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 8000