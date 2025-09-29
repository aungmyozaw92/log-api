from typing import Optional, List
from datetime import datetime
from app.repositories.log_repository import LogRepository
from app.models.log import Log


class LogService:
    def __init__(self, repo: LogRepository):
        self.repo = repo

    def create(self, severity: str, source: str, message: str) -> Log:
        return self.repo.create(severity, source, message)

    def get(self, log_id: int) -> Optional[Log]:
        return self.repo.get(log_id)

    def list(self, start: Optional[datetime], end: Optional[datetime], severity: Optional[str], source: Optional[str], limit: int, offset: int) -> List[Log]:
        return self.repo.list(start, end, severity, source, limit, offset)

    def update(self, log_id: int, severity: Optional[str], source: Optional[str], message: Optional[str]) -> Optional[Log]:
        log = self.repo.get(log_id)
        if not log:
            return None
        return self.repo.update(log, severity, source, message)

    def delete(self, log_id: int) -> bool:
        log = self.repo.get(log_id)
        if not log:
            return False
        self.repo.delete(log)
        return True

    def aggregate(self, start: Optional[datetime], end: Optional[datetime], severity: Optional[str], source: Optional[str], by: str):
        return self.repo.aggregate(start, end, severity, source, by)


