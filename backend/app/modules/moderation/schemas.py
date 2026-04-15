from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import ProfileStatus, ReportStatus


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


class AdminReportUserSummary(BaseModel):
    id: UUID
    email: str


class AdminReportProfileSummary(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    profile_status: ProfileStatus


class AdminReportListItem(BaseModel):
    id: UUID
    reporter: AdminReportUserSummary
    reported_user: AdminReportUserSummary
    reported_profile: AdminReportProfileSummary
    reason_code: str
    status: ReportStatus
    created_at: datetime


class AdminReportDetail(AdminReportListItem):
    notes: str | None
    updated_at: datetime


class AdminReportStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ReportStatus
