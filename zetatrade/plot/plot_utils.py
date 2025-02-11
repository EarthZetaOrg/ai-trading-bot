from argparse import Namespace
from earthzetaorg import OperationalException
from earthzetaorg.state import RunMode
from earthzetaorg.utils import setup_utils_configuration


def validate_plot_args(args: Namespace):
    args_tmp = vars(args)
    if not args_tmp.get('datadir') and not args_tmp.get('config'):
        raise OperationalException(
            "You need to specify either `--datadir` or `--config` "
            "for plot-profit and plot-dataframe.")


def start_plot_dataframe(args: Namespace) -> None:
    """
    Entrypoint for dataframe plotting
    """
    # Import here to avoid errors if plot-dependencies are not installed.
    from earthzetaorg.plot.plotting import analyse_and_plot_pairs
    validate_plot_args(args)
    config = setup_utils_configuration(args, RunMode.PLOT)

    analyse_and_plot_pairs(config)


def start_plot_profit(args: Namespace) -> None:
    """
    Entrypoint for plot_profit
    """
    # Import here to avoid errors if plot-dependencies are not installed.
    from earthzetaorg.plot.plotting import plot_profit
    validate_plot_args(args)
    config = setup_utils_configuration(args, RunMode.PLOT)

    plot_profit(config)
