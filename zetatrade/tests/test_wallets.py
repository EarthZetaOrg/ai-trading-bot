# pragma pylint: disable=missing-docstring
from earthzetaorg.tests.conftest import get_patched_earthzetaorgbot
from unittest.mock import MagicMock


def test_sync_wallet_at_boot(mocker, default_conf):
    default_conf['dry_run'] = False
    mocker.patch.multiple(
        'earthzetaorg.exchange.Exchange',
        get_balances=MagicMock(return_value={
            "BNT": {
                "free": 1.0,
                "used": 2.0,
                "total": 3.0
            },
            "GAS": {
                "free": 0.260739,
                "used": 0.0,
                "total": 0.260739
            },
        })
    )

    earthzetaorg = get_patched_earthzetaorgbot(mocker, default_conf)

    assert len(earthzetaorg.wallets._wallets) == 2
    assert earthzetaorg.wallets._wallets['BNT'].free == 1.0
    assert earthzetaorg.wallets._wallets['BNT'].used == 2.0
    assert earthzetaorg.wallets._wallets['BNT'].total == 3.0
    assert earthzetaorg.wallets._wallets['GAS'].free == 0.260739
    assert earthzetaorg.wallets._wallets['GAS'].used == 0.0
    assert earthzetaorg.wallets._wallets['GAS'].total == 0.260739
    assert earthzetaorg.wallets.get_free('BNT') == 1.0

    mocker.patch.multiple(
        'earthzetaorg.exchange.Exchange',
        get_balances=MagicMock(return_value={
            "BNT": {
                "free": 1.2,
                "used": 1.9,
                "total": 3.5
            },
            "GAS": {
                "free": 0.270739,
                "used": 0.1,
                "total": 0.260439
            },
        })
    )

    earthzetaorg.wallets.update()

    assert len(earthzetaorg.wallets._wallets) == 2
    assert earthzetaorg.wallets._wallets['BNT'].free == 1.2
    assert earthzetaorg.wallets._wallets['BNT'].used == 1.9
    assert earthzetaorg.wallets._wallets['BNT'].total == 3.5
    assert earthzetaorg.wallets._wallets['GAS'].free == 0.270739
    assert earthzetaorg.wallets._wallets['GAS'].used == 0.1
    assert earthzetaorg.wallets._wallets['GAS'].total == 0.260439
    assert earthzetaorg.wallets.get_free('GAS') == 0.270739
    assert earthzetaorg.wallets.get_used('GAS') == 0.1
    assert earthzetaorg.wallets.get_total('GAS') == 0.260439


def test_sync_wallet_missing_data(mocker, default_conf):
    default_conf['dry_run'] = False
    mocker.patch.multiple(
        'earthzetaorg.exchange.Exchange',
        get_balances=MagicMock(return_value={
            "BNT": {
                "free": 1.0,
                "used": 2.0,
                "total": 3.0
            },
            "GAS": {
                "free": 0.260739,
                "total": 0.260739
            },
        })
    )

    earthzetaorg = get_patched_earthzetaorgbot(mocker, default_conf)

    assert len(earthzetaorg.wallets._wallets) == 2
    assert earthzetaorg.wallets._wallets['BNT'].free == 1.0
    assert earthzetaorg.wallets._wallets['BNT'].used == 2.0
    assert earthzetaorg.wallets._wallets['BNT'].total == 3.0
    assert earthzetaorg.wallets._wallets['GAS'].free == 0.260739
    assert earthzetaorg.wallets._wallets['GAS'].used is None
    assert earthzetaorg.wallets._wallets['GAS'].total == 0.260739
    assert earthzetaorg.wallets.get_free('GAS') == 0.260739
