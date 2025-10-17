from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "your_super_secret_flask_key"
CORS(app)
jwt = JWTManager(app)

# Register blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.profile import profile_bp
from routes.queries import queries_bp
from routes.agentic import agentic_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(queries_bp)
app.register_blueprint(agentic_bp)

if __name__ == "__main__":
    app.run(debug=True)
