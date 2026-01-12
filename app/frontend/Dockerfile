# ---------- build stage ----------
FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- runtime stage ----------
FROM nginx:alpine

# Elimina config default
RUN rm /etc/nginx/conf.d/default.conf

# Copia config custom (opcional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia SOLO el build final
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
