import uuid
from collections import defaultdict
from datetime import date

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import (
    BatchLineInclusionStatus,
    PaymentBatch,
    PaymentBatchConfirmResult,
    PaymentBatchCreate,
    PaymentBatchExclusionUpdate,
    PaymentBatchReview,
    PaymentBatchStatus,
    PaymentBatchSummary,
    PaymentBatchWorkLog,
    PaymentBatchWorkLogPublic,
    Remittance,
    RemittanceStatus,
    TimeEntry,
    User,
    WorkLog,
    utc_now,
)


class PaymentBatchService:
    @staticmethod
    def _get_freelancer_name(session: Session, freelancer_id: uuid.UUID) -> str:
        freelancer = session.get(User, freelancer_id)
        if not freelancer:
            return "Unknown freelancer"
        if freelancer.full_name:
            return freelancer.full_name
        return freelancer.email

    @staticmethod
    def _validate_date_range(period_start: date, period_end: date) -> None:
        if period_start > period_end:
            raise HTTPException(status_code=400, detail="Invalid date range")

    @staticmethod
    def _get_batch_or_404(session: Session, batch_id: uuid.UUID) -> PaymentBatch:
        batch = session.get(PaymentBatch, batch_id)
        if not batch:
            raise HTTPException(status_code=404, detail="Payment batch not found")
        return batch

    @staticmethod
    def _get_lines(session: Session, batch_id: uuid.UUID) -> list[PaymentBatchWorkLog]:
        return session.exec(
            select(PaymentBatchWorkLog).where(
                PaymentBatchWorkLog.payment_batch_id == batch_id
            )
        ).all()

    @staticmethod
    def _to_line_public(
        line: PaymentBatchWorkLog, freelancer_name: str
    ) -> PaymentBatchWorkLogPublic:
        return PaymentBatchWorkLogPublic(
            id=line.id,
            worklog_id=line.worklog_id,
            freelancer_id=line.freelancer_id,
            freelancer_name=freelancer_name,
            inclusion_status=line.inclusion_status,
            exclusion_reason=line.exclusion_reason,
            amount_snapshot=line.amount_snapshot,
            total_minutes_snapshot=line.total_minutes_snapshot,
            remittance_id=line.remittance_id,
        )

    @staticmethod
    def _build_summary(
        batch: PaymentBatch, lines: list[PaymentBatchWorkLog]
    ) -> PaymentBatchSummary:
        included_lines = [
            line
            for line in lines
            if line.inclusion_status == BatchLineInclusionStatus.INCLUDED
        ]
        gross_total = sum(line.amount_snapshot for line in lines)
        net_total = sum(line.amount_snapshot for line in included_lines)
        return PaymentBatchSummary(
            id=batch.id,
            period_start=batch.period_start,
            period_end=batch.period_end,
            status=batch.status,
            currency=batch.currency,
            created_by_id=batch.created_by_id,
            confirmed_by_id=batch.confirmed_by_id,
            idempotency_key=batch.idempotency_key,
            error_message=batch.error_message,
            confirmed_at=batch.confirmed_at,
            created_at=batch.created_at,
            updated_at=batch.updated_at,
            included_count=len(included_lines),
            excluded_count=len(lines) - len(included_lines),
            gross_total=gross_total,
            net_total=net_total,
        )

    @staticmethod
    def _get_worklog_snapshot(
        session: Session, worklog_id: uuid.UUID
    ) -> tuple[float, int]:
        entries = session.exec(
            select(TimeEntry).where(TimeEntry.worklog_id == worklog_id)
        ).all()
        amount = 0.0
        total_minutes = 0
        for entry in entries:
            total_minutes += int(round(entry.hours * 60))
            if entry.is_excluded:
                continue
            amount += entry.hours * entry.hourly_rate
        return amount, total_minutes

    @staticmethod
    def create_batch(
        session: Session, current_user: User, batch_in: PaymentBatchCreate
    ) -> PaymentBatchSummary:
        PaymentBatchService._validate_date_range(
            batch_in.period_start, batch_in.period_end
        )

        batch = PaymentBatch(
            period_start=batch_in.period_start,
            period_end=batch_in.period_end,
            currency=batch_in.currency.upper(),
            status=PaymentBatchStatus.DRAFT,
            created_by_id=current_user.id,
        )
        session.add(batch)
        session.commit()
        session.refresh(batch)

        worklogs = session.exec(
            select(WorkLog)
            .where(WorkLog.period_start >= batch_in.period_start)
            .where(WorkLog.period_end <= batch_in.period_end)
            .where(WorkLog.remittance_status == "UNREMITTED")
        ).all()

        lines: list[PaymentBatchWorkLog] = []
        for worklog in worklogs:
            amount, total_minutes = PaymentBatchService._get_worklog_snapshot(
                session, worklog.id
            )
            line = PaymentBatchWorkLog(
                payment_batch_id=batch.id,
                worklog_id=worklog.id,
                freelancer_id=worklog.freelancer_id,
                amount_snapshot=amount,
                total_minutes_snapshot=total_minutes,
                inclusion_status=BatchLineInclusionStatus.INCLUDED,
            )
            lines.append(line)
            session.add(line)

        batch.total_amount_snapshot = sum(line.amount_snapshot for line in lines)
        batch.updated_at = utc_now()
        session.add(batch)
        session.commit()
        session.refresh(batch)

        return PaymentBatchService._build_summary(batch, lines)

    @staticmethod
    def get_batch(session: Session, batch_id: uuid.UUID) -> PaymentBatchSummary:
        batch = PaymentBatchService._get_batch_or_404(session, batch_id)
        lines = PaymentBatchService._get_lines(session, batch_id)
        return PaymentBatchService._build_summary(batch, lines)

    @staticmethod
    def update_exclusions(
        session: Session,
        current_user: User,
        batch_id: uuid.UUID,
        exclusion_in: PaymentBatchExclusionUpdate,
    ) -> PaymentBatchSummary:
        batch = PaymentBatchService._get_batch_or_404(session, batch_id)
        if batch.status != PaymentBatchStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Only DRAFT payment batches can be modified",
            )

        excluded_worklog_ids = set(exclusion_in.excluded_worklog_ids)
        excluded_freelancer_ids = set(exclusion_in.excluded_freelancer_ids)
        reason = exclusion_in.reason or "Excluded by admin"

        lines = PaymentBatchService._get_lines(session, batch_id)
        for line in lines:
            if line.worklog_id in excluded_worklog_ids:
                line.inclusion_status = BatchLineInclusionStatus.EXCLUDED_WORKLOG
                line.exclusion_reason = reason
                line.excluded_at = utc_now()
                line.excluded_by_id = current_user.id
            elif line.freelancer_id in excluded_freelancer_ids:
                line.inclusion_status = BatchLineInclusionStatus.EXCLUDED_FREELANCER
                line.exclusion_reason = reason
                line.excluded_at = utc_now()
                line.excluded_by_id = current_user.id
            else:
                line.inclusion_status = BatchLineInclusionStatus.INCLUDED
                line.exclusion_reason = None
                line.excluded_at = None
                line.excluded_by_id = None
            session.add(line)

        batch.updated_at = utc_now()
        batch.total_amount_snapshot = sum(
            line.amount_snapshot
            for line in lines
            if line.inclusion_status == BatchLineInclusionStatus.INCLUDED
        )
        session.add(batch)
        session.commit()
        session.refresh(batch)

        return PaymentBatchService._build_summary(batch, lines)

    @staticmethod
    def review_batch(session: Session, batch_id: uuid.UUID) -> PaymentBatchReview:
        batch = PaymentBatchService._get_batch_or_404(session, batch_id)
        lines = PaymentBatchService._get_lines(session, batch_id)
        freelancer_names: dict[uuid.UUID, str] = {}

        def get_line_freelancer_name(freelancer_id: uuid.UUID) -> str:
            if freelancer_id not in freelancer_names:
                freelancer_names[freelancer_id] = (
                    PaymentBatchService._get_freelancer_name(session, freelancer_id)
                )
            return freelancer_names[freelancer_id]

        included_worklogs = [
            PaymentBatchService._to_line_public(
                line, get_line_freelancer_name(line.freelancer_id)
            )
            for line in lines
            if line.inclusion_status == BatchLineInclusionStatus.INCLUDED
        ]
        excluded_worklogs = [
            PaymentBatchService._to_line_public(
                line, get_line_freelancer_name(line.freelancer_id)
            )
            for line in lines
            if line.inclusion_status != BatchLineInclusionStatus.INCLUDED
        ]

        return PaymentBatchReview(
            batch=PaymentBatchService._build_summary(batch, lines),
            included_worklogs=included_worklogs,
            excluded_worklogs=excluded_worklogs,
        )

    @staticmethod
    def confirm_batch(
        session: Session,
        current_user: User,
        batch_id: uuid.UUID,
        idempotency_key: str | None,
    ) -> PaymentBatchConfirmResult:
        batch = PaymentBatchService._get_batch_or_404(session, batch_id)
        lines = PaymentBatchService._get_lines(session, batch_id)

        if batch.status == PaymentBatchStatus.CONFIRMED:
            remittance_ids = [
                remittance.id
                for remittance in session.exec(
                    select(Remittance).where(Remittance.payment_batch_id == batch_id)
                ).all()
            ]
            return PaymentBatchConfirmResult(
                batch=PaymentBatchService._build_summary(batch, lines),
                remittance_ids=remittance_ids,
            )

        if batch.status != PaymentBatchStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Only DRAFT payment batches can be confirmed",
            )

        if batch.idempotency_key and idempotency_key:
            if batch.idempotency_key != idempotency_key:
                raise HTTPException(
                    status_code=409,
                    detail="Batch already uses a different idempotency key",
                )

        if idempotency_key and not batch.idempotency_key:
            batch.idempotency_key = idempotency_key

        included_lines = [
            line
            for line in lines
            if line.inclusion_status == BatchLineInclusionStatus.INCLUDED
        ]
        if not included_lines:
            raise HTTPException(
                status_code=400,
                detail="No included worklogs to remit",
            )

        try:
            freelancer_totals: dict[uuid.UUID, float] = defaultdict(float)
            freelancer_lines: dict[uuid.UUID, list[PaymentBatchWorkLog]] = defaultdict(
                list
            )
            for line in included_lines:
                freelancer_totals[line.freelancer_id] += line.amount_snapshot
                freelancer_lines[line.freelancer_id].append(line)

            remittances: list[Remittance] = []
            for freelancer_id, total in freelancer_totals.items():
                remittance = Remittance(
                    payment_batch_id=batch.id,
                    freelancer_id=freelancer_id,
                    status=RemittanceStatus.SUCCEEDED,
                    amount=total,
                )
                session.add(remittance)
                remittances.append(remittance)

            session.flush()

            remittance_id_by_freelancer = {
                remittance.freelancer_id: remittance.id for remittance in remittances
            }

            worklog_ids = {line.worklog_id for line in included_lines}
            for worklog_id in worklog_ids:
                worklog = session.get(WorkLog, worklog_id)
                if worklog:
                    worklog.remittance_status = "REMITTED"
                    worklog.updated_at = utc_now()
                    session.add(worklog)

            for freelancer_id, lines_for_freelancer in freelancer_lines.items():
                remittance_id = remittance_id_by_freelancer[freelancer_id]
                for line in lines_for_freelancer:
                    line.remittance_id = remittance_id
                    session.add(line)

            batch.status = PaymentBatchStatus.CONFIRMED
            batch.confirmed_by_id = current_user.id
            batch.confirmed_at = utc_now()
            batch.updated_at = utc_now()
            batch.total_amount_snapshot = sum(
                line.amount_snapshot for line in included_lines
            )
            session.add(batch)
            session.commit()
            session.refresh(batch)

            return PaymentBatchConfirmResult(
                batch=PaymentBatchService._build_summary(batch, lines),
                remittance_ids=[remittance.id for remittance in remittances],
            )
        except Exception as exc:
            session.rollback()
            failing_batch = PaymentBatchService._get_batch_or_404(session, batch_id)
            failing_batch.status = PaymentBatchStatus.FAILED
            failing_batch.error_message = f"{type(exc).__name__}: {exc}"[:255]
            failing_batch.updated_at = utc_now()
            session.add(failing_batch)
            session.commit()
            raise HTTPException(
                status_code=400,
                detail="Failed to confirm payment batch",
            )

    @staticmethod
    def cancel_batch(
        session: Session,
        current_user: User,
        batch_id: uuid.UUID,
    ) -> PaymentBatchSummary:
        del current_user
        batch = PaymentBatchService._get_batch_or_404(session, batch_id)
        if batch.status != PaymentBatchStatus.DRAFT:
            raise HTTPException(
                status_code=400,
                detail="Only DRAFT payment batches can be cancelled",
            )
        batch.status = PaymentBatchStatus.CANCELLED
        batch.updated_at = utc_now()
        session.add(batch)
        session.commit()
        session.refresh(batch)
        lines = PaymentBatchService._get_lines(session, batch_id)
        return PaymentBatchService._build_summary(batch, lines)
