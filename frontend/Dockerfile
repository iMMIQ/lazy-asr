# Use Node 22 alpine image with bun
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Install bun
RUN npm install -g bun

# Copy package files
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy project files
COPY . .

# Expose port
EXPOSE 3000

# Run the application
CMD ["bun", "run", "dev"]