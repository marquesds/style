# Concurrency

Pick the model from the workload, not from fashion. Threads, processes, and
asyncio solve different bottlenecks; the GIL decides which one helps.

## GIL Reality

CPython runs **one thread of Python bytecode at a time**. Threads still help
for I/O because blocking syscalls (sockets, files, `time.sleep`) and most
C-extension calls (NumPy, hashlib, DB drivers) **release the GIL** while they
wait or crunch. Pure-Python CPU work in threads buys nothing — it adds
context-switch overhead to a serialized computation.

## Decision Table

| Workload | Model |
|---|---|
| I/O-bound, tens of connections | threads via `ThreadPoolExecutor` |
| I/O-bound, thousands of connections | asyncio |
| CPU-bound | `ProcessPoolExecutor` or a native extension that releases the GIL |
| Mixed | asyncio shell + `to_thread` / process pool for the blocking parts |

Never guess the bottleneck — profile first. "It's slow, add threads" without a
profile routinely makes CPU-bound code slower.

## `concurrent.futures` First

Reach for executors before raw `threading.Thread` / `multiprocessing.Process`.
Same API for both pools; swap one class to change model. Futures are handles
the executor fills in — you never call them, you await their results via
`executor.map` (ordered) or `submit` + `as_completed` (completion order).

```python
def fetch_all(urls: list[str]) -> list[bytes]:
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(fetch, urls))
```

```python
def first_results(urls):
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(fetch, u) for u in urls]
        for fut in as_completed(futures):
            yield fut.result()
```

## Threads

- Daemon threads die abruptly when the main thread exits — no cleanup runs.
  Use them only for dispensable background work; non-daemon for anything that
  must finish or release resources.
- Coordinate with `threading.Event` and `queue.Queue`, not shared boolean
  flags or ad-hoc lock dances. A queue hands off ownership of data; a flag
  shares mutable state. Locking discipline and shared-state hazards →
  skill:concurrency-correctness.

## Processes

`ProcessPoolExecutor` sidesteps the GIL: one interpreter per core. Costs:
arguments and return values must **pickle** (no lambdas, open sockets, or
locks across the boundary), and each task pays serialization + process
overhead — batch small tasks. Start methods differ: `spawn` (default on
macOS/Windows; Linux default is `forkserver` since 3.14) imports the module
fresh in each child — guard entry with `if __name__ == "__main__":`; `fork`
is fast but copies locks and threads in unsafe states.

## asyncio

- `async def` defines a coroutine; calling it does **nothing** until awaited
  or wrapped in a task. A never-awaited coroutine is a silent no-op (warning
  at GC time, if you're lucky).
- The event loop is single-threaded cooperative multitasking: **one blocking
  call stalls every task**. No `time.sleep`, no `requests`, no heavy CPU in a
  coroutine. Push blocking work out with `asyncio.to_thread(fn, ...)` (or
  `loop.run_in_executor` with a process pool for CPU work).
- Fan out with `asyncio.gather(*coros)` or, on 3.11+, `asyncio.TaskGroup`
  (structured: failures cancel siblings instead of leaking tasks).
- Call `asyncio.run(main())` exactly once at the top of the program — not
  per request, not inside a running loop.
- Async is contagious: a coroutine's callers must be async too. Keep the
  sync↔async boundary in one place (the shell); don't sprinkle
  `asyncio.run` through library code.

```python
async def fetch_many(urls, limit=10):
    sem = asyncio.Semaphore(limit)

    async def one(url):
        async with sem:
            return await fetch(url)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(one(u)) for u in urls]
    return [t.result() for t in tasks]
```

`Semaphore` is the backpressure knob: unbounded `gather` over 10k URLs opens
10k sockets at once.

## Queues Connect Producers and Consumers

All three models share the same shape: producers put, a bounded queue buffers
and applies backpressure, consumers get. `queue.Queue` (threads),
`multiprocessing.Queue` / executor maps (processes), `asyncio.Queue`
(coroutines). Prefer this hand-off topology to shared mutable structures in
every model.

## GOOD

```python
async def main(urls: list[str]) -> None:
    pages = await fetch_many(urls, limit=20)
    digests = await asyncio.to_thread(hash_all, pages)  # CPU off-loop
    store(digests)

asyncio.run(main(URLS))
```

Bounded fan-out, blocking work off the loop, one `asyncio.run` at the top.

## BAD

```python
async def fetch(url):
    return requests.get(url).content   # blocking call freezes the whole loop

def crunch(data):
    threads = [Thread(target=heavy_math, args=(d,)) for d in data]
    [t.start() for t in threads]; [t.join() for t in threads]
```

Sync HTTP inside a coroutine stalls every task. Threads for pure-Python CPU
work serialize on the GIL — `ProcessPoolExecutor` was the answer.

## Red Flags

- Threads added to CPU-bound pure-Python code "for speed".
- Blocking I/O (`requests`, `time.sleep`, file reads) inside `async def`.
- Coroutine called but never awaited.
- Unbounded `gather` over a large collection — no semaphore, no batching.
- Shared boolean flag + lock where an `Event` or queue fits.
- `multiprocessing` task args that don't pickle, or no `__main__` guard under spawn.
- Model chosen without a profile of the actual bottleneck.
- `asyncio.run` called inside library functions or per work item.
