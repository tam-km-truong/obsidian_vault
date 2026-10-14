---
category: knowledge
tags:
  - python
  - concurrency
  - memory
  - backpressure
  - hpc
source_raw: "[[Backpressure control]]"
status: processed
---

# Backpressure, Concurrency & Memory Management in Python

## 1. What is Backpressure?
Backpressure means throttling producer tasks when downstream consumer queues cannot keep up, preventing out-of-memory (OOM) fatal crashes during high-throughput file processing.

---

## 2. Production Bounded Queue Architecture
```python
import concurrent.futures
import threading

class BoundedExecutor:
    def __init__(self, max_workers=8, max_queue=20):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = threading.BoundedSemaphore(max_queue + max_workers)

    def submit(self, fn, *args, **kwargs):
        self.semaphore.acquire()
        future = self.executor.submit(fn, *args, **kwargs)
        future.add_done_callback(lambda f: self.semaphore.release())
        return future
```

## Related Notes
- [[Data Pipeline - Argmin Grouping on Large TSV]] – File descriptor pooling
- [[CLI - xargs & Parallel Processing]] – Process-level concurrency
