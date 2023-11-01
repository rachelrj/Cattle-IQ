FROM node:18-alpine
RUN CHROMEDRIVER_VERSION=109.0.5414.74 npm install -g chromedriver --chromedriver_version=109.0.5414.74
RUN npm install -g geckodriver
RUN mkdir -p /usr/app/node_modules && chown -R node:node /usr/app
COPY . /usr/app/
WORKDIR /usr/app
RUN npm install
COPY --chown=node:node . .

RUN mkdir /opt/google
RUN mkdir /opt/google/chrome
RUN ln -s /usr/bin/google-chrome /opt/google/chrome/google-chrome
EXPOSE 3000
ENTRYPOINT ["node", "index.js"]