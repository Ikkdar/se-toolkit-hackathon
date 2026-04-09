ARG REGISTRY_PREFIX_DOCKER_HUB=
FROM ${REGISTRY_PREFIX_DOCKER_HUB}node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
ARG NPM_REGISTRY=https://registry.npmjs.org/
RUN npm config set registry ${NPM_REGISTRY} \
	&& npm ci --no-audit --no-fund

COPY . .

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

ARG REGISTRY_PREFIX_DOCKER_HUB=
FROM ${REGISTRY_PREFIX_DOCKER_HUB}nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
