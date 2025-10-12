"""Terminal spinner utilities."""

from __future__ import annotations

import sys
import threading
import time
from contextlib import contextmanager
from typing import Iterator

FRAMES = "|/-\\"


def _spinner(stop_event: threading.Event, message: str) -> None:
    idx = 0
    while not stop_event.is_set():
        frame = FRAMES[idx % len(FRAMES)]
        sys.stdout.write(f"\r{message} {frame}")
        sys.stdout.flush()
        time.sleep(0.1)
        idx += 1
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
    sys.stdout.flush()


@contextmanager
def spinner(message: str) -> Iterator[None]:
    stop_event = threading.Event()
    thread = threading.Thread(target=_spinner, args=(stop_event, message), daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop_event.set()
        thread.join()
