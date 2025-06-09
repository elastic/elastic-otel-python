from __future__ import annotations

import threading
import queue
import logging
from typing import Any, Callable

from elasticotel.opamp.client import OpAMPClient

logger = logging.getLogger(__name__)


class Job:
    """
    Represents a single request job, with retry/backoff metadata.
    """

    def __init__(
        self,
        payload: Any,
        max_retries: int = 1,
        initial_backoff: float = 1.0,
        callback: Callable[None, None] | None = None,
    ):
        self.payload = payload
        self.attempt = 0
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.callback = callback


class OpAMPAgent:
    """
    OpAMPAgent handles:
      - periodic “heartbeat” calls enqueued at a fixed interval
      - on-demand calls via send_on_demand()
      - exponential backoff retry on failures
      - immediate cancellation of all jobs on shutdown
    """

    def __init__(
        self,
        *,
        endpoint: str,
        interval: float,
        handler: Callable[[Any], None],
        max_retries: int = 1,
        initial_backoff: float = 1.0,
    ):
        """
        :param endpoint: the opamp endpoint
        :param interval: seconds between automatic calls
        :param handler: function(payload) that performs the remote request
        :param max_retries: how many times to retry a failed job
        :param initial_backoff: base seconds for exponential backoff
        """
        self.interval = interval
        self.handler = handler
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff

        self._queue: queue.Queue[Job] = queue.Queue()
        self._stop = threading.Event()

        self._worker = threading.Thread(name="OpAMPAgentWorker", target=self._run_worker, daemon=True)
        self._scheduler = threading.Thread(name="OpAMPAgentScheduler", target=self._run_scheduler, daemon=True)
        # start scheduling only after connection with server has been established
        self._schedule = False

        self._client = OpAMPClient(endpoint=endpoint)

    def _enable_scheduler(self):
        self._schedule = True

    def start(self) -> None:
        """
        Starts the scheduler and worker threads.
        """
        self._stop.clear()
        self._worker.start()
        self._scheduler.start()

        # enqueue the connection message so we can then enable heartbeat
        payload = self._client._build_connection_message()
        self.send(payload, max_retries=10, callback=self._enable_scheduler)

    def send(self, payload: Any, max_retries: int | None = None, callback: Callable[None, None] | None = None) -> None:
        """
        Enqueue an on-demand request.
        """
        if max_retries is None:
            max_retries = self.max_retries
        job = Job(payload, max_retries=max_retries, initial_backoff=self.initial_backoff, callback=callback)
        self._queue.put(job)
        logger.debug("On-demand job enqueued: %r", payload)

    def _run_scheduler(self) -> None:
        """
        Periodically enqueue “heartbeat” jobs until stop is signaled.
        """
        while not self._stop.wait(self.interval):
            if self._schedule:
                payload = self._client._build_heartbeat_message()
                job = Job(payload=payload, max_retries=self.max_retries, initial_backoff=self.initial_backoff)
                self._queue.put(job)
                logger.debug("Periodic job enqueued")

    def _run_worker(self) -> None:
        """
        Worker loop: pull jobs, attempt the handler, retry on failure with backoff.
        """
        while not self._stop.is_set():
            try:
                job: Job = self._queue.get(timeout=1)
            except queue.Empty:
                continue

            while job.attempt <= job.max_retries and not self._stop.is_set():
                try:
                    response = self.client._send(job.payload)
                    self.handler(self.client, response)
                    logger.info("Job succeeded: %r", job.payload)
                    break
                except Exception as exc:
                    job.attempt += 1
                    logger.warning("Job %r failed attempt %d/%d: %s", job.payload, job.attempt, job.max_retries, exc)

                    if job.attempt > job.max_retries:
                        logger.error("Job %r dropped after max retries", job.payload)
                        break

                    # exponential backoff, interruptible by stop event
                    delay = job.initial_backoff * (2 ** (job.attempt - 1))
                    logger.debug("Retrying in %.1fs", delay)
                    if self._stop.wait(delay):
                        # stop requested during backoff: abandon job
                        logger.debug("Stop signaled, abandoning job %r", job.payload)
                        break

            try:
                if job.callback is not None:
                    job.callback()
            except Exception as exc:
                logging.warning("Callback for job failed: %s", exc)
            finally:
                self._queue.task_done()

    def stop(self) -> None:
        """
        Immediately cancel all in-flight and queued jobs, then join threads.
        """
        logger.debug("Stopping OpAMPClient: cancelling jobs")
        # Clear pending jobs
        while True:
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break

        # Signal threads to exit
        self._stop.set()
        self._worker.join()
        self._scheduler.join()
        logger.debug("OpAMPClient stopped")
