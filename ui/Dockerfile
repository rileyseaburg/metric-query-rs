# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies first (better layer caching)
COPY package*.json ./
COPY tsconfig.json ./
COPY next.config.ts ./
COPY postcss.config.mjs ./
RUN npm ci

# Copy only the necessary application code
COPY . .

# Build the Next.js application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app
# Set environment variables
ENV NODE_ENV=production
ENV DOCKER_ENV=true
ENV NODE_ENV=production

# Copy built assets from the builder stage
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Expose port
EXPOSE 3000

# Set the command to start the Next.js server
CMD ["npm", "start"]