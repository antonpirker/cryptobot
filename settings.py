import os

# database settings
DB_NAME = os.getenv('CRYPTOBOT_DB_NAME', 'cryptobot')
DB_USER = os.getenv('CRYPTOBOT_DB_USER', 'cryptobot')
DB_PASSWORD = os.getenv('CRYPTOBOT_DB_PASSWORD', 'cryptobot')
DB_HOST = os.getenv('CRYPTOBOT_DB_HOST', 'localhost')

# websocket api configuration
COINIGY_SOCKET_URL = 'wss://sc-02.coinigy.com/socketcluster/'

COINIGY_API_KEY = os.getenv('CRYPTOBOT_COINIGY_API_KEY', '')
COINIGY_API_SECRET = os.getenv('CRYPTOBOT_COINIGY_API_SECRET', '')
COINIGY_SOCKET_CREDENTIALS = {
    'apiKey': COINIGY_API_KEY,
    'apiSecret': COINIGY_API_SECRET,
}

# settings for Coinigy API
COINIGY_API_BASE_URL_PRODUCTION = 'https://api.coinigy.com/api/v1/'
COINIGY_API_BASE_URL_MOCK_SERVER = 'https://private-anon-b1b0ee03ff-coinigy.apiary-mock.com/api/v1/'
COINIGY_API_BASE_URL_DEBUGGING_PROXY = 'https://private-anon-b1b0ee03ff-coinigy.apiary-proxy.com/api/v1/'
COINIGY_API_BASE_URL = COINIGY_API_BASE_URL_PRODUCTION

# markets we want to trade in
# for decimal_precision see:
# https://blog.coinigy.com/2017/09/exchange-update-kraken-reducing-price-precision-round-2/
TRADING_MARKETS = [
    {
        'exchange_code': 'BTRX',
        'primary_currency': 'BTC',
        'secondary_currency': 'USDT',
        'decimal_precision': 2,
    },
#    {
#        'exchange_code': 'BTRX',
#        'primary_currency': 'ETH',
#        'secondary_currency': 'USDT',
#        'decimal_precision': 2,
#    },
#    {
#        'exchange_code': 'BTRX',
#        'primary_currency': 'XRP',
#        'secondary_currency': 'USDT',
#        'decimal_precision': 2,
#    },
#    {
#        'exchange_code': 'BTRX',
#        'primary_currency': 'LTC',
#        'secondary_currency': 'USDT',
#        'decimal_precision': 2,
#    },
]


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, 'templates')