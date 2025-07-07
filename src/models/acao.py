from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Acao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(120), nullable=True)
    bolsa = db.Column(db.String(20), nullable=True)  # Ex: B3, NYSE, NASDAQ

    def __repr__(self):
        return f'<Acao {self.symbol}>'

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'nome': self.nome,
            'bolsa': self.bolsa
        } 