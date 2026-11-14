"""
Smart Farm Agricultural Decision Support Backend
File: backend/app.py

Flask API Server exposing scientific fertilizer recommendation algorithms,
crop advisory services, and manual calculation endpoints.
"""

import os
from flask import Flask, jsonify, request

# Try importing flask_cors, provide robust fallback if not present
try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    has_cors = False

from manual_routes import manual_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smart-farm-fertilizer-secret-2026')
    app.config['JSON_SORT_KEYS'] = False

    # Configure CORS for React / Vite / Mobile Web clients
    if has_cors:
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    else:
        @app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            return response

    # Register Fertilizer Calculation Blueprint
    app.register_blueprint(manual_bp)

    @app.route('/')
    def root():
        return jsonify({
            'application': 'Smart Farm Fertilizer & Nutrient Recommendation API',
            'version': '2.0.0',
            'status': 'online',
            'endpoints': {
                'health': '/api/fertilizer/health',
                'supported_crops': '/api/fertilizer/crops',
                'fertilizer_catalog': '/api/fertilizer/fertilizers',
                'calculate': '/api/fertilizer/calculate'
            }
        }), 200

    @app.route('/api/health')
    def api_health():
        return jsonify({'status': 'ok', 'uptime': 'active'}), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'status': 'error', 'message': 'Requested API endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'status': 'error', 'message': 'Internal server error processing calculation'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌾 Smart Farm Fertilizer Backend running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
