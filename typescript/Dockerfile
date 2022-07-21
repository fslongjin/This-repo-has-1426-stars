FROM node:16-alpine AS builder

COPY ./package.json .
COPY ./yarn.lock ./yarn.lock

RUN yarn install --production

# app
FROM node:16-alpine

WORKDIR /app
COPY --from=builder /node_modules/ /node_modules/
COPY ./package.json .
COPY ./src ./src

CMD ["yarn", "start"]
