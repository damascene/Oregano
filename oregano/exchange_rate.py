from datetime import datetime
import inspect
import requests
import sys
import os
import json
import pkgutil
from threading import Thread
import time
import csv
import decimal
from decimal import Decimal as PyDecimal  # Qt 5.12 also exports Decimal
from collections import defaultdict

from . import networks
from .bitcoin import COIN
from .i18n import _
from .util import PrintError, ThreadJob, print_error, inv_base_units


DEFAULT_ENABLED = True
DEFAULT_CURRENCY = "USD"
DEFAULT_EXCHANGE = "CoinGecko"  # Note the exchange here should ideally also support history rates

# See https://en.wikipedia.org/wiki/ISO_4217
CCY_PRECISIONS = {'BHD': 3, 'BIF': 0, 'BYR': 0, 'CLF': 4, 'CLP': 0,
                  'CVE': 0, 'DJF': 0, 'GNF': 0, 'IQD': 3, 'ISK': 0,
                  'JOD': 3, 'JPY': 0, 'KMF': 0, 'KRW': 0, 'KWD': 3,
                  'LYD': 3, 'MGA': 1, 'MRO': 1, 'OMR': 3, 'PYG': 0,
                  'RWF': 0, 'TND': 3, 'UGX': 0, 'UYI': 0, 'VND': 0,
                  'VUV': 0, 'XAF': 0, 'XAU': 4, 'XOF': 0, 'XPF': 0}


def to_decimal(x):
    # helper function mainly for float->Decimal conversion, i.e.:
    #   >>> Decimal(41754.681)
    #   Decimal('41754.680999999996856786310672760009765625')
    #   >>> Decimal("41754.681")
    #   Decimal('41754.681')
    if isinstance(x, PyDecimal):
        return x
    return PyDecimal(str(x))


class ExchangeBase(PrintError):

    def __init__(self, on_quotes, on_history):
        self.history = {}
        self.history_timestamps = defaultdict(float)
        self.quotes = {}
        self.on_quotes = on_quotes
        self.on_history = on_history

    def get_json(self, site, get_string):
        # APIs must have https
        url = ''.join(['https://', site, get_string])
        response = requests.request('GET', url, headers={'User-Agent' : 'Oregano'}, timeout=20)
        if response.status_code != 200:
            raise RuntimeWarning("Response status: " + str(response.status_code))
        return response.json()

    def get_csv(self, site, get_string):
        url = ''.join(['https://', site, get_string])
        response = requests.request('GET', url, headers={'User-Agent' : 'Oregano'})
        if response.status_code != 200:
            raise RuntimeWarning("Response status: " + str(response.status_code))
        reader = csv.DictReader(response.content.decode().split('\n'))
        return list(reader)

    def name(self):
        return self.__class__.__name__

    def update_safe(self, ccy):
        try:
            self.print_error("getting fx quotes for", ccy)
            self.quotes = self.get_rates(ccy)
            self.print_error("received fx quotes")
        except Exception as e:
            self.print_error("failed fx quotes:", e)
        self.on_quotes()

    def update(self, ccy):
        t = Thread(target=self.update_safe, args=(ccy,), daemon=True)
        t.start()

    def read_historical_rates(self, ccy, cache_dir):
        filename = self._get_cache_filename(ccy, cache_dir)
        h, timestamp = None, 0.0
        if os.path.exists(filename):
            timestamp = os.stat(filename).st_mtime
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    h = json.loads(f.read())
                if h:
                    self.print_error("read_historical_rates: returning cached history from", filename)
            except Exception as e:
                self.print_error("read_historical_rates: error", repr(e))
        h = h or None
        return h, timestamp

    def _get_cache_filename(self, ccy, cache_dir):
        return os.path.join(cache_dir, self.name() + '_' + ccy)

    @staticmethod
    def _is_timestamp_old(timestamp):
        HOUR = 60.0*60.0  # number of seconds in an hour
        return time.time() - timestamp >= 24.0 * HOUR  # check history rates every 24 hours, as the granularity is per-day anyway

    def is_historical_rate_old(self, ccy):
        return self._is_timestamp_old(self.history_timestamps.get(ccy, 0.0))

    def _cache_historical_rates(self, h, ccy, cache_dir):
        ''' Writes the history, h, to the cache file. Catches its own exceptions
        and always returns successfully, even if the write process failed. '''
        wroteBytes, filename = 0, '(none)'
        try:
            filename = self._get_cache_filename(ccy, cache_dir)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json.dumps(h))
            wroteBytes = os.stat(filename).st_size
        except Exception as e:
            self.print_error("cache_historical_rates error:", repr(e))
            return False
        self.print_error(f"cache_historical_rates: wrote {wroteBytes} bytes to file {filename}")
        return True

    def get_historical_rates_safe(self, ccy, cache_dir):
        h, timestamp = self.read_historical_rates(ccy, cache_dir)
        if not h or self._is_timestamp_old(timestamp):
            try:
                self.print_error("requesting fx history for", ccy)
                h = self.request_history(ccy)
                self.print_error("received fx history for", ccy)
                if not h:
                    # Paranoia: No data; abort early rather than write out an
                    # empty file
                    raise RuntimeWarning(f"received empty history for {ccy}")
                self._cache_historical_rates(h, ccy, cache_dir)
            except Exception as e:
                self.print_error("failed fx history:", repr(e))
                return
        self.print_error("received history rates of length", len(h))
        self.history[ccy] = h
        self.history_timestamps[ccy] = timestamp
        self.on_history()

    def get_historical_rates(self, ccy, cache_dir):
        result, timestamp = self.history.get(ccy), self.history_timestamps.get(ccy, 0.0)

        if (not result or self._is_timestamp_old(timestamp)) and ccy in self.history_ccys():
            t = Thread(target=self.get_historical_rates_safe, args=(ccy, cache_dir), daemon=True)
            t.start()
        return result

    def history_ccys(self):
        return []

    def historical_rate(self, ccy, d_t):
        if d_t is None:
            return 'NaN'
        return self.history.get(ccy, {}).get(d_t.strftime('%Y-%m-%d'),'NaN')

    def get_currencies(self):
        rates = self.get_rates('')
        return sorted([str(a) for (a, b) in rates.items() if b is not None and len(a)==3])


class CoinGecko(ExchangeBase):

    def get_rates(self, ccy):
        json = self.get_json('api.coingecko.com', '/api/v3/coins/tether?localization=False&sparkline=false')
        json2 = self.get_json('explorer.ergon.network', '/ext/summary')
        xrg_price = json2['data'][0]['lastPrice']
        prices = json["market_data"]["current_price"]
        result = dict([(a[0].upper(),to_decimal(a[1])*to_decimal(xrg_price)) for a in prices.items()])
        result['XRG'] = PyDecimal(1)
        result['mXRG'] = PyDecimal(1000)
        return result

    def history_ccys(self):
        return ['AED', 'ARS', 'AUD', 'BTD', 'BHD', 'BMD', 'BRL', 'BTC',
                'CAD', 'CHF', 'CLP', 'CNY', 'CZK', 'DKK', 'ETH', 'EUR',
                'GBP', 'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'JPY', 'KRW',
                'KWD', 'LKR', 'LTC', 'MMK', 'MXH', 'MYR', 'NOK', 'NZD',
                'PHP', 'PKR', 'PLN', 'RUB', 'SAR', 'SEK', 'SGD', 'THB',
                'TRY', 'TWD', 'USD', 'VEF', 'VND', 'XAG', 'XAU', 'XDR',
                'ZAR']

    def request_history(self, ccy):
        history = self.get_json('api.coingecko.com', '/api/v3/coins/tether/market_chart?vs_currency=%s&days=max' % ccy)
        from datetime import datetime as dt
        return dict([(dt.utcfromtimestamp(h[0]/1000).strftime('%Y-%m-%d'), h[1])
                     for h in history['prices']])

class BitstampYadio(ExchangeBase):
    def get_rates(self, ccy):
        json_usd = self.get_json('www.bitstamp.net', '/api/v2/ticker/bchusd')
        json_ars = self.get_json('api.yadio.io', '/exrates/ARS')
        return {'ARS': to_decimal(json_usd['last']) / to_decimal(json_ars['ARS']['USD'])}


class CoinPaprika(ExchangeBase):

    def get_rates(self, ccy):
        ccys = ['BTC', 'ETH', 'USD', 'EUR', 'PLN', 'KRW', 'GBP', 'CAD', 'JPY', 'RUB', 'TRY', 'NZD', 'AUD', 'CHF', 'UAH',
                'HKD', 'SGD', 'NGN', 'PHP', 'MXN', 'BRL', 'THB', 'CLP', 'CNY', 'CZK', 'DKK', 'HUF', 'IDR', 'ILS', 'INR',
                'MYR', 'NOK', 'PKR', 'SEK', 'TWD', 'ZAR', 'VND', 'BOB', 'COP', 'PEN', 'ARS', 'ISK']
        json = self.get_json('api.coinpaprika.com', '/v1/tickers/xrg-ergon?quotes=%s' % ','.join(ccys))
        prices = json['quotes']
        return dict([(curr, to_decimal(data["price"])) for curr, data in prices.items()])

    def history_ccys(self):
        return ['BTC', 'USD']

    def request_history(self, ccy):
        history = self.get_json('api.coinpaprika.com', '/v1/tickers/xrg-ergon/historical?start=2021-07-08&interval=24h')
        return dict([(item['timestamp'].split('T')[0], item['price']) for item in history])

def dictinvert(d):
    inv = {}
    for k, vlist in d.items():
        for v in vlist:
            keys = inv.setdefault(v, [])
            keys.append(k)
    return inv

def get_exchanges_and_currencies():
    try:
        data = pkgutil.get_data(__name__, 'currencies.json')
        return json.loads(data.decode('utf-8'))
    except:
        pass

    path = os.path.join(os.path.dirname(__file__), 'currencies.json')
    d = {}
    is_exchange = lambda obj: (inspect.isclass(obj)
                               and issubclass(obj, ExchangeBase)
                               and obj != ExchangeBase)
    exchanges = dict(inspect.getmembers(sys.modules[__name__], is_exchange))
    for name, klass in exchanges.items():
        exchange = klass(None, None)
        try:
            d[name] = exchange.get_currencies()
            print_error(name, "ok")
        except:
            print_error(name, "error")
            continue
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, indent=4, sort_keys=True))
    return d


CURRENCIES = get_exchanges_and_currencies()


def get_exchanges_by_ccy(history=True):
    if not history:
        return dictinvert(CURRENCIES)
    d = {}
    exchanges = CURRENCIES.keys()
    for name in exchanges:
        try:
            klass = globals()[name]
        except KeyError:
            # can happen if currencies.json is not in synch with this .py file, see #1559
            continue
        exchange = klass(None, None)
        d[name] = exchange.history_ccys()
    return dictinvert(d)


class FxThread(ThreadJob):

    default_currency = DEFAULT_CURRENCY
    default_exchange = DEFAULT_EXCHANGE

    def __init__(self, config, network):
        self.config = config
        self.network = network
        self.ccy = self.get_currency()
        self.history_used_spot = False
        self.ccy_combo = None
        self.hist_checkbox = None
        self.timeout = 0.0
        self.cache_dir = os.path.join(config.path, 'cache')
        self.set_exchange(self.config_exchange())
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

    def get_currencies(self, h):
        d = get_exchanges_by_ccy(h)
        return sorted(d.keys())

    def get_exchanges_by_ccy(self, ccy, h):
        d = get_exchanges_by_ccy(h)
        return d.get(ccy, [])

    def ccy_amount_str(self, amount, commas, default_prec=2, is_diff=False):
        prec = CCY_PRECISIONS.get(self.ccy, default_prec)
        diff_str = ''
        if is_diff:
            diff_str = '+' if amount >= 0 else '-'
        fmt_str = "%s{:%s.%df}" % (diff_str, "," if commas else "", max(0, prec))
        try:
            rounded_amount = round(amount, prec)
        except decimal.InvalidOperation:
            rounded_amount = amount
        return fmt_str.format(rounded_amount)

    def run(self):
        """This runs from the Network thread. It is invoked roughly every
        100ms (see network.py), with actual work being done every 2.5 minutes."""
        if self.is_enabled():
            if self.timeout <= time.time():
                self.exchange.update(self.ccy)
                if (self.show_history()
                        and (self.timeout == 0  # forced update
                             # OR > 24 hours have expired
                             or self.exchange.is_historical_rate_old(self.ccy))):
                    # Update historical rates. Note this doesn't actually
                    # go out to the network unless cache file is missing
                    # and/or >= 24 hours have passed since last fetch.
                    self.exchange.get_historical_rates(self.ccy, self.cache_dir)
                # And, finally, update self.timeout so we execute this branch
                # every ~2.5 minutes
                self.timeout = time.time() + 150

    @staticmethod
    def is_supported():
        """Fiat currency is only supported on BCH MainNet, for all other chains it is not supported."""
        return not networks.net.TESTNET

    def is_enabled(self):
        return bool(self.is_supported() and self.config.get('use_exchange_rate', DEFAULT_ENABLED))

    def set_enabled(self, b):
        return self.config.set_key('use_exchange_rate', bool(b))

    def get_history_config(self):
        return bool(self.config.get('history_rates'))

    def set_history_config(self, b):
        self.config.set_key('history_rates', bool(b))

    def get_fiat_address_config(self):
        return bool(self.config.get('fiat_address'))

    def set_fiat_address_config(self, b):
        self.config.set_key('fiat_address', bool(b))

    def get_currency(self):
        """Use when dynamic fetching is needed"""
        return self.config.get("currency", self.default_currency)

    def config_exchange(self):
        """Returns the currently-configured exchange."""
        return self.config.get('use_exchange', self.default_exchange)

    def show_history(self):
        return self.is_enabled() and self.get_history_config() and self.ccy in self.exchange.history_ccys()

    def set_currency(self, ccy):
        self.ccy = ccy
        if self.get_currency() != ccy:
            self.config.set_key('currency', ccy, True)
        self.timeout = 0  # Force update because self.ccy changes
        self.on_quotes()

    def set_exchange(self, name):
        default_class = globals().get(self.default_exchange)
        class_ = globals().get(name, default_class)
        if self.config_exchange() != name:
            self.config.set_key('use_exchange', name, True)
        self.exchange = class_(self.on_quotes, self.on_history)
        if self.get_history_config() and self.ccy not in self.exchange.history_ccys() and class_ != default_class:
            # this exchange has no history for this ccy. Try the default exchange.
            # If that also fails the user will be stuck in a strange UI
            # situation where the checkbox is checked but they see no history
            # Note this code is here to migrate users from previous history
            # API exchanges in config that are no longer serving histories.
            self.set_exchange(self.default_exchange)
            return
        self.print_error("using exchange", name)
        # A new exchange means new fx quotes, initially empty.
        # This forces a quote refresh, which will happen in the Network thread.
        self.timeout = 0

    def on_quotes(self):
        if self.network:
            self.network.trigger_callback('on_quotes')

    def on_history(self):
        if self.network:
            self.network.trigger_callback('on_history')

    def exchange_rate(self):
        '''Returns None, or the exchange rate as a PyDecimal'''
        rate = self.exchange.quotes.get(self.ccy)
        if rate is None:
            return PyDecimal('NaN')
        return PyDecimal(rate)

    def format_amount_and_units(self, btc_balance, is_diff=False, commas=True):
        amount_str = self.format_amount(btc_balance, is_diff=is_diff, commas=commas)
        return '' if not amount_str else "%s %s" % (amount_str, self.ccy)

    def format_amount(self, btc_balance, is_diff=False, commas=True):
        rate = self.exchange_rate()
        return ('' if rate.is_nan()
                else self.value_str(btc_balance, rate, is_diff=is_diff, commas=commas))

    def get_fiat_status_text(self, btc_balance, base_unit, decimal_point):
        rate = self.exchange_rate()
        default_prec = 2
        if base_unit == inv_base_units.get(2):  # if base_unit == 'bits', increase precision on fiat as bits is pretty tiny as of 2019
            default_prec = 4
        return _("  (No FX rate available)") if rate.is_nan() else " 1 %s~%s %s" % (base_unit,
            self.value_str(COIN / (10**(8 - decimal_point)), rate, default_prec ), self.ccy )

    def value_str(self, fixoshis, rate, default_prec=2, is_diff=False, commas=True):
        value = (PyDecimal('NaN') if fixoshis is None
                 else PyDecimal(fixoshis) / COIN * PyDecimal(rate))
        if value.is_nan():
            return _("No data")
        return "%s" % (self.ccy_amount_str(value, commas, default_prec, is_diff=is_diff))

    def fiat_to_amount(self, fiat):
        rate = self.exchange_rate()
        return (PyDecimal('NaN') if rate.is_nan()
                else int(PyDecimal(fiat) / rate * COIN))

    def history_rate(self, d_t):
        if d_t is None:
            return PyDecimal('NaN')
        rate = self.exchange.historical_rate(self.ccy, d_t)
        # Frequently there is no rate for today, until tomorrow :)
        # Use spot quotes in that case
        if rate =='NaN' and (datetime.today().date() - d_t.date()).days <= 2:
            rate = self.exchange.quotes.get(self.ccy, 'NaN')
            self.history_used_spot = True
        return PyDecimal(rate)

    def historical_value_str(self, fixoshis, d_t):
        rate = self.history_rate(d_t)
        return self.value_str(fixoshis, rate)

    def historical_value(self, fixoshis, d_t):
        rate = self.history_rate(d_t)
        return PyDecimal(fixoshis) / COIN * PyDecimal(rate)

    def timestamp_rate(self, timestamp):
        from .util import timestamp_to_datetime
        date = timestamp_to_datetime(timestamp)
        return self.history_rate(date)
