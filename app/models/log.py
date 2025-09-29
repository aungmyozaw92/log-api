from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_logs_ts_sev_src", "timestamp", "severity", "source"),
    )


