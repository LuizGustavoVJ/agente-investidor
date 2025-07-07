import jwt
from flask import Blueprint, jsonify, request, g, current_app
from models.user import User, db
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc6750 import BearerTokenValidator
import secrets
import datetime

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

JWT_SECRET = 'supersecretjwtkey'  # Troque para um segredo seguro em produção
JWT_ALG = 'HS256'

class SimpleToken:
    def __init__(self, payload):
        self.payload = payload

    def get(self, key, default=None):
        return self.payload.get(key, default)

    def is_expired(self):
        exp = self.payload.get('exp')
        if exp is None:
            return True
        return datetime.datetime.utcnow().timestamp() > exp

    def is_revoked(self):
        return False

    def get_scope(self):
        return None

class SimpleBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        try:
            payload = jwt.decode(token_string, JWT_SECRET, algorithms=[JWT_ALG])
            return SimpleToken(payload)
        except Exception:
            return None
    def request_invalid(self, request):
        return False
    def token_revoked(self, token):
        return False

require_oauth = ResourceProtector()
require_oauth.register_token_validator(SimpleBearerTokenValidator())

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({
            'success': False,
            'error': 'Todos os campos são obrigatórios.'
        }), 400
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({
            'success': False,
            'error': 'Usuário ou e-mail já cadastrado.'
        }), 400
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuário registrado com sucesso.'})

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({
            'success': False,
            'error': 'Usuário ou senha inválidos.'
        }), 401
    # Gerar JWT
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': exp.timestamp()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return jsonify({
        'success': True,
        'access_token': token,
        'token_type': 'Bearer'
    })

@user_bp.route('/me', methods=['GET'])
@require_oauth()
def me():
    token_obj = g.authlib_server_oauth2_token
    if not token_obj:
        return jsonify({'success': False, 'error': 'Token inválido.'}), 401
    user_id = token_obj.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Usuário não encontrado.'
        }), 404
    return jsonify({'success': True, 'user': user.to_dict()})
