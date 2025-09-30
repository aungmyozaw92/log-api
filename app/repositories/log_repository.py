from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from typing import List, Optional
from app.models.log import Log


class LogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, severity: str, source: str, message: str) -> Log:
        log = Log(severity=severity, source=source, message=message)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get(self, log_id: int) -> Optional[Log]:
        return self.db.get(Log, log_id)

    def list(self, start: Optional[datetime], end: Optional[datetime], severity: Optional[str], source: Optional[str], limit: int, offset: int) -> List[Log]:
        stmt = select(Log)
        if start:
            stmt = stmt.where(Log.timestamp >= start)
        if end:
            stmt = stmt.where(Log.timestamp <= end)
        if severity:
            stmt = stmt.where(Log.severity == severity)
        if source:
            stmt = stmt.where(Log.source == source)
        stmt = stmt.order_by(Log.timestamp.desc()).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def count(self, start: Optional[datetime], end: Optional[datetime], severity: Optional[str], source: Optional[str]) -> int:
        stmt = select(func.count()).select_from(Log)
        if start:
            stmt = stmt.where(Log.timestamp >= start)
        if end:
            stmt = stmt.where(Log.timestamp <= end)
        if severity:
            stmt = stmt.where(Log.severity == severity)
        if source:
            stmt = stmt.where(Log.source == source)
        return self.db.execute(stmt).scalar() or 0

    def update(self, log: Log, severity: Optional[str], source: Optional[str], message: Optional[str]) -> Log:
        if severity is not None:
            log.severity = severity
        if source is not None:
            log.source = source
        if message is not None:
            log.message = message
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def delete(self, log: Log) -> None:
        self.db.delete(log)
        self.db.commit()

    def aggregate(self, start: Optional[datetime], end: Optional[datetime], severity: Optional[str], source: Optional[str], by: str):
        if by not in {"severity", "source"}:
            raise ValueError("Invalid aggregate field")
        column = Log.severity if by == "severity" else Log.source
        stmt = select(column.label("key"), func.count().label("count"))
        if start:
            stmt = stmt.where(Log.timestamp >= start)
        if end:
            stmt = stmt.where(Log.timestamp <= end)
        if severity:
            stmt = stmt.where(Log.severity == severity)
        if source:
            stmt = stmt.where(Log.source == source)
        stmt = stmt.group_by(column).order_by(func.count().desc())
        rows = self.db.execute(stmt).all()
        return [{"key": r.key, "count": r.count} for r in rows]
