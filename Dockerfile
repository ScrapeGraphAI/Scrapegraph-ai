FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && \
useradd -m -s /bin/bash app

USER app

RUN pip install scrapegraphai
