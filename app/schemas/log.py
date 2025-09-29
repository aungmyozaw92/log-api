from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class LogCreate(BaseModel):
	severity: str = Field(min_length=1, max_length=50)
	source: str = Field(min_length=1, max_length=100)
	message: str = Field(min_length=1, max_length=1000)


class LogUpdate(BaseModel):
	severity: Optional[str] = Field(default=None, min_length=1, max_length=50)
	source: Optional[str] = Field(default=None, min_length=1, max_length=100)
	message: Optional[str] = Field(default=None, min_length=1, max_length=1000)


class LogResponse(BaseModel):
	id: int
	timestamp: datetime
	severity: str
	source: str
	message: str

	model_config = ConfigDict(from_attributes=True)


class LogQuery(BaseModel):
	start: Optional[datetime] = None
	end: Optional[datetime] = None
	severity: Optional[str] = None
	source: Optional[str] = None
	limit: int = Field(default=100, ge=1, le=1000)
	offset: int = Field(default=0, ge=0)


class LogAggregateBucket(BaseModel):
	key: str
	count: int


class LogAggregateResponse(BaseModel):
	by: str
	buckets: List[LogAggregateBucket]
