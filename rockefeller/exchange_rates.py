# -*- coding: utf-8 -*-
import decimal
from collections import namedtuple


class ExchangeRate(namedtuple('ExchangeRate', 'code_from code_to rate date')):
    """Class for creating exchange rate objects. An exchange rate object
    stores the ``rate`` between two currency codes, optionally for a specific date.

    Initialization params:

        ``code_from``
            Code of currency used as the base.

        ``code_to``
            Code of currency used as the target.

        ``rate``
            Exchange rate between currency codes. numeric or string.

        ``date``
            Date for the exchange rate. datetime, default to None.
    """
    def __new__(cls, code_from, code_to, rate, date=None):
        if not isinstance(rate, decimal.Decimal):
            rate = decimal.Decimal(str(rate))
        return super(ExchangeRate, cls).__new__(cls, code_from, code_to, rate, date)


class ExchangeRates(object):
    def __init__(self, store):
        self.store = store

    def add_exchange_rate(self, base_currency, currency, exchange_rate, date=None):
        """Store an exchange rate between two currencies.

        :param base_currency: Currency to use as base.
        :param currency: Currency to use as target.
        :param exchange_rate: Exchange rate between ``base_currency`` and
            ``currency``.
        :param date: Date of the rate.
            :class:`datetime.date`.
        """
        self.store.add_exchange_rate(base_currency, currency,
                                     str(exchange_rate), date)

    def remove_exchange_rate(self, base_currency, currency, date=None):
        """Remove an exchange rate between two currencies.

        :param base_currency: Currency to use as base.
        :param currency: Currency to use as target.
        :param exchange_rate: Exchange rate between ``base_currency`` and
            ``currency``.
        :param date: Date of the rate.
            :class:`datetime.date`.
        """
        self.store.remove_exchange_rate(base_currency, currency, date)

    def get_exchange_rate(self, base_currency, currency, indirection_currency=None, date=None):
        """Get exchange rate of a currency relatively to another one.

        If rate for ``currency`` relatively to ``base_currency`` can't be
        found the rate for ``base_currency`` relatively to ``currency`` will
        be searched and if it's found rate is going to be its inverse. Otherwise
        will try with indirection_currency if is set.

        :param base_currency: Currency used as the base.
            :class:`~rockefeller.currency.Currency` instance.
        :param currency: Currency you want to know its exchange rate in
            relation to ``base_currency``.
            :class:`~rockefeller.currency.Currency` instance.
        :param indirection_currency: Use this currency as the indirection
            currency. :class:`~rockefeller.currency.Currency` instance.
        :param date: Date for the exchange rate.
            :class:`datetime.date`.

        :return: Exchange rate as a ``decimal``.
        """
        # get rate from store
        rate = self.store.get_exchange_rate(base_currency, currency, date)
        if rate:
            return decimal.Decimal(str(rate))
        # else try with inverse
        inverse = self.store.get_exchange_rate(currency, base_currency, date)
        if inverse:
            return decimal.Decimal(1) / decimal.Decimal(inverse)
        # else try with indirection_currency
        if indirection_currency:
            rate_from_base = get_exchange_rate(self.currency, indirection_currency, date)
            rate_base_to = get_exchange_rate(indirection_currency, currency, date)
            if rate_from_base and rate_base_to:
                rate = rate_from_base * rate_base_to
                return decimal.Decimal(str(rate))
        return rate


class MemoryExchangeRates(object):

    def __init__(self):
        self.rates = {}

    def _get_key(self, base_currency, currency, date):
        return hash(base_currency), hash(currency), hash(date)

    def add_exchange_rate(self, base_currency, currency, exchange_rate, date):
        """Store exchange rate of one currency relatively to another one.

        :param base_currency: Currency used as the base.
            :class:`~rockefeller.currency.Currency` instance.
        :param currency: Currency you want to know its exchange rate in
            relation to ``base_currency``.
            :class:`~rockefeller.currency.Currency` instance.
        :param exchange_rate: Exchange rate as a string. :class:`str` instance.
        :param date: Date for the exchange rate.
            :class:`datetime.date`.
        """
        self.rates[self._get_key(base_currency, currency, date)] = exchange_rate

    def remove_exchange_rate(self, base_currency, currency, date):
        """Remove exchange rate of one currency relatively to another one.

        If an exchange rate between ``base_currency`` and ``currency`` can't be
        found is going to try to find a rate between ``currency`` and
        ``base_currency``.

        :param base_currency: Currency used as the base.
            :class:`~rockefeller.currency.Currency` instance.
        :param currency: Currency you want to know its exchange rate in
            relation to ``base_currency``.
            :class:`~rockefeller.currency.Currency` instance.
        :param date: Date for the exchange rate.
            :class:`datetime.date`.
        """
        self.rates.pop(self._get_key(base_currency, currency, date), None)
        self.rates.pop(self._get_key(currency, base_currency, date), None)

    def get_exchange_rate(self, base_currency, currency, date):
        """Get exchange rate of a currency relatively to another one.

        :param base_currency: Currency used as the base.
            :class:`~rockefeller.currency.Currency` instance.
        :param currency: Currency you want to know its exchange rate in
            relation to ``base_currency``.
            :class:`~rockefeller.currency.Currency` instance.
        :param date: Date for the exchange rate.
            :class:`datetime.date`.

        :return: Exchange rate as a string. :class:`str` instance.
        """
        return self.rates.get(self._get_key(base_currency, currency, date))

exchange_rates = ExchangeRates(store=MemoryExchangeRates())
add_exchange_rate = exchange_rates.add_exchange_rate
remove_exchange_rate = exchange_rates.remove_exchange_rate
get_exchange_rate = exchange_rates.get_exchange_rate
