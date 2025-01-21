FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir scrapegraphai
RUN pip install --no-cache-dir scrapegraphai[burr]

RUN python3 -m playwright install-deps
RUN python3 -m playwright install
