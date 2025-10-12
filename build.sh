#!/bin/bash

echo "Building ASR application with integrated frontend..."

# Build frontend
echo "Building frontend..."
cd frontend && npm run build

# Create backend static directory and copy frontend build
echo "Copying frontend build to backend static directory..."
rm -rf ../backend/static
mkdir -p ../backend/static
cp -r build/* ../backend/static/

echo "Build completed successfully!"
echo "Frontend build copied to backend/static/"
echo "You can now run the backend and access the frontend at http://localhost:8000"
