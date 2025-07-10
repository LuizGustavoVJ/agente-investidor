import os
import sys
from flask import (
    Flask, send_from_directory, render_template, redirect, url_for, request
)
from flask_cors import CORS
from flask_migrate import Migrate

try:
    # Tentar imports relativos primeiro (quando executado diretamente)
    from models.acao import db
    from routes.user import user_bp
    from routes.agente import agente_bp
except ImportError:
    # Se falhar, usar imports absolutos (quando executado como módulo)
    from src.models.acao import db
    from src.routes.user import user_bp
    from src.routes.agente import agente_bp

# Adicionar o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'app.db')

app = Flask(__name__, template_folder='views')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir requisições do frontend
CORS(app)

app.register_blueprint(user_bp)
app.register_blueprint(agente_bp)

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


# Rotas de views
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login_page():
    return render_template('auth/login.html')


@app.route('/cadastro')
def cadastro_page():
    return render_template('auth/cadastro.html')


# Redirecionar para login se não autenticado (exceto login/cadastro/static)
@app.before_request
def require_login():
    # Não aplica redirecionamento para rotas de API
    if request.path.startswith('/api/'):
        return
    if request.endpoint in [
        'login_page', 'cadastro_page', 'static',
        'user.register', 'user.login'
    ]:
        return
    if not request.cookies.get('access_token') and \
            request.endpoint not in ['home']:
        return redirect(url_for('login_page'))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)