# Metric Query Interface

A powerful time-series metric processing system with a high-performance Rust core, Python API layer, and React frontend.

## Architecture

This project demonstrates a streaming data system for processing and transforming time-series metrics, with the following components:

- **Rust Core Library**: High-performance processing engine
- **Python Bindings**: PyO3-based interface for Python access
- **Flask API**: RESTful service layer exposing the transformation capabilities
- **React UI**: Interactive web interface for visualizing and interacting with the metrics

## Getting Started (For Beginners)

If you're new to this project or to development in general, follow these steps to get started:

### Prerequisites

Before you begin, you'll need to install:

1. **Rust**
   - Visit [https://rustup.rs/](https://rustup.rs/) and follow the installation instructions
   - After installation, run `rustc --version` to verify it works

2. **Python (3.8 or newer)**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
   - Verify with `python --version`

3. **Node.js & npm**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify with `node --version` and `npm --version`

4. **Docker (Optional for local development)**
   - Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - After installation, run `docker --version` to verify

### Running Without Docker (Development)

If you don't have Docker installed, you can run the components separately:

1. **Build the Rust library**:
   ```bash
   # From the root directory
   cargo build
   ```

2. **Set up the Python API**:
   ```bash
   # Navigate to the API directory
   cd api
   
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   # source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the API server
   python app.py
   # The API will be available at http://localhost:5000
   ```

3. **Run the UI**:
   ```bash
   # Navigate to the UI directory
   cd ui
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   # The UI will be available at http://localhost:3000
   ```

## Features

- **Filter Operations**: GT, LT, GTE, LTE, Eq
- **Aggregations**: SUM, AVG, MIN, MAX
- **Time Groupings**: HOUR, MINUTE, DAY
- **Pipeline API**: Fluent interface for chaining transformations
- **Plugin Architecture**: Extensible design for custom transformations

## Deployment Options

### Local Development with Docker Compose

If you have Docker installed, this is the easiest way to run the application:

```bash
# Build and start both API and UI containers
docker-compose up --build

# Access the UI at http://localhost:3000
# The API is available at http://localhost:5000
```

### Troubleshooting Common Issues

- **"Command not found" errors**: Make sure the required tools are installed and in your PATH
- **Port conflicts**: If ports 3000 or 5000 are in use, you can change them:
  - For the API: Edit `api/app.py` and change the port number in `app.run()`
  - For the UI: Edit `ui/package.json` and add `-p [new-port]` to the dev script

### Production Deployment on Kubernetes

For production deployment, we provide both direct Kubernetes manifests and a Helm chart:

#### Option 1: Direct Kubernetes Manifests

Kubernetes manifests are provided in the `k8s` directory:

1. **Build and push Docker images**

```bash
# Build and tag images
docker build -t your-registry/metrics-api:latest -f api/Dockerfile .
docker build -t your-registry/metrics-ui:latest -f ui/Dockerfile ./ui

# Push to your container registry
docker push your-registry/metrics-api:latest
docker push your-registry/metrics-ui:latest
```

2. **Update image references in Kubernetes manifests**

Edit `k8s/api-deployment.yaml` and `k8s/ui-deployment.yaml` to use your image names.

3. **Apply Kubernetes manifests**

```bash
# Create deployments and services
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/ui-deployment.yaml

# Set up ingress for accessing the application
kubectl apply -f k8s/ingress.yaml
```

#### Option 2: Helm Chart Deployment (Recommended)

For a more configurable and maintainable deployment, use the provided Helm chart:

1. **Build and push Docker images** (same as above)

2. **Configure the deployment**

Edit `metrics-chart/values.yaml` to customize:
- Image repository paths
- Replica counts
- Resource allocations
- Ingress hostnames

3. **Install the Helm chart**

```bash
# Install the chart with your custom values
helm install metrics-release ./metrics-chart/ -f ./metrics-chart/values.yaml

# For different environments, use the appropriate values file:
# helm install metrics-release ./metrics-chart/ -f ./metrics-chart/values-prod.yaml
# helm install metrics-release ./metrics-chart/ -f ./metrics-chart/values-dev.yaml
```

4. **Verify the deployment**

```bash
# Check that all pods are running
kubectl get pods -n metrics-chart

# Verify services and ingress
kubectl get svc,ing -n metrics-chart
```

### Helm Chart Features

The metrics-chart Helm chart provides:

- Automatic namespace creation (`metrics-chart`)
- Configurable API and UI deployments
- TLS certificate management with cert-manager
- Ingress configuration with custom hostnames
- Health checks and readiness probes
- Resource limits for production stability

### DNS Configuration

Ensure DNS records are configured for:
- `metrics-demandbase.rileyseaburg.com` (UI application)
- `api-metrics-demandbase.rileyseaburg.com` (API backend)

## Accessing the Deployed Application

Once deployed, the application will be available at:

- **Frontend UI**: [https://metrics-demandbase.rileyseaburg.com](https://metrics-demandbase.rileyseaburg.com)
- **API Endpoint**: [https://api-metrics-demandbase.rileyseaburg.com](https://api-metrics-demandbase.rileyseaburg.com)

## Development

### Project Structure

```
.
├── api/                    # Flask API
│   ├── app.py              # Main Flask application
│   ├── Dockerfile          # API container definition
│   ├── metric_query_library/  # Python bindings
│   └── test_data.json      # Sample data
├── src/                    # Rust core library
│   ├── models/             # Data models
│   ├── errors.rs           # Error handling
│   ├── lib.rs              # Library entry point
│   ├── plugin_impls.rs     # Plugin implementations
│   ├── plugins.rs          # Plugin system
│   └── transformations.rs  # Core transformation logic
├── ui/                     # React frontend
│   ├── src/                # UI source code
│   │   ├── app/            # Next.js app router
│   │   ├── components/     # React components
│   │   └── lib/            # Utilities and API client
│   └── Dockerfile          # UI container definition
├── k8s/                    # Kubernetes manifests
│   ├── api-deployment.yaml # API deployment configuration
│   ├── ui-deployment.yaml  # UI deployment configuration
│   └── ingress.yaml        # Ingress configuration
└── metrics-chart/          # Helm chart for Kubernetes deployment
    ├── Chart.yaml          # Chart metadata
    ├── values.yaml         # Default configuration values
    ├── values-dev.yaml     # Development environment values
    ├── values-prod.yaml    # Production environment values
    └── templates/          # Kubernetes template manifests
        ├── api-deployment.yaml
        ├── ui-deployment.yaml
        ├── ingress.yaml
        └── namespace.yaml
```

### Performance Considerations

The application is designed for high performance:

- Rust core for efficient metric processing
- Optimized algorithms for time-series transformations
- Containerized deployment for scalability
- Independent scaling of UI and API components

## Learn More

For more details about the API endpoints, see the Swagger documentation available at:
- Local: http://localhost:5000/apidocs/
- Production API: https://api-metrics-demandbase.rileyseaburg.com
- Production UI: https://metrics-demandbase.rileyseaburg.com
- Production API Swagger: https://api-metrics-demandbase.rileyseaburg.com/apidocs/
