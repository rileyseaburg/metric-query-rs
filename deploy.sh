#!/bin/bash
# deploy.sh - Build containers and deploy the Metrics application to Kubernetes
# Usage: ./deploy.sh [registry] [tag]
#   registry: Docker registry to push images to (default: registry.quantum-forge.net)
#   tag: Tag for Docker images (default: latest)

set -e  # Exit immediately if a command exits with a non-zero status

# Default values
REGISTRY=${1:-"registry.quantum-forge.net"}
TAG=${2:-"latest"}
CHART_DIR="./metrics-chart"
VALUES_FILE="$CHART_DIR/values.yaml"
RELEASE_NAME="metrics-release"

# Print script configuration
echo "=== Deployment Configuration ==="
echo "Registry: $REGISTRY"
echo "Tag: $TAG"
echo "Chart directory: $CHART_DIR"
echo "Values file: $VALUES_FILE"
echo "Release name: $RELEASE_NAME"
echo "==============================="

# Build and push API image
build_api() {
  echo "=== Building API image ==="
  cd api
  docker build -t $REGISTRY/metrics-api:$TAG .
  docker push $REGISTRY/metrics-api:$TAG
  cd ..
  echo "API image built and pushed successfully"
}

# Build and push UI image
build_ui() {
  echo "=== Building UI image ==="
  cd ui
