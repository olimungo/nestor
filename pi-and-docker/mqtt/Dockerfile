FROM node:14

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install
# RUN npm ci --only=production

COPY scripts scripts

EXPOSE 8080
CMD [ "node", "scripts/server.js" ]