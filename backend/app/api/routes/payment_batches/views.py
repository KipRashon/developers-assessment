import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.api.routes.payment_batches.service import PaymentBatchService
from app.models import (
    PaymentBatchConfirmResult,
    PaymentBatchCreate,
    PaymentBatchExclusionUpdate,
    PaymentBatchReview,
    PaymentBatchSummary,
)

router = APIRouter(prefix="/payment-batches", tags=["payment-batches"])


@router.post(
    "/",
    response_model=PaymentBatchSummary,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_payment_batch(
    session: SessionDep,
    current_user: CurrentUser,
    batch_in: PaymentBatchCreate,
) -> PaymentBatchSummary:
    """
    Create a draft payment batch from eligible worklogs.
    """
    return PaymentBatchService.create_batch(session, current_user, batch_in)


@router.get(
    "/{batch_id}",
    response_model=PaymentBatchSummary,
    dependencies=[Depends(get_current_active_superuser)],
)
def get_payment_batch(session: SessionDep, batch_id: uuid.UUID) -> PaymentBatchSummary:
    """
    Fetch a payment batch summary.
    """
    return PaymentBatchService.get_batch(session, batch_id)


@router.put(
    "/{batch_id}/exclusions",
    response_model=PaymentBatchSummary,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_payment_batch_exclusions(
    session: SessionDep,
    current_user: CurrentUser,
    batch_id: uuid.UUID,
    exclusion_in: PaymentBatchExclusionUpdate,
) -> PaymentBatchSummary:
    """
    Update excluded worklogs and freelancers for a draft batch.
    """
    return PaymentBatchService.update_exclusions(
        session, current_user, batch_id, exclusion_in
    )


@router.get(
    "/{batch_id}/review",
    response_model=PaymentBatchReview,
    dependencies=[Depends(get_current_active_superuser)],
)
def review_payment_batch(
    session: SessionDep, batch_id: uuid.UUID
) -> PaymentBatchReview:
    """
    Review included and excluded worklogs before confirmation.
    """
    return PaymentBatchService.review_batch(session, batch_id)


@router.post(
    "/{batch_id}/confirm",
    response_model=PaymentBatchConfirmResult,
    dependencies=[Depends(get_current_active_superuser)],
)
def confirm_payment_batch(
    session: SessionDep,
    current_user: CurrentUser,
    batch_id: uuid.UUID,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> PaymentBatchConfirmResult:
    """
    Confirm a draft payment batch and generate remittances.
    """
    return PaymentBatchService.confirm_batch(
        session, current_user, batch_id, idempotency_key
    )


@router.post(
    "/{batch_id}/cancel",
    response_model=PaymentBatchSummary,
    dependencies=[Depends(get_current_active_superuser)],
)
def cancel_payment_batch(
    session: SessionDep,
    current_user: CurrentUser,
    batch_id: uuid.UUID,
) -> PaymentBatchSummary:
    """
    Cancel a draft payment batch.
    """
    return PaymentBatchService.cancel_batch(session, current_user, batch_id)
