from __future__ import annotations

import math
import os
import weakref
from logging import getLogger
from os import environ
from threading import Event, Thread
from time import time_ns

from .exceptions import OpAMPTimeoutError
from .environment_variables import OPAMP_AGENT_INTERVAL, OPAMP_AGENT_TIMEOUT
from .transport.http import HttpTransport
from .transport.requests import RequestsTransport

_logger = getLogger(__name__)

_DEFAULT_OPAMP_TIMEOUT_MS = 5_000


class OpAMPClient:
    # TODO: need to support basic auth too
    def __init__(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
        timeout_millis: int = _DEFAULT_OPAMP_TIMEOUT_MS,
        transport: HttpTransport | None = None,
    ):
        self._timeout_millis = timeout_millis
        self._transport = transport if transport is not None else RequestsTransport

        self._endpoint = endpoint
        # TODO: add a proper user agent
        self._headers = headers or {}

    def _status_message():
        pass

    def _poll_message():
        pass

    def poll(self, data):
        # TODO: sort out where to add the logic of deciding what message to send
        return self._transport.send(
            url=self._endpoint, headers=self._headers, data=data, timeout_millis=self._timeout_millis
        )


class OpAMPAgent:
    def __init__(self):
        try:
            interval_millis = float(environ.get(OPAMP_AGENT_INTERVAL, 30000))
        except ValueError:
            _logger.warning("Found invalid value for export interval, using default")
            interval_millis = 30000
        try:
            timeout_millis = float(environ.get(OPAMP_AGENT_TIMEOUT, 5000))
        except ValueError:
            _logger.warning("Found invalid value for export timeout, using default")
            timeout_millis = 5000

        # TODO: env for auth

        self._interval_millis = interval_millis
        self._timeout_millis = timeout_millis

        self._shutdown = False
        self._shutdown_event = Event()

        self._daemon_thread = None

        if self._interval_millis > 0 and self._interval_millis < math.inf:
            self._daemon_thread = self._create_thread()
            self._daemon_thread.start()
            if hasattr(os, "register_at_fork"):
                weak_at_fork = weakref.WeakMethod(self._at_fork_reinit)

                os.register_at_fork(
                    after_in_child=lambda: weak_at_fork()()  # pylint: disable=unnecessary-lambda
                )
        elif self._interval_millis <= 0:
            raise ValueError(
                f"interval value {self._interval_millis} is invalid \
                and needs to be larger than zero."
            )

    def _create_thread(self):
        return Thread(
            name="OpAMPAgent",
            target=self._worker,
            daemon=True,
        )

    def _at_fork_reinit(self):
        self._daemon_thread = self._create_thread()
        self._daemon_thread.start()

    def _worker(self) -> None:
        client = OpAMPClient(timeout_millis=self._timeout_millis)
        interval_secs = self._interval_millis / 1e3

        while not self._shutdown_event.wait(interval_secs):
            # TODO: here we should block on a queue
            try:
                client.poll()
            except OpAMPTimeoutError:
                _logger.warning(
                    "OpAMP send status timed out. Will try again after %s seconds",
                    interval_secs,
                    exc_info=True,
                )

    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        deadline_ns = time_ns() + timeout_millis * 10**6

        self._shutdown = True
        self._shutdown_event.set()
        if self._daemon_thread:
            self._daemon_thread.join(timeout=(deadline_ns - time_ns()) / 10**9)
