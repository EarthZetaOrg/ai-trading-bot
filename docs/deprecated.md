# Deprecated features

This page contains description of the command line arguments, configuration parameters
and the bot features that were declared as DEPRECATED by the bot development team
and are no longer supported. Please avoid their usage in your configuration.

## Deprecated

### the `--refresh-pairs-cached` command line option

`--refresh-pairs-cached` in the context of backtesting, hyperopt and edge allows to refresh candle data for backtesting.
Since this leads to much confusion, and slows down backtesting (while not being part of backtesting) this has been singled out 
as a seperate earthzetaorg subcommand `earthzetaorg download-data`.

This command line option was deprecated in `2019.7-dev` and will be removed after the next release.

## Removed features

### The **--dynamic-whitelist** command line option

This command line option was deprecated in 2018 and removed earthzetaorg 2019.6-dev (develop branch)
and in earthzetaorg 2019.7 (master branch).

### the `--live` command line option

`--live` in the context of backtesting allowed to download the latest tick data for backtesting.
Did only download the latest 500 candles, so was ineffective in getting good backtest data.
Removed in 2019-7-dev (develop branch) and in earthzetaorg 2019-8 (master branch)
