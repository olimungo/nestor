FROM node:15-alpine

WORKDIR /usr/src/app

COPY package*.json ./ 

RUN npm i
# RUN npm ci --only=production

COPY scripts scripts

CMD [ "npm", "start" ]