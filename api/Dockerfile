# Stage 1: Build the Rust library
FROM rust:1.73-bullseye as build

# Install Python for maturin
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up build directory
WORKDIR /build

# Install maturin
RUN pip3 install maturin

# Copy Rust source code and build files
COPY src/ /build/src/
COPY Cargo.toml /build/Cargo.toml
COPY pyproject.toml /build/pyproject.toml

# Copy Python module (needed for maturin to find the Python source)
COPY api/ /build/api/

# Build the Rust library with Python bindings
# The module name is determined by the #[pymodule] macro in src/lib.rs
# and the package name in pyproject.toml
RUN maturin build --release

# Stage 2: Create the final Python image
FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Copy the built wheel from the build stage
COPY --from=build /build/target/wheels/*.whl /tmp/

# Copy Python API code
COPY api/ /app/

# Install dependencies and the built wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir /tmp/*.whl

# Expose API port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask app
CMD ["flask", "run"]