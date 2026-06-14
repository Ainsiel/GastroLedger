FROM node:22.13.1-alpine AS dependencies

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /workspace

COPY package.json package-lock.json* .npmrc ./
COPY apps/web/package.json apps/web/package.json
COPY packages/api-contract/package.json packages/api-contract/package.json
RUN npm ci

FROM dependencies AS development

COPY . .
CMD ["npm", "--workspace", "@gastroledger/web", "run", "dev"]

FROM dependencies AS build

COPY . .
RUN npm --workspace @gastroledger/api-contract run build \
    && npm --workspace @gastroledger/web run build

FROM node:22.13.1-alpine AS runtime

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production
WORKDIR /workspace

COPY --from=build /workspace /workspace
CMD ["npm", "--workspace", "@gastroledger/web", "run", "start"]
