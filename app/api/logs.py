from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.repositories.log_repository import LogRepository
from app.services.log_service import LogService
from app.schemas.log import LogCreate, LogUpdate, LogResponse, LogQuery, LogAggregateResponse
from app.schemas.user import APIResponse
from app.core.redis_conn import get_queue
from app.jobs.export_jobs import export_logs_csv_job
import redis


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
    result = svc.list(start, end, severity, source, limit, offset)
    return APIResponse(
        success=True,
        message="Logs fetched",
        data={
            "logs": [LogResponse.model_validate(l).model_dump() for l in result["items"]],
            "total": result["total"],
            "limit": limit,
            "offset": offset,
        },
    )

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


@router.post("/export", response_model=APIResponse)
def enqueue_export(
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    source: Optional[str] = Query(default=None),
):
    q = get_queue("exports")
    job = q.enqueue(export_logs_csv_job, start.isoformat() if start else None, end.isoformat() if end else None, severity, source)
    return APIResponse(success=True, message="Export enqueued", data={"job_id": job.get_id()})


@router.get("/export/{job_id}", response_model=APIResponse)
def export_status(job_id: str):
    q = get_queue("exports")
    job = q.fetch_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.is_finished:
        return APIResponse(success=True, message="Export ready", data={"status": "finished", "path": job.result})
    if job.is_failed:
        return APIResponse(success=False, message="Export failed", data={"status": "failed"})
    return APIResponse(success=True, message="Export pending", data={"status": job.get_status()})


@router.get("/export/{job_id}/download")
def download_export(job_id: str):
    q = get_queue("exports")
    job = q.fetch_job(job_id)
    if not job or not job.is_finished:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not ready")
    return FileResponse(job.result, filename=job.result.split("/")[-1], media_type="text/csv")
