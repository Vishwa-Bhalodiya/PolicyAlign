import time
import threading

class RateLimiter:
    def __init__(self, min_interval_seconds: float = 1.0):
        self.min_interval = min_interval_seconds
        self.lock = threading.Lock()
        self.last_call_time = 0

    def wait(self):
        with self.lock:
            elapsed = time.time() - self.last_call_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_call_time = time.time()

rate_limiter = RateLimiter()