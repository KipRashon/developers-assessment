from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import (
    PaymentBatch,
    PaymentBatchStatus,
    PaymentBatchWorkLog,
    Remittance,
    WorkLog,
)
from tests.utils.worklog import add_time_entry, create_random_worklog


def test_create_and_review_payment_batch(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    worklog = create_random_worklog(
        db,
        period_start=date(2026, 2, 1),
        period_end=date(2026, 2, 28),
    )
    add_time_entry(db, worklog_id=worklog.id, hours=2, hourly_rate=40)
    add_time_entry(db, worklog_id=worklog.id, hours=1, hourly_rate=20, is_excluded=True)

    create_response = client.post(
        f"{settings.API_V1_STR}/payment-batches/",
        headers=superuser_token_headers,
        json={"period_start": "2026-02-01", "period_end": "2026-02-28"},
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "DRAFT"
    assert created["included_count"] >= 1

    review_response = client.get(
        f"{settings.API_V1_STR}/payment-batches/{created['id']}/review",
        headers=superuser_token_headers,
    )
    assert review_response.status_code == 200
    review = review_response.json()
    assert review["batch"]["id"] == created["id"]
    assert len(review["included_worklogs"]) >= 1
    assert review["included_worklogs"][0]["freelancer_name"]


def test_review_payment_batch_returns_freelancer_name_for_exclusions(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    worklog = create_random_worklog(
        db,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 31),
    )
    add_time_entry(db, worklog_id=worklog.id, hours=2, hourly_rate=40)

    create_response = client.post(
        f"{settings.API_V1_STR}/payment-batches/",
        headers=superuser_token_headers,
        json={"period_start": "2026-05-01", "period_end": "2026-05-31"},
    )
    assert create_response.status_code == 201
    batch_id = create_response.json()["id"]

    exclusion_response = client.put(
        f"{settings.API_V1_STR}/payment-batches/{batch_id}/exclusions",
        headers=superuser_token_headers,
        json={
            "excluded_worklog_ids": [str(worklog.id)],
            "reason": "Disputed",
        },
    )
    assert exclusion_response.status_code == 200

    review_response = client.get(
        f"{settings.API_V1_STR}/payment-batches/{batch_id}/review",
        headers=superuser_token_headers,
    )

    assert review_response.status_code == 200
    excluded = review_response.json()["excluded_worklogs"]
    assert len(excluded) >= 1
    assert excluded[0]["freelancer_name"]


def test_update_payment_batch_exclusions(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    worklog = create_random_worklog(
        db,
        period_start=date(2026, 3, 1),
        period_end=date(2026, 3, 31),
    )
    add_time_entry(db, worklog_id=worklog.id, hours=1, hourly_rate=100)

    create_response = client.post(
        f"{settings.API_V1_STR}/payment-batches/",
        headers=superuser_token_headers,
        json={"period_start": "2026-03-01", "period_end": "2026-03-31"},
    )
    batch_id = create_response.json()["id"]

    exclusion_response = client.put(
        f"{settings.API_V1_STR}/payment-batches/{batch_id}/exclusions",
        headers=superuser_token_headers,
        json={
            "excluded_worklog_ids": [str(worklog.id)],
            "reason": "Disputed",
        },
    )

    assert exclusion_response.status_code == 200
    content = exclusion_response.json()
    assert content["excluded_count"] >= 1
    assert content["net_total"] == 0


def test_confirm_payment_batch_is_idempotent(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    worklog = create_random_worklog(
        db,
        period_start=date(2026, 4, 1),
        period_end=date(2026, 4, 30),
    )
    add_time_entry(db, worklog_id=worklog.id, hours=2, hourly_rate=50)

    create_response = client.post(
        f"{settings.API_V1_STR}/payment-batches/",
        headers=superuser_token_headers,
        json={"period_start": "2026-04-01", "period_end": "2026-04-30"},
    )
    batch_id = create_response.json()["id"]

    first_confirm = client.post(
        f"{settings.API_V1_STR}/payment-batches/{batch_id}/confirm",
        headers={**superuser_token_headers, "Idempotency-Key": "phase4-key-1"},
    )
    assert first_confirm.status_code == 200
    first_payload = first_confirm.json()
    assert first_payload["batch"]["status"] == "CONFIRMED"
    assert len(first_payload["remittance_ids"]) >= 1

    second_confirm = client.post(
        f"{settings.API_V1_STR}/payment-batches/{batch_id}/confirm",
        headers={**superuser_token_headers, "Idempotency-Key": "phase4-key-1"},
    )
    assert second_confirm.status_code == 200
    second_payload = second_confirm.json()
    assert second_payload["batch"]["status"] == "CONFIRMED"
    assert second_payload["remittance_ids"] == first_payload["remittance_ids"]

    batch = db.exec(select(PaymentBatch).where(PaymentBatch.id == batch_id)).first()
    assert batch is not None
    assert batch.status == PaymentBatchStatus.CONFIRMED

    remittances = db.exec(
        select(Remittance).where(Remittance.payment_batch_id == batch_id)
    ).all()
    assert len(remittances) == 1

    updated_worklog = db.get(WorkLog, worklog.id)
    assert updated_worklog is not None
    assert updated_worklog.remittance_status == "REMITTED"


def test_confirm_payment_batch_with_multiple_freelancers(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    worklog_1 = create_random_worklog(
        db,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 31),
    )
    worklog_2 = create_random_worklog(
        db,
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 31),
    )
    add_time_entry(db, worklog_id=worklog_1.id, hours=2, hourly_rate=30)
    add_time_entry(db, worklog_id=worklog_2.id, hours=3, hourly_rate=40)

    create_response = client.post(
        f"{settings.API_V1_STR}/payment-batches/",
        headers=superuser_token_headers,
        json={"period_start": "2026-05-01", "period_end": "2026-05-31"},
    )
    batch_id = create_response.json()["id"]

    confirm_response = client.post(
        f"{settings.API_V1_STR}/payment-batches/{batch_id}/confirm",
        headers={**superuser_token_headers, "Idempotency-Key": "phase4-key-2"},
    )

    assert confirm_response.status_code == 200
    payload = confirm_response.json()
    assert payload["batch"]["status"] == "CONFIRMED"
    assert len(payload["remittance_ids"]) == 2

    remittances = db.exec(
        select(Remittance).where(Remittance.payment_batch_id == batch_id)
    ).all()
    assert len(remittances) == 2

    lines = db.exec(
        select(PaymentBatchWorkLog).where(
            PaymentBatchWorkLog.payment_batch_id == batch_id
        )
    ).all()
    assert len(lines) >= 2
    assert all(line.remittance_id is not None for line in lines)
