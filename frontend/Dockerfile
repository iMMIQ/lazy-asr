# Use Node 22 alpine image
FROM node:22-alpine

# Set working directory
WORKDIR /app

RUN npm config set registry https://registry.npmmirror.com/

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "start"]