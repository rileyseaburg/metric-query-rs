"""
Metric Query API - Main Application
"""
from flask import Flask
from flasgger import Swagger
from flask_cors import CORS

# Import configuration
from config import get_swagger_template

# Import route blueprints
from routes import (
    docs_bp, metrics_bp, labeled_metrics_bp, extensions_bp, tests_bp
)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    # Configure CORS with more explicit settings
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "supports_credentials": True,
        "max_age": 86400  # 24 hours
    }})
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configure Swagger with detailed OpenAPI specification
    Swagger(app, template=get_swagger_template())
    
    # Register blueprints with URL prefixes
    app.register_blueprint(docs_bp, url_prefix='')
    app.register_blueprint(metrics_bp, url_prefix='/metrics')
    app.register_blueprint(labeled_metrics_bp, url_prefix='/labeled-metrics')
    app.register_blueprint(extensions_bp, url_prefix='')
    app.register_blueprint(tests_bp, url_prefix='/test')
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
