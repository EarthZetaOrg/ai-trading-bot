"""
Main earthzetaorg worker class.
"""
import logging
import time
import traceback
from argparse import Namespace
from typing import Any, Callable, Optional
import sdnotify

from earthzetaorg import (constants, OperationalException, TemporaryError,
                       __version__)
from earthzetaorg.configuration import Configuration
from earthzetaorg.earthzetaorgbot import earthzetaorgBot
from earthzetaorg.state import State
from earthzetaorg.rpc import RPCMessageType


logger = logging.getLogger(__name__)


class Worker(object):
    """
    earthzetaorgbot worker class
    """

    def __init__(self, args: Namespace, config=None) -> None:
        """
        Init all variables and objects the bot needs to work
        """
        logger.info('Starting worker %s', __version__)

        self._args = args
        self._config = config
        self._init(False)

        # Tell systemd that we completed initialization phase
        if self._sd_notify:
            logger.debug("sd_notify: READY=1")
            self._sd_notify.notify("READY=1")

    def _init(self, reconfig: bool) -> None:
        """
        Also called from the _reconfigure() method (with reconfig=True).
        """
        if reconfig or self._config is None:
            # Load configuration
            self._config = Configuration(self._args, None).get_config()

        # Init the instance of the bot
        self.earthzetaorg = earthzetaorgBot(self._config)

        self._throttle_secs = self._config.get('internals', {}).get(
            'process_throttle_secs',
            constants.PROCESS_THROTTLE_SECS
        )

        self._sd_notify = sdnotify.SystemdNotifier() if \
            self._config.get('internals', {}).get('sd_notify', False) else None

    @property
    def state(self) -> State:
        return self.earthzetaorg.state

    @state.setter
    def state(self, value: State) -> None:
        self.earthzetaorg.state = value

    def run(self) -> None:
        state = None
        while True:
            state = self._worker(old_state=state)
            if state == State.RELOAD_CONF:
                self._reconfigure()

    def _worker(self, old_state: Optional[State], throttle_secs: Optional[float] = None) -> State:
        """
        Trading routine that must be run at each loop
        :param old_state: the previous service state from the previous call
        :return: current service state
        """
        state = self.earthzetaorg.state
        if throttle_secs is None:
            throttle_secs = self._throttle_secs

        # Log state transition
        if state != old_state:
            self.earthzetaorg.rpc.send_msg({
                'type': RPCMessageType.STATUS_NOTIFICATION,
                'status': f'{state.name.lower()}'
            })
            logger.info('Changing state to: %s', state.name)
            if state == State.RUNNING:
                self.earthzetaorg.startup()

        if state == State.STOPPED:
            # Ping systemd watchdog before sleeping in the stopped state
            if self._sd_notify:
                logger.debug("sd_notify: WATCHDOG=1\\nSTATUS=State: STOPPED.")
                self._sd_notify.notify("WATCHDOG=1\nSTATUS=State: STOPPED.")

            time.sleep(throttle_secs)

        elif state == State.RUNNING:
            # Ping systemd watchdog before throttling
            if self._sd_notify:
                logger.debug("sd_notify: WATCHDOG=1\\nSTATUS=State: RUNNING.")
                self._sd_notify.notify("WATCHDOG=1\nSTATUS=State: RUNNING.")

            self._throttle(func=self._process, min_secs=throttle_secs)

        return state

    def _throttle(self, func: Callable[..., Any], min_secs: float, *args, **kwargs) -> Any:
        """
        Throttles the given callable that it
        takes at least `min_secs` to finish execution.
        :param func: Any callable
        :param min_secs: minimum execution time in seconds
        :return: Any
        """
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = max(min_secs - (end - start), 0.0)
        logger.debug('Throttling %s for %.2f seconds', func.__name__, duration)
        time.sleep(duration)
        return result

    def _process(self) -> None:
        logger.debug("========================================")
        try:
            self.earthzetaorg.process()
        except TemporaryError as error:
            logger.warning(f"Error: {error}, retrying in {constants.RETRY_TIMEOUT} seconds...")
            time.sleep(constants.RETRY_TIMEOUT)
        except OperationalException:
            tb = traceback.format_exc()
            hint = 'Issue `/start` if you think it is safe to restart.'
            self.earthzetaorg.rpc.send_msg({
                'type': RPCMessageType.STATUS_NOTIFICATION,
                'status': f'OperationalException:\n```\n{tb}```{hint}'
            })
            logger.exception('OperationalException. Stopping trader ...')
            self.earthzetaorg.state = State.STOPPED

    def _reconfigure(self) -> None:
        """
        Cleans up current earthzetaorgbot instance, reloads the configuration and
        replaces it with the new instance
        """
        # Tell systemd that we initiated reconfiguration
        if self._sd_notify:
            logger.debug("sd_notify: RELOADING=1")
            self._sd_notify.notify("RELOADING=1")

        # Clean up current earthzetaorg modules
        self.earthzetaorg.cleanup()

        # Load and validate config and create new instance of the bot
        self._init(True)

        self.earthzetaorg.rpc.send_msg({
            'type': RPCMessageType.STATUS_NOTIFICATION,
            'status': 'config reloaded'
        })

        # Tell systemd that we completed reconfiguration
        if self._sd_notify:
            logger.debug("sd_notify: READY=1")
            self._sd_notify.notify("READY=1")

    def exit(self) -> None:
        # Tell systemd that we are exiting now
        if self._sd_notify:
            logger.debug("sd_notify: STOPPING=1")
            self._sd_notify.notify("STOPPING=1")

        if self.earthzetaorg:
            self.earthzetaorg.rpc.send_msg({
                'type': RPCMessageType.STATUS_NOTIFICATION,
                'status': 'process died'
            })
            self.earthzetaorg.cleanup()
