FROM python:3.11

ENV GECKODRIVER_VERSION=0.30.0

RUN apt-get update

RUN apt-get install -y ca-certificates curl firefox-esr wget

RUN update-ca-certificates

RUN wget --no-check-certificate -O- https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz | tar -xz -C /usr/local/bin
RUN chmod +x /usr/local/bin/geckodriver

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . /usr/app

WORKDIR /usr/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD ["python", "index.py"]