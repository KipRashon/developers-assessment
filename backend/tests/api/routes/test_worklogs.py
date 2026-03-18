import uuid
from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.worklog import add_time_entry, create_random_worklog


def test_read_worklogs(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    worklog = create_random_worklog(db)
    add_time_entry(db, worklog_id=worklog.id, hours=2, hourly_rate=50)
    add_time_entry(db, worklog_id=worklog.id, hours=1, hourly_rate=30, is_excluded=True)

    response = client.get(
        f"{settings.API_V1_STR}/worklogs/",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["count"] >= 1
    row = next(
        (item for item in content["data"] if item["id"] == str(worklog.id)), None
    )
    assert row is not None
    assert row["earned_amount"] == 100
    assert row["freelancer_name"]


def test_read_worklogs_filter_date_range(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    in_range = create_random_worklog(
        db,
        period_start=date(2026, 2, 1),
        period_end=date(2026, 2, 28),
    )
    add_time_entry(db, worklog_id=in_range.id, hours=2, hourly_rate=50)

    out_of_range = create_random_worklog(
        db,
        period_start=date(2026, 3, 1),
        period_end=date(2026, 3, 31),
    )
    add_time_entry(db, worklog_id=out_of_range.id, hours=2, hourly_rate=50)

    response = client.get(
        f"{settings.API_V1_STR}/worklogs/?start_date=2026-02-01&end_date=2026-02-28",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["data"]}
    assert str(in_range.id) in ids
    assert str(out_of_range.id) not in ids


def test_read_worklogs_filter_remittance_status(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    remitted = create_random_worklog(db, remittance_status="REMITTED")
    add_time_entry(db, worklog_id=remitted.id, hours=1, hourly_rate=80)

    unremitted = create_random_worklog(db, remittance_status="UNREMITTED")
    add_time_entry(db, worklog_id=unremitted.id, hours=1, hourly_rate=80)

    response = client.get(
        f"{settings.API_V1_STR}/worklogs/?remittanceStatus=REMITTED",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["data"]}
    assert str(remitted.id) in ids
    assert str(unremitted.id) not in ids


def test_read_worklogs_filter_freelancer(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    first = create_random_worklog(db)
    add_time_entry(db, worklog_id=first.id, hours=1, hourly_rate=80)

    second = create_random_worklog(db)
    add_time_entry(db, worklog_id=second.id, hours=1, hourly_rate=80)

    response = client.get(
        f"{settings.API_V1_STR}/worklogs/?freelancerId={first.freelancer_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["data"]}
    assert str(first.id) in ids
    assert str(second.id) not in ids


def test_read_worklog_freelancers(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    first = create_random_worklog(
        db,
        period_start=date(2026, 6, 1),
        period_end=date(2026, 6, 30),
    )
    add_time_entry(db, worklog_id=first.id, hours=1, hourly_rate=50)

    second = create_random_worklog(
        db,
        period_start=date(2026, 6, 1),
        period_end=date(2026, 6, 30),
    )
    add_time_entry(db, worklog_id=second.id, hours=1, hourly_rate=60)

    response = client.get(
        f"{settings.API_V1_STR}/worklogs/freelancers?start_date=2026-06-01&end_date=2026-06-30&remittanceStatus=UNREMITTED",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    ids = {item["id"] for item in content["data"]}
    assert str(first.freelancer_id) in ids
    assert str(second.freelancer_id) in ids
    assert content["count"] >= 2


def test_read_worklogs_invalid_date_range(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/worklogs/?start_date=2026-04-02&end_date=2026-04-01",
        headers=superuser_token_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid date range"


def test_read_worklog_detail(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    worklog = create_random_worklog(db)
    entry = add_time_entry(db, worklog_id=worklog.id, hours=3, hourly_rate=40)

    response = client.get(
        f"{settings.API_V1_STR}/worklogs/{worklog.id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(worklog.id)
    assert content["earned_amount"] == 120
    assert content["freelancer_name"]
    assert len(content["time_entries"]) == 1
    assert content["time_entries"][0]["id"] == str(entry.id)


def test_read_worklog_detail_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/worklogs/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Worklog not found"


def test_read_worklogs_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    worklog = create_random_worklog(db)
    add_time_entry(db, worklog_id=worklog.id, hours=2, hourly_rate=50)

    response = client.get(
        f"{settings.API_V1_STR}/worklogs/",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The user doesn't have enough privileges"
