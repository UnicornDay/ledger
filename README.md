# Task Ledger — AI Agent Activity Database

A lightweight SQLite-based task ledger for tracking every activity across your multi-agent orchestration system. Records which agent ran, what input it received, what output it produced, how many retries it took, and when it happened.

## Why You Need This

- **Audit Trail** — Stop repeating work. Check the ledger before dispatching to see if a task has already been completed.
- **Failure Forensics** — Know exactly which agent failed, how many times it retried, and what error it returned. No more re-running and praying.
- **Orchestration Decisions** — Give your master agent memory between pipeline steps so it can escalate, retry, or wait based on persisted state.

## Files

| File | Role |
|---|---|
| `task_ledger.py` | Writer — `create_task()`, `update_status()`, `get_task()` |
| `query_ledger.py` | Reader — `summary`, `failed`, `run <id>` |
| `agent_ledger.db` | SQLite database (auto-created) |

## Quick Start

```python
from task_ledger import TaskLedger

l = TaskLedger()

# Register a new task
l.create_task("fetch_01", "run_001", "exe_agent", {"cmd": "fetch data"})

# Update its status
l.update_status("fetch_01", "IN_PROGRESS")
l.update_status("fetch_01", "COMPLETED", output_data={"count": 57})

# Retrieve it
t = l.get_task("fetch_01")
print(t["status"])  # COMPLETED
```

## Query Commands

```bash
# Summary of all runs
py query_ledger.py summary

# All failed tasks
py query_ledger.py failed

# Replay a specific run
py query_ledger.py run run_001
```

## Database Schema

```sql
CREATE TABLE task_ledger (
    task_id        TEXT PRIMARY KEY,
    master_run_id  TEXT NOT NULL,
    subagent_name  TEXT NOT NULL,
    status         TEXT NOT NULL CHECK(status IN ('PENDING','IN_PROGRESS','COMPLETED','FAILED')),
    input_payload  TEXT,
    output_payload TEXT,
    retry_count    INTEGER DEFAULT 0,
    updated_at     TEXT NOT NULL
);
```

## Background Reading

- [Building a Master Agent That Orchestrates Your AI Agent Ecosystem](https://medium.com/@wl8380/building-a-master-agent-that-orchestrates-your-ai-agent-ecosystem-4568bbdfbf82)
- [Why Your AI Agents Need a Task Ledger Database](https://medium.com/p/631cc462d3ca)

## License

MIT
