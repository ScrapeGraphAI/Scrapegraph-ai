FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y

RUN pip install scrapegraphai
RUN pip install scrapegraphai[burr]

RUN python3 -m playwright install-deps
RUN python3 -m playwright install