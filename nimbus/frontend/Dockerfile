# Stage 1: Build
FROM node:20-alpine as build
WORKDIR /app
COPY package.json package-lock.json* tsconfig.json vite.config.ts ./
COPY src ./src
COPY index.html ./
RUN npm install && npm run build

# Stage 2: Serve
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist .
COPY public/favicon.ico ./favicon.ico
COPY public/favicon.svg ./favicon.svg
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
