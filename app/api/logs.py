from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.repositories.log_repository import LogRepository
from app.services.log_service import LogService
from app.schemas.log import LogCreate, LogUpdate, LogResponse, LogQuery, LogAggregateResponse
from app.schemas.user import APIResponse


router = APIRouter()


def get_log_service(db: Session = Depends(get_db)):
    return LogService(LogRepository(db))


@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_log(body: LogCreate, svc: LogService = Depends(get_log_service)):
    log = svc.create(body.severity, body.source, body.message)
    return APIResponse(success=True, message="Log created", data={"log": LogResponse.model_validate(log).model_dump()})


@router.get("/{log_id}", response_model=APIResponse)
def get_log(log_id: int, svc: LogService = Depends(get_log_service)):
    log = svc.get(log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return APIResponse(success=True, message="Log fetched", data={"log": LogResponse.model_validate(log).model_dump()})


@router.get("/", response_model=APIResponse)
def list_logs(
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    svc: LogService = Depends(get_log_service),
):
    logs = svc.list(start, end, severity, source, limit, offset)
    return APIResponse(success=True, message="Logs fetched", data={"logs": [LogResponse.model_validate(l).model_dump() for l in logs]})


@router.patch("/{log_id}", response_model=APIResponse)
def update_log(log_id: int, body: LogUpdate, svc: LogService = Depends(get_log_service)):
    updated = svc.update(log_id, body.severity, body.source, body.message)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return APIResponse(success=True, message="Log updated", data={"log": LogResponse.model_validate(updated).model_dump()})


@router.delete("/{log_id}", response_model=APIResponse, status_code=status.HTTP_200_OK)
def delete_log(log_id: int, svc: LogService = Depends(get_log_service)):
    ok = svc.delete(log_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return APIResponse(success=True, message="Log deleted", data=None)


@router.get("/aggregate/by/{by}", response_model=APIResponse)
def aggregate_logs(
    by: str,
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
    svc: LogService = Depends(get_log_service),
):
    buckets = svc.aggregate(start, end, severity, source, by)
    return APIResponse(success=True, message="Aggregates fetched", data={"aggregation": {"by": by, "buckets": buckets}})


