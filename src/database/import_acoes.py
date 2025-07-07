import os
import yfinance as yf
from src.models.acao import db, Acao
from flask import Flask

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = os.path.join(basedir, 'database', 'app.db')

# Configuração da app Flask para usar o contexto do banco
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)

# Função para importar ações da B3
def importar_acoes_b3():
    print('Importando ações da B3...')
    tickers = yf.Tickers(' '.join([f'{l}{n}.SA' for l in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for n in range(1,10)]))
    # Alternativamente, use uma lista pública de tickers B3
    # Aqui, exemplo com alguns tickers conhecidos
    tickers_list = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'BBAS3.SA', 'B3SA3.SA', 'WEGE3.SA', 'MGLU3.SA',
        'LREN3.SA', 'RENT3.SA', 'SUZB3.SA', 'GGBR4.SA', 'CSNA3.SA', 'USIM5.SA', 'JBSS3.SA', 'PRIO3.SA', 'EGIE3.SA',
        'CPLE6.SA', 'ELET3.SA', 'ELET6.SA', 'BRFS3.SA', 'BRKM5.SA', 'BRAP4.SA', 'HAPV3.SA', 'NTCO3.SA', 'RAIZ4.SA'
    ]
    for symbol in tickers_list:
        info = yf.Ticker(symbol).info
        nome = info.get('shortName') or info.get('longName')
        if nome:
            acao = Acao.query.filter_by(symbol=symbol).first()
            if not acao:
                acao = Acao(symbol=symbol, nome=nome, bolsa='B3')
                db.session.add(acao)
    db.session.commit()
    print('Ações da B3 importadas.')

# Função para importar ações dos EUA (NYSE/NASDAQ)
def importar_acoes_usa():
    print('Importando ações dos EUA...')
    # Exemplo com alguns tickers conhecidos
    tickers_list = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ', 'WMT', 'PG', 'DIS', 'MA', 'HD',
        'BAC', 'XOM', 'KO', 'PFE', 'PEP', 'CSCO', 'T', 'VZ', 'ADBE', 'NFLX', 'CRM', 'ABT', 'MCD', 'COST', 'NKE', 'TMO'
    ]
    for symbol in tickers_list:
        info = yf.Ticker(symbol).info
        nome = info.get('shortName') or info.get('longName')
        if nome:
            acao = Acao.query.filter_by(symbol=symbol).first()
            if not acao:
                acao = Acao(symbol=symbol, nome=nome, bolsa='NYSE/NASDAQ')
                db.session.add(acao)
    db.session.commit()
    print('Ações dos EUA importadas.')

if __name__ == '__main__':
    with app.app_context():
        importar_acoes_b3()
        importar_acoes_usa()
        print('Importação concluída.') 