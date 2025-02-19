FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies including TypeScript support
# Install dependencies including TypeScript support and Geist
RUN npm install -g typescript @types/node
RUN npm install geist
RUN npm ci

# Copy frontend source
COPY . .

# Set environment variables
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NODE_ENV=production

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]