import uuid
from datetime import date, datetime, timezone
from enum import Enum

from pydantic import EmailStr
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    worklogs: list["WorkLog"] = Relationship(
        back_populates="freelancer", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


class WorkLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_name: str = Field(min_length=1, max_length=255)
    freelancer_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    period_start: date = Field(index=True)
    period_end: date = Field(index=True)
    remittance_status: str = Field(default="UNREMITTED", max_length=20, index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)

    freelancer: User | None = Relationship(back_populates="worklogs")
    time_entries: list["TimeEntry"] = Relationship(
        back_populates="worklog", cascade_delete=True
    )


class TimeEntry(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", nullable=False, ondelete="CASCADE", index=True
    )
    started_at: datetime = Field(nullable=False, index=True)
    ended_at: datetime = Field(nullable=False, index=True)
    hours: float = Field(default=0)
    hourly_rate: float = Field(default=0)
    is_excluded: bool = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)

    worklog: WorkLog | None = Relationship(back_populates="time_entries")


class WorkLogListItemPublic(SQLModel):
    id: uuid.UUID
    task_name: str
    freelancer_id: uuid.UUID
    freelancer_name: str
    period_start: date
    period_end: date
    remittance_status: str
    earned_amount: float


class WorkLogsPublic(SQLModel):
    data: list[WorkLogListItemPublic]
    count: int


class WorkLogFreelancerFilterOptionPublic(SQLModel):
    id: uuid.UUID
    name: str


class WorkLogFreelancersPublic(SQLModel):
    data: list[WorkLogFreelancerFilterOptionPublic]
    count: int


class TimeEntryPublic(SQLModel):
    id: uuid.UUID
    worklog_id: uuid.UUID
    started_at: datetime
    ended_at: datetime
    hours: float
    hourly_rate: float
    is_excluded: bool


class WorkLogDetailPublic(SQLModel):
    id: uuid.UUID
    task_name: str
    freelancer_id: uuid.UUID
    freelancer_name: str
    period_start: date
    period_end: date
    remittance_status: str
    earned_amount: float
    time_entries: list[TimeEntryPublic]


class PaymentBatchStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BatchLineInclusionStatus(str, Enum):
    INCLUDED = "INCLUDED"
    EXCLUDED_WORKLOG = "EXCLUDED_WORKLOG"
    EXCLUDED_FREELANCER = "EXCLUDED_FREELANCER"


class RemittanceStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentBatch(SQLModel, table=True):
    __tablename__ = "payment_batch"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    period_start: date = Field(index=True)
    period_end: date = Field(index=True)
    status: PaymentBatchStatus = Field(default=PaymentBatchStatus.DRAFT, index=True)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    created_by_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL", index=True
    )
    confirmed_by_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL", index=True
    )
    idempotency_key: str | None = Field(default=None, max_length=255, index=True)
    error_message: str | None = Field(default=None, max_length=255)
    confirmed_at: datetime | None = Field(default=None)
    total_amount_snapshot: float = Field(default=0)
    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now)

    payment_batch_worklogs: list["PaymentBatchWorkLog"] = Relationship(
        back_populates="payment_batch", cascade_delete=True
    )
    remittances: list["Remittance"] = Relationship(
        back_populates="payment_batch", cascade_delete=True
    )


class PaymentBatchWorkLog(SQLModel, table=True):
    __tablename__ = "payment_batch_worklog"
    __table_args__ = (UniqueConstraint("payment_batch_id", "worklog_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    payment_batch_id: uuid.UUID = Field(
        foreign_key="payment_batch.id", nullable=False, ondelete="CASCADE", index=True
    )
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", nullable=False, ondelete="RESTRICT", index=True
    )
    freelancer_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="RESTRICT", index=True
    )
    inclusion_status: BatchLineInclusionStatus = Field(
        default=BatchLineInclusionStatus.INCLUDED, index=True
    )
    exclusion_reason: str | None = Field(default=None, max_length=255)
    excluded_at: datetime | None = Field(default=None)
    excluded_by_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL", index=True
    )
    amount_snapshot: float = Field(default=0)
    total_minutes_snapshot: int = Field(default=0, ge=0)
    remittance_id: uuid.UUID | None = Field(
        default=None, foreign_key="remittance.id", ondelete="SET NULL", index=True
    )
    created_at: datetime = Field(default_factory=utc_now, index=True)

    payment_batch: PaymentBatch | None = Relationship(
        back_populates="payment_batch_worklogs"
    )
    worklog: WorkLog | None = Relationship()


class Remittance(SQLModel, table=True):
    __tablename__ = "remittance"
    __table_args__ = (UniqueConstraint("payment_batch_id", "freelancer_id"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    payment_batch_id: uuid.UUID = Field(
        foreign_key="payment_batch.id", nullable=False, ondelete="CASCADE", index=True
    )
    freelancer_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="RESTRICT", index=True
    )
    status: RemittanceStatus = Field(default=RemittanceStatus.PENDING, index=True)
    amount: float = Field(default=0)
    external_reference: str | None = Field(default=None, max_length=128)
    failure_reason: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now)

    payment_batch: PaymentBatch | None = Relationship(back_populates="remittances")


class PaymentBatchCreate(SQLModel):
    period_start: date
    period_end: date
    currency: str = Field(default="USD", min_length=3, max_length=3)


class PaymentBatchExclusionUpdate(SQLModel):
    excluded_worklog_ids: list[uuid.UUID] = Field(default_factory=list)
    excluded_freelancer_ids: list[uuid.UUID] = Field(default_factory=list)
    reason: str | None = Field(default=None, max_length=255)


class PaymentBatchWorkLogPublic(SQLModel):
    id: uuid.UUID
    worklog_id: uuid.UUID
    freelancer_id: uuid.UUID
    freelancer_name: str
    inclusion_status: BatchLineInclusionStatus
    exclusion_reason: str | None
    amount_snapshot: float
    total_minutes_snapshot: int
    remittance_id: uuid.UUID | None


class PaymentBatchSummary(SQLModel):
    id: uuid.UUID
    period_start: date
    period_end: date
    status: PaymentBatchStatus
    currency: str
    created_by_id: uuid.UUID | None
    confirmed_by_id: uuid.UUID | None
    idempotency_key: str | None
    error_message: str | None
    confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    included_count: int
    excluded_count: int
    gross_total: float
    net_total: float


class PaymentBatchReview(SQLModel):
    batch: PaymentBatchSummary
    included_worklogs: list[PaymentBatchWorkLogPublic]
    excluded_worklogs: list[PaymentBatchWorkLogPublic]


class PaymentBatchConfirmResult(SQLModel):
    batch: PaymentBatchSummary
    remittance_ids: list[uuid.UUID]


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
