import re
from unittest.mock import MagicMock, PropertyMock

import pytest

from earthzetaorg.state import RunMode
from earthzetaorg.tests.conftest import get_args, log_has, patch_exchange
from earthzetaorg.utils import (setup_utils_configuration, start_create_userdir,
                             start_download_data, start_list_exchanges)


def test_setup_utils_configuration():
    args = [
        '--config', 'config.json.example',
    ]

    config = setup_utils_configuration(get_args(args), RunMode.OTHER)
    assert "exchange" in config
    assert config['exchange']['dry_run'] is True
    assert config['exchange']['key'] == ''
    assert config['exchange']['secret'] == ''


def test_list_exchanges(capsys):

    args = [
        "list-exchanges",
    ]

    start_list_exchanges(get_args(args))
    captured = capsys.readouterr()
    assert re.match(r"Exchanges supported by ccxt and available.*", captured.out)
    assert re.match(r".*binance,.*", captured.out)
    assert re.match(r".*bittrex,.*", captured.out)

    # Test with --one-column
    args = [
        "list-exchanges",
        "--one-column",
    ]

    start_list_exchanges(get_args(args))
    captured = capsys.readouterr()
    assert not re.match(r"Exchanges supported by ccxt and available.*", captured.out)
    assert re.search(r"^binance$", captured.out, re.MULTILINE)
    assert re.search(r"^bittrex$", captured.out, re.MULTILINE)


def test_create_datadir_failed(caplog):

    args = [
        "create-userdir",
    ]
    with pytest.raises(SystemExit):
        start_create_userdir(get_args(args))
    assert log_has("`create-userdir` requires --userdir to be set.", caplog)


def test_create_datadir(caplog, mocker):
    cud = mocker.patch("earthzetaorg.utils.create_userdata_dir", MagicMock())
    args = [
        "create-userdir",
        "--userdir",
        "/temp/earthzetaorg/test"
    ]
    start_create_userdir(get_args(args))

    assert cud.call_count == 1
    assert len(caplog.record_tuples) == 0


def test_download_data_keyboardInterrupt(mocker, caplog, markets):
    dl_mock = mocker.patch('earthzetaorg.utils.refresh_backtest_ohlcv_data',
                           MagicMock(side_effect=KeyboardInterrupt))
    patch_exchange(mocker)
    mocker.patch(
        'earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value=markets)
    )
    args = [
        "download-data",
        "--exchange", "binance",
        "--pairs", "ETH/BTC", "XRP/BTC",
    ]
    with pytest.raises(SystemExit):
        start_download_data(get_args(args))

    assert dl_mock.call_count == 1


def test_download_data_no_markets(mocker, caplog):
    dl_mock = mocker.patch('earthzetaorg.utils.refresh_backtest_ohlcv_data',
                           MagicMock(return_value=["ETH/BTC", "XRP/BTC"]))
    patch_exchange(mocker)
    mocker.patch(
        'earthzetaorg.exchange.Exchange.markets', PropertyMock(return_value={})
    )
    args = [
        "download-data",
        "--exchange", "binance",
        "--pairs", "ETH/BTC", "XRP/BTC",
        "--days", "20"
    ]
    start_download_data(get_args(args))
    assert dl_mock.call_args[1]['timerange'].starttype == "date"
    assert log_has("Pairs [ETH/BTC,XRP/BTC] not available on exchange binance.", caplog)
