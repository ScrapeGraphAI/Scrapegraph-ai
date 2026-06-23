FROM node:24-alpine
WORKDIR /app
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
