import uuid
from datetime import UTC, date, datetime, timedelta

from sqlmodel import Session

from app.models import TimeEntry, WorkLog
from tests.utils.user import create_random_user


def create_random_worklog(
    db: Session,
    *,
    period_start: date | None = None,
    period_end: date | None = None,
    remittance_status: str = "UNREMITTED",
) -> WorkLog:
    user = create_random_user(db)
    freelancer_id = user.id
    assert freelancer_id is not None

    worklog = WorkLog(
        task_name="Feature implementation",
        freelancer_id=freelancer_id,
        period_start=period_start or date(2026, 1, 1),
        period_end=period_end or date(2026, 1, 31),
        remittance_status=remittance_status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(worklog)
    db.commit()
    db.refresh(worklog)
    return worklog


def add_time_entry(
    db: Session,
    *,
    worklog_id: uuid.UUID,
    hours: float,
    hourly_rate: float,
    is_excluded: bool = False,
) -> TimeEntry:
    started_at = datetime.now(UTC)
    ended_at = started_at + timedelta(hours=1)

    entry = TimeEntry(
        worklog_id=worklog_id,
        started_at=started_at,
        ended_at=ended_at,
        hours=hours,
        hourly_rate=hourly_rate,
        is_excluded=is_excluded,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
