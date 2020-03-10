#!/usr/bin/env python3

# API Related Section

""" API """
PRIVATE_API_URL = 'https://max-api.maicoin.com/api'
PUBLIC_API_URL = 'https://max-api.maicoin.com/api'

PRIVATE_API_VERSION = 'v2'
PUBLIC_API_VERSION = 'v2'

""" Exchange """
EXCHANGE_NAME = 'MAX'
EXCHANGE_TOKEN = 'MAX'

# Customized Section
MINIMUM_ORDER_AMOUNT = {
    'BAT': 20.0, 'BCH': 0.03, 'BCNT': 300.0, 'BTC': 0.0015, 'CCCX': 2100.0,
    'EOS': 1.7, 'ETH': 0.05, 'FMF': 8000.0, 'GNT': 110.0, 'KNC': 36.0,
    'LTC': 0.1112, 'MAX': 100.0, 'MITH': 190.0, 'OMG': 5.0, 'SEELE': 1180.0,
    'TRX': 340.0, 'TWD': 250.0, 'USDT': 8.0, 'XRP': 27.0, 'ZRX': 30.0,
}

MINIMUM_AMOUNT_KEY = 'moq'

# pyCryptoTrader Section

""" Balances """
BALANCE_AVAILABLE = 'balance'
BALANCE_TOTAL = None

""" Depths """
DEPTHS_KEY_AMOUNT = 1
DEPTHS_KEY_PRICE = 0

""" Orders """
ORDER_AMOUNT_MAX = None
ORDER_AMOUNT_MINIMUM = MINIMUM_AMOUNT_KEY
ORDER_AMOUNT_EXECUTED = 'executed_volume'
ORDER_AMOUNT_ORIGINAL = 'volume'
ORDER_AMOUNT_REMAINING = 'remaining_volume'

ORDER_FEE_BY_CURRENCY = 'fee_currency'
ORDER_FEE_BY_EXCHANGE = None

ORDER_PRICE_AVERAGE = 'avg_price'
ORDER_PRICE_PLACED = 'price'

ORDER_STATUS_IN_PROGRESS = 'wait'
ORDER_STATUS_PARTIAL_DEAL = 'convert'
ORDER_STATUS_COMPLETED = 'done'
ORDER_STATUS_PARTIAL_COMPLETED = None
ORDER_STATUS_CANCELLED = 'cancel'

ORDER_ID_PLACED = 'id'

""" Precisions """
PRECISION_UNIT_BASE = 'base_unit_precision'
PRECISION_UNIT_QUOTE = 'quote_unit_precision'

""" Tickers """
TICKER_PRICE_HIGH = 'high'
TICKER_PRICE_LAST = 'last'
TICKER_PRICE_LOW = 'low'

# Shared Section
COMMON_KEY_ACTION = 'side'
COMMON_KEY_AMOUNT = 'amount'
COMMON_KEY_ASKS = 'asks'
COMMON_KEY_BASE = 'base'
COMMON_KEY_BIDS = 'bids'
COMMON_KEY_BUY = 'buy'
COMMON_KEY_COUNT = 'count'
COMMON_KEY_CURRENCY = 'currency'
COMMON_KEY_DATA = 'data'
COMMON_KEY_FEE = 'fee'
COMMON_KEY_ID = 'id'
COMMON_KEY_LIMIT = 'limit'
COMMON_KEY_MARKET = 'market'
COMMON_KEY_NAME = 'name'
COMMON_KEY_PAIR = 'pair'
COMMON_KEY_PRICE = 'price'
COMMON_KEY_QUOTE = 'quote'
COMMON_KEY_SELL = 'sell'
COMMON_KEY_STATUS = 'state'
COMMON_KEY_TIMESTAMP = 'updated_at'
COMMON_KEY_TOTAL = 'total'
COMMON_KEY_TYPE = 'type'
COMMON_KEY_VOLUME = 'volume'
