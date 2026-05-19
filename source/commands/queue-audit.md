---
id: queue-audit
kind: command
title: Queue topology audit
description: >
  Walk the queue topology audit checklist. Engages skill:queue-topology-design.
  Per queue: subscriber exists, stale reaper exists, worker not embedded in web,
  dedicated thread pool when noisy.
agents:
  claude: { kind: command }
  cursor: { kind: command }
  codex:  { section: commands }
  goose:  { section: commands }
  openclaw: { section: commands }
  opencode: { kind: command }
  pi:       { section: commands }
  vibe:   { kind: command }
---

Use skill:queue-topology-design.

Steps:

1. List every queue name defined in the codebase. For each queue, answer:
   - Is at least one worker process subscribed to this queue?
   - Is the worker running in a separate process from the web server?
   - Does this queue have its own concurrency and timeout configuration?
   - Is there a stale-job reaper that targets this queue's job table?
2. Check recurring jobs specifically: is each recurring job enqueued to a queue that has an active subscriber?
3. Check for noisy job types sharing a queue with latency-sensitive jobs. Flag any that should be split.
4. Verify observability: does each queue have a depth metric and an error-rate alert?
5. Report findings as a checklist. Mark each item green (pass), yellow (warning), or red (fail).
6. For each red or yellow item, propose the minimal fix referencing skill:queue-topology-design.

Output a flat checklist with queue name, finding, severity, and proposed fix.
