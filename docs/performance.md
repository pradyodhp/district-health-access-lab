# Local performance and Monte Carlo summary check

Measured on the audit workspace, Python 3.10, seed 42, training status-quo triangular inputs. Timings include tracemalloc overhead; not a Render SLA or API load result.

| Draws | Seconds | Peak traced bytes | Screened p50 |
| --- | --- | --- | --- |
| 1000 | 0.0186 | 253558 | 384.016 |
| 5000 | 0.0931 | 1198847 | 384.532 |
| 10000 | 0.2082 | 2399608 | 384.133 |
| 25000 | 0.5605 | 6037440 | 385.618 |
| 100000 | 2.2361 | 23609848 | 385.102 |

Median shifts are below 2 synthetic people between adjacent tested sizes. This is a limited one-seed summary check, not a formal convergence test or validation of the healthcare model. API/browser latency and multiuser load remain unbenchmarked. Rerun `python3 scripts/benchmark.py`; machine timing is not deterministic.
