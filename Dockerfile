FROM python:3.9-slim

ENV GECKODRIVER_VERSION=0.30.0

WORKDIR /usr/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -yqq unzip curl firefox-esr wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget -O- https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz | tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver

EXPOSE 3000

CMD ["python", "index.py"]





