FROM node:20-alpine
WORKDIR /app
COPY server.js index.html hero.png favicon.png ./
EXPOSE 80
CMD ["node", "server.js"]
