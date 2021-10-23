FROM node:14-alpine

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install
# RUN npm ci --only=production

COPY scripts scripts

CMD [ "npm", "start" ]