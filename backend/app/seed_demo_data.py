import logging
from datetime import date, datetime, time, timezone

from sqlmodel import Session, delete, select

from app import crud
from app.core.db import engine
from app.models import TimeEntry, User, UserCreate, WorkLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SEED_USERS = [
    {
        "email": "freelancer.alex@example.com",
        "password": "changethis",
        "full_name": "Alex Rivera",
    },
    {
        "email": "freelancer.maya@example.com",
        "password": "changethis",
        "full_name": "Maya Patel",
    },
    {
        "email": "freelancer.liam@example.com",
        "password": "changethis",
        "full_name": "Liam Johnson",
    },
]


SEED_WORKLOGS = {
    "freelancer.alex@example.com": [
        {
            "task_name": "API integration sprint",
            "period_start": date(2024, 2, 1),
            "period_end": date(2024, 2, 14),
            "remittance_status": "UNREMITTED",
            "entries": [
                {"hours": 4.0, "hourly_rate": 70.0, "is_excluded": False},
                {"hours": 2.0, "hourly_rate": 70.0, "is_excluded": False},
                {"hours": 1.0, "hourly_rate": 70.0, "is_excluded": True},
            ],
        },
        {
            "task_name": "Incident response hardening",
            "period_start": date(2025, 9, 10),
            "period_end": date(2025, 9, 25),
            "remittance_status": "UNREMITTED",
            "entries": [
                {"hours": 3.5, "hourly_rate": 90.0, "is_excluded": False},
                {"hours": 2.5, "hourly_rate": 90.0, "is_excluded": False},
            ],
        },
        {
            "task_name": "Legacy migration support",
            "period_start": date(2026, 1, 5),
            "period_end": date(2026, 1, 20),
            "remittance_status": "REMITTED",
            "entries": [
                {"hours": 5.0, "hourly_rate": 80.0, "is_excluded": False},
                {"hours": 1.5, "hourly_rate": 80.0, "is_excluded": False},
            ],
        },
    ],
    "freelancer.maya@example.com": [
        {
            "task_name": "Frontend dashboard polish",
            "period_start": date(2024, 7, 1),
            "period_end": date(2024, 7, 20),
            "remittance_status": "UNREMITTED",
            "entries": [
                {"hours": 6.0, "hourly_rate": 65.0, "is_excluded": False},
                {"hours": 2.0, "hourly_rate": 65.0, "is_excluded": False},
            ],
        },
        {
            "task_name": "Accessibility remediation",
            "period_start": date(2025, 4, 4),
            "period_end": date(2025, 4, 28),
            "remittance_status": "UNREMITTED",
            "entries": [
                {"hours": 3.0, "hourly_rate": 75.0, "is_excluded": False},
                {"hours": 2.0, "hourly_rate": 75.0, "is_excluded": False},
                {"hours": 1.0, "hourly_rate": 75.0, "is_excluded": True},
            ],
        },
        {
            "task_name": "Post-release support",
            "period_start": date(2026, 3, 1),
            "period_end": date(2026, 3, 15),
            "remittance_status": "REMITTED",
            "entries": [
                {"hours": 2.5, "hourly_rate": 70.0, "is_excluded": False},
                {"hours": 2.5, "hourly_rate": 70.0, "is_excluded": False},
            ],
        },
    ],
    "freelancer.liam@example.com": [
        {
            "task_name": "Data backfill scripts",
            "period_start": date(2024, 11, 11),
            "period_end": date(2024, 11, 30),
            "remittance_status": "UNREMITTED",
            "entries": [
                {"hours": 4.5, "hourly_rate": 85.0, "is_excluded": False},
                {"hours": 3.0, "hourly_rate": 85.0, "is_excluded": False},
            ],
        },
        {
            "task_name": "Monitoring alert tuning",
            "period_start": date(2025, 12, 1),
            "period_end": date(2025, 12, 18),
            "remittance_status": "UNREMITTED",
            "entries": [
                {"hours": 2.0, "hourly_rate": 95.0, "is_excluded": False},
                {"hours": 3.0, "hourly_rate": 95.0, "is_excluded": False},
            ],
        },
        {
            "task_name": "Production rollout",
            "period_start": date(2026, 5, 1),
            "period_end": date(2026, 5, 19),
            "remittance_status": "REMITTED",
            "entries": [
                {"hours": 3.0, "hourly_rate": 100.0, "is_excluded": False},
                {"hours": 1.0, "hourly_rate": 100.0, "is_excluded": True},
            ],
        },
    ],
}


def _get_or_create_user(
    session: Session,
    *,
    email: str,
    password: str,
    full_name: str,
) -> User:
    user = crud.get_user_by_email(session=session, email=email)
    if user:
        user.full_name = full_name
        user.is_active = True
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    created = crud.create_user(
        session=session,
        user_create=UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_superuser=False,
            is_active=True,
        ),
    )
    return created


def _seed_worklog(
    session: Session,
    *,
    freelancer_id,
    task_name: str,
    period_start: date,
    period_end: date,
    remittance_status: str,
    entries: list[dict[str, float | bool]],
) -> None:
    existing = session.exec(
        select(WorkLog)
        .where(WorkLog.freelancer_id == freelancer_id)
        .where(WorkLog.task_name == task_name)
        .where(WorkLog.period_start == period_start)
        .where(WorkLog.period_end == period_end)
    ).first()

    if existing:
        worklog = existing
        worklog.remittance_status = remittance_status
        worklog.updated_at = datetime.now(timezone.utc)
        session.add(worklog)
        session.commit()
        session.refresh(worklog)
        session.exec(delete(TimeEntry).where(TimeEntry.worklog_id == worklog.id))
        session.commit()
    else:
        worklog = WorkLog(
            freelancer_id=freelancer_id,
            task_name=task_name,
            period_start=period_start,
            period_end=period_end,
            remittance_status=remittance_status,
        )
        session.add(worklog)
        session.commit()
        session.refresh(worklog)

    for index, entry in enumerate(entries):
        day = min(period_start.day + index, 28)
        started_at = datetime.combine(
            date(period_start.year, period_start.month, day),
            time(9, 0),
            tzinfo=timezone.utc,
        )
        ended_at = datetime.combine(
            date(period_start.year, period_start.month, day),
            time(10, 0),
            tzinfo=timezone.utc,
        )
        time_entry = TimeEntry(
            worklog_id=worklog.id,
            started_at=started_at,
            ended_at=ended_at,
            hours=float(entry["hours"]),
            hourly_rate=float(entry["hourly_rate"]),
            is_excluded=bool(entry["is_excluded"]),
        )
        session.add(time_entry)

    session.commit()


def init() -> None:
    with Session(engine) as session:
        logger.info("Seeding demo users and worklogs")
        for user_seed in SEED_USERS:
            user = _get_or_create_user(
                session,
                email=user_seed["email"],
                password=user_seed["password"],
                full_name=user_seed["full_name"],
            )
            worklogs = SEED_WORKLOGS[user_seed["email"]]
            for worklog_seed in worklogs:
                _seed_worklog(
                    session,
                    freelancer_id=user.id,
                    task_name=worklog_seed["task_name"],
                    period_start=worklog_seed["period_start"],
                    period_end=worklog_seed["period_end"],
                    remittance_status=worklog_seed["remittance_status"],
                    entries=worklog_seed["entries"],
                )
        logger.info("Demo seed completed")


def main() -> None:
    init()


if __name__ == "__main__":
    main()
