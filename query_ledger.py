import sqlite3, json, sys

db_path = r"C:\Users\willi\.opencode\master\agent_ledger.db"
mode = sys.argv[1] if len(sys.argv) > 1 else "summary"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

if mode == "summary":
    rows = conn.execute("""
        SELECT master_run_id, subagent_name, status, COUNT(*) as cnt
        FROM task_ledger GROUP BY master_run_id, subagent_name, status
        ORDER BY master_run_id
    """).fetchall()
    for r in rows:
        print(f"{r['master_run_id']:30s} {r['subagent_name']:15s} {r['status']:12s} {r['cnt']} tasks")

elif mode == "failed":
    rows = conn.execute("SELECT * FROM task_ledger WHERE status='FAILED'").fetchall()
    print(json.dumps([dict(r) for r in rows], indent=2) if rows else "No failed tasks")

elif mode == "run":
    run_id = sys.argv[2]
    rows = conn.execute("SELECT * FROM task_ledger WHERE master_run_id=? ORDER BY task_id", (run_id,)).fetchall()
    for r in rows:
        d = dict(r)
        print(f"{d['task_id']:30s} {d['subagent_name']:15s} {d['status']:12s} retry={d['retry_count']}")

conn.close()
