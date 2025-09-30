import csv
import io
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.repositories.log_repository import LogRepository


def export_logs_csv_job(start: Optional[str], end: Optional[str], severity: Optional[str], source: Optional[str]) -> str:
    db: Session = SessionLocal()
    try:
        repo = LogRepository(db)
        # Parse ISO strings to datetime if provided
        def _to_dt(v: Optional[str]) -> Optional[datetime]:
            if not v:
                return None
            try:
                return datetime.fromisoformat(v)
            except Exception:
                return None
        start_dt = _to_dt(start)
        end_dt = _to_dt(end)
        # stream through pages
        limit = 1000
        offset = 0
        rows = []
        while True:
            items = repo.list(start_dt, end_dt, severity, source, limit, offset)
            if not items:
                break
            for l in items:
                rows.append([l.id, l.timestamp.isoformat() if l.timestamp else "", l.severity, l.source, l.message])
            offset += limit
        # write csv to tmp file
        now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"logs_export_{now}.csv"
        out_dir = os.getenv("EXPORT_DIR", "/tmp")
        path = os.path.join(out_dir, filename)
        os.makedirs(out_dir, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "timestamp", "severity", "source", "message"])
            writer.writerows(rows)
        return path
    finally:
        db.close()


