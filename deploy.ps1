# deploy.ps1 - Build containers and deploy the Metrics application to Kubernetes
# Usage: .\deploy.ps1 [registry] [tag] [skipPush]
#   registry: Docker registry to push images to (default: registry.quantum-forge.net)
#   tag: Tag for Docker images (default: latest)
#   skipPush: Skip pushing images to registry (default: false)

# Stop on first error
$ErrorActionPreference = "Stop"

# Default values
$registry = if ($args[0]) { $args[0] } else { "registry.quantum-forge.net" }
$tag = if ($args[1]) { $args[1] } else { "latest" }
$skipPush = if ($args[2] -eq "true") { $true } else { $false }
$chartDir = ".\metrics-chart"
$valuesFile = "$chartDir\values.yaml"
$releaseName = "metrics-release"

# Print script configuration
Write-Host "=== Deployment Configuration ===" -ForegroundColor Cyan
Write-Host "Registry: $registry"
Write-Host "Tag: $tag"
Write-Host "Skip Push: $skipPush"
Write-Host "Chart directory: $chartDir"
Write-Host "Values file: $valuesFile"
Write-Host "Release name: $releaseName"
Write-Host "===============================" -ForegroundColor Cyan

# Function to build and push API image
function Build-ApiImage {
    Write-Host "=== Building API image ===" -ForegroundColor Green
    try {
        # Build from the root directory to ensure all files are in context
        docker build -t "$registry/metrics-api:$tag" -f "./api/Dockerfile" .
        if ($LASTEXITCODE -ne 0) { throw "Docker build failed for API" }
        
        # Push image if skipPush is false
        if (-not $skipPush) {
            Write-Host "Pushing API image to registry..." -ForegroundColor Yellow
            docker push "$registry/metrics-api:$tag"
            if ($LASTEXITCODE -ne 0) { throw "Docker push failed for API" }
            Write-Host "API image pushed successfully" -ForegroundColor Green
        } else {
            Write-Host "Skipping push for API image (skipPush=true)" -ForegroundColor Yellow
        }
        
        Write-Host "API image built successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Error building API image: $_" -ForegroundColor Red
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Function to build and push UI image
function Build-UiImage {
    Write-Host "=== Building UI image ===" -ForegroundColor Green
    try {
        # Build from the root directory to ensure all files are in context
        docker build -t "$registry/metrics-ui:$tag" -f "./ui/Dockerfile" .
        if ($LASTEXITCODE -ne 0) { throw "Docker build failed for UI" }
        
        # Push image if skipPush is false
        if (-not $skipPush) {
            Write-Host "Pushing UI image to registry..." -ForegroundColor Yellow
            docker push "$registry/metrics-ui:$tag"
            if ($LASTEXITCODE -ne 0) { throw "Docker push failed for UI" }
            Write-Host "UI image pushed successfully" -ForegroundColor Green
        } else {
            Write-Host "Skipping push for UI image (skipPush=true)" -ForegroundColor Yellow
        }
        
        Write-Host "UI image built successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Error building UI image: $_" -ForegroundColor Red
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Function to deploy Helm chart
function Deploy-HelmChart {
    Write-Host "=== Deploying Helm Chart ===" -ForegroundColor Green
    try {
        # Check if the release already exists
        $releaseExists = helm list -q | Select-String -Pattern "^$releaseName$"
        
        if ($releaseExists) {
            # Upgrade existing release
            Write-Host "Upgrading existing Helm release '$releaseName'..." -ForegroundColor Yellow
            helm upgrade $releaseName $chartDir -f $valuesFile
            if ($LASTEXITCODE -ne 0) { throw "Helm upgrade failed" }
            Write-Host "Helm chart upgraded successfully" -ForegroundColor Green
        } else {
            # Install new release
            Write-Host "Installing new Helm release '$releaseName'..." -ForegroundColor Yellow
            helm install $releaseName $chartDir -f $valuesFile
            if ($LASTEXITCODE -ne 0) { throw "Helm install failed" }
            Write-Host "Helm chart installed successfully" -ForegroundColor Green
        }
        
        # Display release information
        Write-Host "Helm release information:" -ForegroundColor Cyan
        helm status $releaseName
    }
    catch {
        Write-Host "Error deploying Helm chart: $_" -ForegroundColor Red
        exit 1
    }
}

# Main execution
try {
    Write-Host "Starting deployment process..." -ForegroundColor Yellow
    
    # Build and push Docker images
    Build-ApiImage
    Build-UiImage
    
    # Deploy Helm chart
    Deploy-HelmChart
    
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Deployment failed: $_" -ForegroundColor Red
    exit 1
}