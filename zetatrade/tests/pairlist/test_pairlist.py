# pragma pylint: disable=missing-docstring,C0103,protected-access

from unittest.mock import MagicMock, PropertyMock

from earthzetaorg import OperationalException
from earthzetaorg.constants import AVAILABLE_PAIRLISTS
from earthzetaorg.resolvers import PairListResolver
from earthzetaorg.tests.conftest import get_patched_earthzetaorgbot
import pytest

# whitelist, blacklist


@pytest.fixture(scope="function")
def whitelist_conf(default_conf):
    default_conf['stake_currency'] = 'BTC'
    default_conf['exchange']['pair_whitelist'] = [
        'ETH/BTC',
        'TKN/BTC',
        'TRST/BTC',
        'SWT/BTC',
        'BCC/BTC'
    ]
    default_conf['exchange']['pair_blacklist'] = [
        'BLK/BTC'
    ]
    default_conf['pairlist'] = {'method': 'StaticPairList',
                                'config': {'number_assets': 3}
                                }

    return default_conf


def test_load_pairlist_noexist(mocker, markets, default_conf):
    earthzetaorgbot = get_patched_earthzetaorgbot(mocker, default_conf)
    mocker.patch('earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets))
    with pytest.raises(OperationalException,
                       match=r"Impossible to load Pairlist 'NonexistingPairList'. "
                             r"This class does not exist or contains Python code errors."):
        PairListResolver('NonexistingPairList', earthzetaorgbot, default_conf).pairlist


def test_refresh_market_pair_not_in_whitelist(mocker, markets, whitelist_conf):

    earthzetaorgbot = get_patched_earthzetaorgbot(mocker, whitelist_conf)

    mocker.patch('earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets))
    earthzetaorgbot.pairlists.refresh_pairlist()
    # List ordered by BaseVolume
    whitelist = ['ETH/BTC', 'TKN/BTC']
    # Ensure all except those in whitelist are removed
    assert set(whitelist) == set(earthzetaorgbot.pairlists.whitelist)
    # Ensure config dict hasn't been changed
    assert (whitelist_conf['exchange']['pair_whitelist'] ==
            earthzetaorgbot.config['exchange']['pair_whitelist'])


def test_refresh_pairlists(mocker, markets, whitelist_conf):
    earthzetaorgbot = get_patched_earthzetaorgbot(mocker, whitelist_conf)

    mocker.patch('earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets))
    earthzetaorgbot.pairlists.refresh_pairlist()
    # List ordered by BaseVolume
    whitelist = ['ETH/BTC', 'TKN/BTC']
    # Ensure all except those in whitelist are removed
    assert set(whitelist) == set(earthzetaorgbot.pairlists.whitelist)
    assert whitelist_conf['exchange']['pair_blacklist'] == earthzetaorgbot.pairlists.blacklist


def test_refresh_pairlist_dynamic(mocker, markets, tickers, whitelist_conf):
    whitelist_conf['pairlist'] = {'method': 'VolumePairList',
                                  'config': {'number_assets': 5}
                                  }
    mocker.patch.multiple(
        'earthzetaorg.exchange.Exchange',
        markets=PropertyMock(return_value=markets),
        get_tickers=tickers,
        exchange_has=MagicMock(return_value=True)
    )
    earthzetaorgbot = get_patched_earthzetaorgbot(mocker, whitelist_conf)

    # argument: use the whitelist dynamically by exchange-volume
    whitelist = ['ETH/BTC', 'TKN/BTC', 'BTT/BTC']
    earthzetaorgbot.pairlists.refresh_pairlist()

    assert whitelist == earthzetaorgbot.pairlists.whitelist

    whitelist_conf['pairlist'] = {'method': 'VolumePairList',
                                  'config': {}
                                  }
    with pytest.raises(OperationalException,
                       match=r'`number_assets` not specified. Please check your configuration '
                             r'for "pairlist.config.number_assets"'):
        PairListResolver('VolumePairList', earthzetaorgbot, whitelist_conf).pairlist


def test_VolumePairList_refresh_empty(mocker, markets_empty, whitelist_conf):
    earthzetaorgbot = get_patched_earthzetaorgbot(mocker, whitelist_conf)
    mocker.patch('earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets_empty))

    # argument: use the whitelist dynamically by exchange-volume
    whitelist = []
    whitelist_conf['exchange']['pair_whitelist'] = []
    earthzetaorgbot.pairlists.refresh_pairlist()
    pairslist = whitelist_conf['exchange']['pair_whitelist']

    assert set(whitelist) == set(pairslist)


@pytest.mark.parametrize("precision_filter,base_currency,key,whitelist_result", [
    (False, "BTC", "quoteVolume", ['ETH/BTC', 'TKN/BTC', 'BTT/BTC']),
    (False, "BTC", "bidVolume", ['BTT/BTC', 'TKN/BTC', 'ETH/BTC']),
    (False, "USDT", "quoteVolume", ['ETH/USDT', 'LTC/USDT']),
    (False, "ETH", "quoteVolume", []),  # this replaces tests that were removed from test_exchange
    (True, "BTC", "quoteVolume", ["ETH/BTC", "TKN/BTC"]),
    (True, "BTC", "bidVolume", ["TKN/BTC", "ETH/BTC"])
])
def test_VolumePairList_whitelist_gen(mocker, whitelist_conf, markets, tickers, base_currency, key,
                                      whitelist_result, precision_filter) -> None:
    whitelist_conf['pairlist']['method'] = 'VolumePairList'
    mocker.patch('earthzetaorg.exchange.Exchange.exchange_has', MagicMock(return_value=True))
    earthzetaorg = get_patched_earthzetaorgbot(mocker, whitelist_conf)
    mocker.patch('earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets))
    mocker.patch('earthzetaorg.exchange.Exchange.get_tickers', tickers)
    mocker.patch('earthzetaorg.exchange.Exchange.symbol_price_prec', lambda s, p, r: round(r, 8))

    earthzetaorg.pairlists._precision_filter = precision_filter
    earthzetaorg.config['stake_currency'] = base_currency
    whitelist = earthzetaorg.pairlists._gen_pair_whitelist(base_currency=base_currency, key=key)
    assert whitelist == whitelist_result


def test_gen_pair_whitelist_not_supported(mocker, default_conf, tickers) -> None:
    default_conf['pairlist'] = {'method': 'VolumePairList',
                                'config': {'number_assets': 10}
                                }
    mocker.patch('earthzetaorg.exchange.Exchange.get_tickers', tickers)
    mocker.patch('earthzetaorg.exchange.Exchange.exchange_has', MagicMock(return_value=False))

    with pytest.raises(OperationalException):
        get_patched_earthzetaorgbot(mocker, default_conf)


@pytest.mark.parametrize("pairlist", AVAILABLE_PAIRLISTS)
def test_pairlist_class(mocker, whitelist_conf, markets, pairlist):
    whitelist_conf['pairlist']['method'] = pairlist
    mocker.patch('earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets))
    mocker.patch('earthzetaorg.exchange.Exchange.exchange_has', MagicMock(return_value=True))
    earthzetaorg = get_patched_earthzetaorgbot(mocker, whitelist_conf)

    assert earthzetaorg.pairlists.name == pairlist
    assert pairlist in earthzetaorg.pairlists.short_desc()
    assert isinstance(earthzetaorg.pairlists.whitelist, list)
    assert isinstance(earthzetaorg.pairlists.blacklist, list)


@pytest.mark.parametrize("pairlist", AVAILABLE_PAIRLISTS)
@pytest.mark.parametrize("whitelist,log_message", [
    (['ETH/BTC', 'TKN/BTC'], ""),
    (['ETH/BTC', 'TKN/BTC', 'TRX/ETH'], "is not compatible with exchange"),  # TRX/ETH wrong stake
    (['ETH/BTC', 'TKN/BTC', 'BCH/BTC'], "is not compatible with exchange"),  # BCH/BTC not available
    (['ETH/BTC', 'TKN/BTC', 'BLK/BTC'], "is not compatible with exchange"),  # BLK/BTC in blacklist
    (['ETH/BTC', 'TKN/BTC', 'LTC/BTC'], "Market is not active")  # LTC/BTC is inactive
])
def test_validate_whitelist(mocker, whitelist_conf, markets, pairlist, whitelist, caplog,
                            log_message):
    whitelist_conf['pairlist']['method'] = pairlist
    mocker.patch('earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets))
    mocker.patch('earthzetaorg.exchange.Exchange.exchange_has', MagicMock(return_value=True))
    earthzetaorg = get_patched_earthzetaorgbot(mocker, whitelist_conf)
    caplog.clear()

    new_whitelist = earthzetaorg.pairlists._validate_whitelist(whitelist)

    assert set(new_whitelist) == set(['ETH/BTC', 'TKN/BTC'])
    assert log_message in caplog.text
