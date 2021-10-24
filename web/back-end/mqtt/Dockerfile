FROM node:14-alpine

WORKDIR /usr/src/app

COPY package*.json ./

# RUN npm ci --only=production
RUN npm i

COPY scripts scripts

CMD [ "npm", "start" ]