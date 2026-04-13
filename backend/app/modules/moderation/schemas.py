from uuid import UUID

from pydantic import BaseModel, Field


class BlockCreate(BaseModel):
    profile_id: UUID


class BlockResponse(BaseModel):
    message: str


class ReportCreate(BaseModel):
    profile_id: UUID
    reason_code: str = Field(min_length=2, max_length=64)
    notes: str | None = Field(default=None, max_length=1000)


class ReportResponse(BaseModel):
    message: str