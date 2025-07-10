import random


class ApiClient:
    """
    Cliente de API fictício para simular respostas das APIs YahooFinance e DataBank.
    """
    def call_api(self, endpoint, query=None):
        if endpoint == 'YahooFinance/get_stock_profile':
            return {
                'quoteSummary': {
                    'result': [{
                        'summaryProfile': {
                            'longBusinessSummary': (
                                'Empresa fictícia para testes.'
                            ),
                            'sector': 'Energia',
                            'industry': 'Petróleo e Gás',
                            'website': 'https://www.exemplo.com'
                        }
                    }]
                }
            }
        elif endpoint == 'YahooFinance/get_stock_chart':
            price = round(random.uniform(10, 100), 2)
            closes = [
                round(price * (1 + random.uniform(-0.05, 0.05)), 2)
                for _ in range(30)
            ]
            closes[0] = round(price * 0.95, 2)
            closes[-1] = round(price * 1.05, 2)
            return {
                'chart': {
                    'result': [{
                        'meta': {
                            'regularMarketPrice': price,
                            'marketCap': random.randint(
                                1_000_000_000, 100_000_000_000
                            ),
                            'currency': 'BRL',
                            'exchangeName': 'B3',
                            'regularMarketVolume': random.randint(
                                1_000_000, 10_000_000
                            ),
                            'longName': 'Empresa Fictícia'
                        },
                        'timestamp': [i for i in range(30)],
                        'indicators': {
                            'quote': [{
                                'close': closes
                            }]
                        }
                    }]
                }
            }
        elif endpoint == 'YahooFinance/get_stock_insights':
            return {
                'finance': {
                    'result': {
                        'symbol': query.get('symbol', 'N/A'),
                        'recommendation': {
                            'rating': 'BUY',
                            'targetPrice': round(random.uniform(20, 120), 2)
                        }
                    }
                }
            }
        elif endpoint == 'DataBank/indicator_data':
            return {
                'countryName': 'Brasil',
                'indicatorName': 'PIB',
                'data': {'2022': 1.8e12, '2021': 1.7e12},
            }
        elif endpoint == 'DataBank/indicator_list':
            return {
                'total': 2,
                'items': [
                    {
                        'indicatorCode': 'NY.GDP.MKTP.CD',
                        'indicatorName': 'GDP (current US$)'
                    },
                    {
                        'indicatorCode': 'FP.CPI.TOTL',
                        'indicatorName': (
                            'Inflation, consumer prices (annual %)'
                        )
                    }
                ]
            }
        else:
            return {
                'error': f'Endpoint não implementado: {endpoint}'
            } 