#!/bin/bash
set -e

cd /home/ec2-user/product-review-service/backend

echo "=== Git pull ==="
git pull origin main

echo "=== Docker compose up ==="
docker compose -f docker-compose.prod.yml up -d --build

echo "=== Remove unused images ==="
docker image prune -f

echo "Deploy Complete"
