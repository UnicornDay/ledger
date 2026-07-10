import sqlite3
import json
from datetime import datetime

class TaskLedger:
    def __init__(self, db_path="agent_ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database and creates the ledger table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_ledger (
                    task_id TEXT PRIMARY KEY,
                    master_run_id TEXT NOT NULL,
                    subagent_name TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),
                    input_payload TEXT,
                    output_payload TEXT,
                    retry_count INTEGER DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def create_task(self, task_id, master_run_id, subagent_name, input_data):
        """Registers a new subtask in the ledger."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                INSERT INTO task_ledger (task_id, master_run_id, subagent_name, status, input_payload, updated_at)
                VALUES (?, ?, ?, 'PENDING', ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    status='PENDING',
                    input_payload=excluded.input_payload,
                    updated_at=excluded.updated_at
            """, (task_id, master_run_id, subagent_name, json.dumps(input_data), now))
            conn.commit()

    def update_status(self, task_id, status, output_data=None, increment_retry=False):
        """Updates a task's status, timestamp, outputs, and optionally increments the retry counter."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            output_str = json.dumps(output_data) if output_data is not None else None
            
            if increment_retry:
                cursor.execute("""
                    UPDATE task_ledger 
                    SET status = ?, output_payload = ?, retry_count = retry_count + 1, updated_at = ?
                    WHERE task_id = ?
                """, (status, output_str, now, task_id))
            else:
                cursor.execute("""
                    UPDATE task_ledger 
                    SET status = ?, output_payload = ?, updated_at = ?
                    WHERE task_id = ?
                """, (status, output_str, now, task_id))
            conn.commit()

    def get_task(self, task_id):
        """Retrieves details for a specific task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM task_ledger WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None


if __name__ == "__main__":
    ledger = TaskLedger()
    print("Database and 'task_ledger' table initialized successfully.")
    
    ledger.create_task("fetch_prices_01", "run_abc123", "yfinance_agent", {"ticker": "BTC-USD"})
    print("Task created: PENDING")
    
    ledger.update_status("fetch_prices_01", "IN_PROGRESS")
    print("Task updated: IN_PROGRESS")
    
    ledger.update_status("fetch_prices_01", "COMPLETED", output_data={"price": 65000, "currency": "USD"})
    print("Task updated: COMPLETED with payload saved.")
