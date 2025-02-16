# pragma pylint: disable=missing-docstring, C0103, C0330
# pragma pylint: disable=protected-access, too-many-lines, invalid-name, too-many-arguments

from unittest.mock import MagicMock

import pytest

from earthzetaorg.edge import PairInfo
from earthzetaorg.optimize import setup_configuration, start_edge
from earthzetaorg.optimize.edge_cli import EdgeCli
from earthzetaorg.state import RunMode
from earthzetaorg.tests.conftest import (get_args, log_has, log_has_re,
                                      patch_exchange,
                                      patched_configuration_load_config_file)


def test_setup_configuration_without_arguments(mocker, default_conf, caplog) -> None:
    patched_configuration_load_config_file(mocker, default_conf)

    args = [
        '--config', 'config.json',
        '--strategy', 'DefaultStrategy',
        'edge'
    ]

    config = setup_configuration(get_args(args), RunMode.EDGE)
    assert config['runmode'] == RunMode.EDGE

    assert 'max_open_trades' in config
    assert 'stake_currency' in config
    assert 'stake_amount' in config
    assert 'exchange' in config
    assert 'pair_whitelist' in config['exchange']
    assert 'datadir' in config
    assert log_has('Using data directory: {} ...'.format(config['datadir']), caplog)
    assert 'ticker_interval' in config
    assert not log_has_re('Parameter -i/--ticker-interval detected .*', caplog)

    assert 'refresh_pairs' not in config
    assert not log_has('Parameter -r/--refresh-pairs-cached detected ...', caplog)

    assert 'timerange' not in config
    assert 'stoploss_range' not in config


@pytest.mark.filterwarnings("ignore:DEPRECATED")
def test_setup_edge_configuration_with_arguments(mocker, edge_conf, caplog) -> None:
    patched_configuration_load_config_file(mocker, edge_conf)
    mocker.patch(
        'earthzetaorg.configuration.configuration.create_datadir',
        lambda c, x: x
    )

    args = [
        '--config', 'config.json',
        '--strategy', 'DefaultStrategy',
        '--datadir', '/foo/bar',
        'edge',
        '--ticker-interval', '1m',
        '--refresh-pairs-cached',
        '--timerange', ':100',
        '--stoplosses=-0.01,-0.10,-0.001'
    ]

    config = setup_configuration(get_args(args), RunMode.EDGE)
    assert 'max_open_trades' in config
    assert 'stake_currency' in config
    assert 'stake_amount' in config
    assert 'exchange' in config
    assert 'pair_whitelist' in config['exchange']
    assert 'datadir' in config
    assert config['runmode'] == RunMode.EDGE
    assert log_has('Using data directory: {} ...'.format(config['datadir']), caplog)
    assert 'ticker_interval' in config
    assert log_has('Parameter -i/--ticker-interval detected ... Using ticker_interval: 1m ...',
                   caplog)

    assert 'refresh_pairs' in config
    assert log_has('Parameter -r/--refresh-pairs-cached detected ...', caplog)
    assert 'timerange' in config
    assert log_has('Parameter --timerange detected: {} ...'.format(config['timerange']), caplog)


def test_start(mocker, fee, edge_conf, caplog) -> None:
    start_mock = MagicMock()
    mocker.patch('earthzetaorg.exchange.Exchange.get_fee', fee)
    patch_exchange(mocker)
    mocker.patch('earthzetaorg.optimize.edge_cli.EdgeCli.start', start_mock)
    patched_configuration_load_config_file(mocker, edge_conf)

    args = [
        '--config', 'config.json',
        '--strategy', 'DefaultStrategy',
        'edge'
    ]
    args = get_args(args)
    start_edge(args)
    assert log_has('Starting earthzetaorg in Edge mode', caplog)
    assert start_mock.call_count == 1


def test_edge_init(mocker, edge_conf) -> None:
    patch_exchange(mocker)
    edge_conf['stake_amount'] = 20
    edge_cli = EdgeCli(edge_conf)
    assert edge_cli.config == edge_conf
    assert edge_cli.config['stake_amount'] == 'unlimited'
    assert callable(edge_cli.edge.calculate)


def test_generate_edge_table(edge_conf, mocker):
    patch_exchange(mocker)
    edge_cli = EdgeCli(edge_conf)

    results = {}
    results['ETH/BTC'] = PairInfo(-0.01, 0.60, 2, 1, 3, 10, 60)

    assert edge_cli._generate_edge_table(results).count(':|') == 7
    assert edge_cli._generate_edge_table(results).count('| ETH/BTC |') == 1
    assert edge_cli._generate_edge_table(results).count(
        '|   risk reward ratio |   required risk reward |   expectancy |') == 1
