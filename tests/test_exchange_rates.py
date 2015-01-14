# -*- coding: utf-8 -*-
import decimal
import mock
from datetime import date

import rockefeller
import rockefeller.gae.exchange_rates


def setup_module(module):
    module.usd = rockefeller.Currency(name='United States Dollar',
                                      code='USD', numeric='840',
                                      symbol=u'$', exponent=2).support()
    module.eur = rockefeller.Currency(name='Euro',
                                      code='EUR', numeric='978',
                                      symbol=u'€', exponent=2).support()


class TestExchangeRates:
    def test_add_exchange_rate(self):
        today = date.today()
        er = rockefeller.ExchangeRates(store=mock.Mock())
        er.add_exchange_rate(base_currency=usd, currency=eur, exchange_rate=1.0, date=today)
        er.store.add_exchange_rate.assert_called_once_with(usd, eur, '1.0', today)

    def test_remove_exchange_rate(self):
        today = date.today()
        er = rockefeller.ExchangeRates(store=mock.Mock())
        er.remove_exchange_rate(base_currency=usd, currency=eur, date=today)
        er.store.remove_exchange_rate.assert_called_once_with(usd, eur, today)

    def test_get_exchange_rate(self):
        today = date.today()
        er = rockefeller.ExchangeRates(store=mock.Mock())
        er.store.get_exchange_rate.return_value = 1.0
        rate = er.get_exchange_rate(base_currency=usd, currency=eur, date=today)
        er.store.get_exchange_rate.assert_called_once_with(usd, eur, today)
        assert rate == 1.0

    def test_get_exchange_equivalent(self):
        today = date.today()
        er = rockefeller.ExchangeRates(store=mock.Mock())
        er.store.get_exchange_rate.return_value = None
        rate = er.get_exchange_rate(base_currency=usd, currency=eur, date=today)
        assert er.store.get_exchange_rate.call_count == 2
        er.store.get_exchange_rate.assert_called_with(eur, usd, today)
        assert rate is None


class TestExchangeRate:
    def test_rate_as_decimal(self):
        er = rockefeller.ExchangeRate(usd, eur, .78, date.today())
        assert isinstance(er.rate, decimal.Decimal)


class TestMemoryExchangeRates:
    def test_add_exchange_rate(self):
        today = date.today()
        st = rockefeller.MemoryExchangeRates()
        st.add_exchange_rate(usd, eur, 1.0, today)

        assert st.get_exchange_rate(
            rockefeller.Currency.USD, rockefeller.Currency.EUR, today) == 1.0

    def test_remove_exchange_rate_added(self):
        today = date.today()
        st = rockefeller.MemoryExchangeRates()
        st.add_exchange_rate(usd, eur, 1.0, today)
        st.add_exchange_rate(eur, usd, 1.0, today)
        st.remove_exchange_rate(usd, eur, today)

        assert st.get_exchange_rate(
            rockefeller.Currency.USD, rockefeller.Currency.EUR, today) is None
        assert st.get_exchange_rate(
            rockefeller.Currency.EUR, rockefeller.Currency.USD, today) is None

    def test_remove_exchange_rate(self):
        today = date.today()
        st = rockefeller.MemoryExchangeRates()
        st.remove_exchange_rate(usd, eur, today)

        assert st.get_exchange_rate(
            rockefeller.Currency.USD, rockefeller.Currency.EUR, today) is None
        assert st.get_exchange_rate(
            rockefeller.Currency.EUR, rockefeller.Currency.USD, today) is None

    def test_not_stored_exchange_rate(self):
        today = date.today()
        st = rockefeller.MemoryExchangeRates()

        assert st.get_exchange_rate(
            rockefeller.Currency.USD, rockefeller.Currency.EUR, today) is None


class TestGAEExchangeRates:
    def test_add_exchange_rate(self):
        st = rockefeller.gae.exchange_rates.GAEExchangeRates(mock.Mock())
        st.add_exchange_rate(usd, eur, 1.0)

        st.model.add_exchange_rate.assert_called_once_with(usd, eur, 1.0)

    def test_remove_exchange_rate_added(self):
        st = rockefeller.gae.exchange_rates.GAEExchangeRates(mock.Mock())
        st.add_exchange_rate(usd, eur, 1.0)
        st.remove_exchange_rate(usd, eur)

        st.model.remove_exchange_rate.assert_any_call(usd, eur)
        st.model.remove_exchange_rate.assert_any_call(eur, usd)

    def test_remove_exchange_rate(self):
        st = rockefeller.gae.exchange_rates.GAEExchangeRates(mock.Mock())
        st.remove_exchange_rate(usd, eur)

        st.model.remove_exchange_rate.assert_any_call(usd, eur)
        st.model.remove_exchange_rate.assert_any_call(eur, usd)

    def test_get_exchange_rate(self):
        st = rockefeller.gae.exchange_rates.GAEExchangeRates(mock.Mock())
        st.get_exchange_rate(usd, eur)

        st.model.get_exchange_rate.assert_called_once_with(usd, eur)

    def test_exchange_rate_same_currency(self):
        st = rockefeller.gae.exchange_rates.GAEExchangeRates(mock.Mock())

        assert decimal.Decimal(1) == st.get_exchange_rate(eur, eur)
