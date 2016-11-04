FROM python:2.7

ENV PYTHONUNBUFFERED 1
RUN apt-get update
#RUN apt-get update -qq && apt-get install -y build-essential
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt