import json

import pytest
from pandas import DataFrame

from earthzetaorg.data.converter import parse_ticker_dataframe
from earthzetaorg.strategy.default_strategy import DefaultStrategy


@pytest.fixture
def result():
    with open('earthzetaorg/tests/testdata/ETH_BTC-1m.json') as data_file:
        return parse_ticker_dataframe(json.load(data_file), '1m', pair="UNITTEST/BTC",
                                      fill_missing=True)


def test_default_strategy_structure():
    assert hasattr(DefaultStrategy, 'minimal_roi')
    assert hasattr(DefaultStrategy, 'stoploss')
    assert hasattr(DefaultStrategy, 'ticker_interval')
    assert hasattr(DefaultStrategy, 'populate_indicators')
    assert hasattr(DefaultStrategy, 'populate_buy_trend')
    assert hasattr(DefaultStrategy, 'populate_sell_trend')


def test_default_strategy(result):
    strategy = DefaultStrategy({})

    metadata = {'pair': 'ETH/BTC'}
    assert type(strategy.minimal_roi) is dict
    assert type(strategy.stoploss) is float
    assert type(strategy.ticker_interval) is str
    indicators = strategy.populate_indicators(result, metadata)
    assert type(indicators) is DataFrame
    assert type(strategy.populate_buy_trend(indicators, metadata)) is DataFrame
    assert type(strategy.populate_sell_trend(indicators, metadata)) is DataFrame
