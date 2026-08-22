import os
from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'globetrotter-production-secret-2026')

# Enable CORS for production deployments
cors_origin = os.getenv('CORS_ORIGINS', '*')
CORS(app, resources={r"/api/*": {"origins": cors_origin}})

# ── Health check ──────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({'success': True, 'message': 'GlobeTrotter API is running 🌍'})

# ── Serve index for root URL ──────────────────────────────────
@app.route('/')
def index():
    return app.send_static_file('index.html')

# ── Register blueprints ───────────────────────────────────────
from routes.activities import activities_bp
from routes.trips import trips_bp
from routes.budget import budget_bp

app.register_blueprint(activities_bp, url_prefix='/api')
app.register_blueprint(trips_bp,      url_prefix='/api')
app.register_blueprint(budget_bp,     url_prefix='/api')

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    print(f'[OK] GlobeTrotter starting on http://{host}:{port}')
    app.run(host=host, port=port, debug=False)
