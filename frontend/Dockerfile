FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY public/ ./public/
COPY src/ ./src/
COPY tsconfig.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Build the app
RUN npm run build

# Install serve to run the built app
RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]