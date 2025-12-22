from __future__ import annotations

import queue
import threading
import traceback

from typing import Callable, cast

from ._guidance import logger


class Runner:
    __jobs: queue.SimpleQueue[dict]
    __results: queue.SimpleQueue[dict]
    __thread: threading.Thread

    def __init__(self) -> None:
        self.__jobs = queue.SimpleQueue[dict]()
        self.__results = queue.SimpleQueue[dict]()
        self.__thread = threading.Thread(target = self.__thread_proc)
        self.__thread.start()

    @property
    def thread(self) -> threading.Thread:
        return self.__thread

    def stop(self) -> None:
        self.__jobs.put({ 'quit': True })
        self.__thread.join()

    def run_job(self, job: Callable[[dict], dict], /, **kwargs) -> None:
        self.__jobs.put({ 'job': job } | kwargs)

    def poll_result(self) -> dict | None:
        if self.__results.empty():
            return None
        return self.__results.get_nowait()

    def add_result(self, d: dict) -> None:
        self.__results.put(d)

    def __thread_proc(self) -> None:
        while True:
            try:
                job = self.__jobs.get()
                if 'quit' in job:
                    return
                if 'job' in job:
                    callable = cast(Callable[[dict], dict], job['job'])
                    del job['job']
                    self.__results.put(callable(job))
            except BaseException as exc:
                exc_str = traceback.format_exc()
                logger.error('an exception has been thrown in the runner')
                logger.error(exc_str)
                self.__results.put({ 'error': exc, 'message': exc_str })
