from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from .collector import collect_holder_snapshot
from .compute import compute_metric
from .config import REFRESH_SECONDS
from .storage import Storage


@dataclass
class Tracker:
    ca: str
    stop_event: threading.Event = field(default_factory=threading.Event)
    thread: threading.Thread | None = None


class Runtime:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self._lock = threading.Lock()
        self._trackers: dict[str, Tracker] = {}

    def list_tracking(self) -> list[str]:
        with self._lock:
            return list(self._trackers.keys())

    def start_tracking(self, ca: str) -> bool:
        with self._lock:
            if ca in self._trackers:
                return False
            tracker = Tracker(ca=ca)
            t = threading.Thread(target=self._run_loop, args=(tracker,), daemon=True)
            tracker.thread = t
            self._trackers[ca] = tracker
            t.start()
            return True

    def stop_tracking(self, ca: str) -> bool:
        with self._lock:
            tracker = self._trackers.get(ca)
            if not tracker:
                return False
            tracker.stop_event.set()
            return True

    def _run_loop(self, tracker: Tracker) -> None:
        ca = tracker.ca
        while not tracker.stop_event.is_set():
            start = time.time()
            ts = int(start)
            try:
                balances, holder_count = collect_holder_snapshot(ca)
                metric, top50, trimmed = compute_metric(ca, ts, balances, holder_count)
                metric.sample_ok = 1
                metric.err_msg = None
                self.storage.insert_metric(metric, top50, trimmed)
                latency_ms = int((time.time() - start) * 1000)
                self.storage.insert_job_log(ts=ts, ca=ca, status="ok", latency_ms=latency_ms)
            except Exception as e:
                err = str(e)
                metric, top50, trimmed = compute_metric(ca, ts, [], 0)
                metric.sample_ok = 0
                metric.err_msg = err
                self.storage.insert_metric(metric, top50, trimmed)
                self.storage.insert_job_log(ts=ts, ca=ca, status="error", err_msg=err)
            tracker.stop_event.wait(REFRESH_SECONDS)

        with self._lock:
            self._trackers.pop(ca, None)
