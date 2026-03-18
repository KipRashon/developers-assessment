import uuid
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import Session, func, select

from app.models import (
    TimeEntry,
    TimeEntryPublic,
    User,
    WorkLog,
    WorkLogDetailPublic,
    WorkLogFreelancerFilterOptionPublic,
    WorkLogFreelancersPublic,
    WorkLogListItemPublic,
    WorkLogsPublic,
)


class WorkLogService:
    @staticmethod
    def _get_freelancer_name(session: Session, freelancer_id: uuid.UUID) -> str:
        freelancer = session.get(User, freelancer_id)
        if not freelancer:
            return "Unknown freelancer"
        if freelancer.full_name:
            return freelancer.full_name
        return freelancer.email

    @staticmethod
    def _validate_date_range(start_date: date | None, end_date: date | None) -> None:
        if start_date is not None and end_date is not None and start_date > end_date:
            raise HTTPException(status_code=400, detail="Invalid date range")

    @staticmethod
    def _validate_remittance_status(remittance_status: str | None) -> None:
        if remittance_status is None:
            return

        if remittance_status not in {"REMITTED", "UNREMITTED"}:
            raise HTTPException(
                status_code=400,
                detail="Invalid remittance status. Use REMITTED or UNREMITTED",
            )

    @staticmethod
    def _calc_earned_amount(time_entries: list[TimeEntry]) -> float:
        amount = Decimal("0")
        for entry in time_entries:
            if entry.is_excluded:
                continue
            amount += Decimal(str(entry.hours)) * Decimal(str(entry.hourly_rate))

        return float(amount)

    @staticmethod
    def get_worklogs(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        start_date: date | None = None,
        end_date: date | None = None,
        remittance_status: str | None = None,
        freelancer_id: uuid.UUID | None = None,
    ) -> WorkLogsPublic:
        WorkLogService._validate_date_range(start_date, end_date)
        WorkLogService._validate_remittance_status(remittance_status)

        statement = select(WorkLog)
        count_statement = select(func.count()).select_from(WorkLog)

        if start_date is not None:
            statement = statement.where(WorkLog.period_start >= start_date)
            count_statement = count_statement.where(WorkLog.period_start >= start_date)
        if end_date is not None:
            statement = statement.where(WorkLog.period_end <= end_date)
            count_statement = count_statement.where(WorkLog.period_end <= end_date)
        if remittance_status is not None:
            statement = statement.where(WorkLog.remittance_status == remittance_status)
            count_statement = count_statement.where(
                WorkLog.remittance_status == remittance_status
            )
        if freelancer_id is not None:
            statement = statement.where(WorkLog.freelancer_id == freelancer_id)
            count_statement = count_statement.where(
                WorkLog.freelancer_id == freelancer_id
            )

        worklogs = session.exec(statement.offset(skip).limit(limit)).all()
        count = session.exec(count_statement).one()

        data: list[WorkLogListItemPublic] = []
        for worklog in worklogs:
            time_entries = session.exec(
                select(TimeEntry).where(TimeEntry.worklog_id == worklog.id)
            ).all()
            data.append(
                WorkLogListItemPublic(
                    id=worklog.id,
                    task_name=worklog.task_name,
                    freelancer_id=worklog.freelancer_id,
                    freelancer_name=WorkLogService._get_freelancer_name(
                        session, worklog.freelancer_id
                    ),
                    period_start=worklog.period_start,
                    period_end=worklog.period_end,
                    remittance_status=worklog.remittance_status,
                    earned_amount=WorkLogService._calc_earned_amount(time_entries),
                )
            )

        return WorkLogsPublic(data=data, count=count)

    @staticmethod
    def get_worklog_freelancers(
        session: Session,
        start_date: date | None = None,
        end_date: date | None = None,
        remittance_status: str | None = None,
    ) -> WorkLogFreelancersPublic:
        WorkLogService._validate_date_range(start_date, end_date)
        WorkLogService._validate_remittance_status(remittance_status)

        statement = select(WorkLog)

        if start_date is not None:
            statement = statement.where(WorkLog.period_start >= start_date)
        if end_date is not None:
            statement = statement.where(WorkLog.period_end <= end_date)
        if remittance_status is not None:
            statement = statement.where(WorkLog.remittance_status == remittance_status)

        worklogs = session.exec(statement).all()
        freelancer_names: dict[uuid.UUID, str] = {}
        for worklog in worklogs:
            if worklog.freelancer_id in freelancer_names:
                continue
            freelancer_names[worklog.freelancer_id] = (
                WorkLogService._get_freelancer_name(session, worklog.freelancer_id)
            )

        data = [
            WorkLogFreelancerFilterOptionPublic(id=freelancer_id, name=name)
            for freelancer_id, name in freelancer_names.items()
        ]
        data.sort(key=lambda row: row.name.lower())

        return WorkLogFreelancersPublic(data=data, count=len(data))

    @staticmethod
    def get_worklog_detail(
        session: Session, worklog_id: uuid.UUID
    ) -> WorkLogDetailPublic:
        worklog = session.get(WorkLog, worklog_id)
        if not worklog:
            raise HTTPException(status_code=404, detail="Worklog not found")

        time_entries = session.exec(
            select(TimeEntry).where(TimeEntry.worklog_id == worklog_id)
        ).all()

        time_entries_public = [
            TimeEntryPublic.model_validate(entry) for entry in time_entries
        ]

        return WorkLogDetailPublic(
            id=worklog.id,
            task_name=worklog.task_name,
            freelancer_id=worklog.freelancer_id,
            freelancer_name=WorkLogService._get_freelancer_name(
                session, worklog.freelancer_id
            ),
            period_start=worklog.period_start,
            period_end=worklog.period_end,
            remittance_status=worklog.remittance_status,
            earned_amount=WorkLogService._calc_earned_amount(time_entries),
            time_entries=time_entries_public,
        )
