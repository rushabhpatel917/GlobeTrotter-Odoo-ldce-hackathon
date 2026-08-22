from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'globetrotter-hackathon-2026'
CORS(app)

# ── Health check ──────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({'success': True, 'message': 'GlobeTrotter API is running 🌍'})

# ── Serve index for root URL ──────────────────────────────────
@app.route('/')
def index():
    return app.send_static_file('index.html')

# ── Register blueprints here as features are added ────────────
from routes.activities import activities_bp
app.register_blueprint(activities_bp, url_prefix='/api')

# from routes.auth import auth_bp
# app.register_blueprint(auth_bp, url_prefix='/api/auth')

if __name__ == '__main__':
    init_db()
    print('🌍 GlobeTrotter starting on http://localhost:5000')
    app.run(debug=True, port=5000)
