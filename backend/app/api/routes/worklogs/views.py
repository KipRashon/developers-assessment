import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import SessionDep, get_current_active_superuser
from app.api.routes.worklogs.service import WorkLogService
from app.models import WorkLogDetailPublic, WorkLogFreelancersPublic, WorkLogsPublic

router = APIRouter(prefix="/worklogs", tags=["worklogs"])


@router.get(
    "/",
    response_model=WorkLogsPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_worklogs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    start_date: date | None = None,
    end_date: date | None = None,
    remittance_status: Annotated[str | None, Query(alias="remittanceStatus")] = None,
    freelancer_id: Annotated[uuid.UUID | None, Query(alias="freelancerId")] = None,
) -> WorkLogsPublic:
    """
    Retrieve worklogs with earned amounts.
    """
    return WorkLogService.get_worklogs(
        session=session,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        remittance_status=remittance_status,
        freelancer_id=freelancer_id,
    )


@router.get(
    "/freelancers",
    response_model=WorkLogFreelancersPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_worklog_freelancers(
    session: SessionDep,
    start_date: date | None = None,
    end_date: date | None = None,
    remittance_status: Annotated[str | None, Query(alias="remittanceStatus")] = None,
) -> WorkLogFreelancersPublic:
    """
    Retrieve freelancers available for the current worklog filters.
    """
    return WorkLogService.get_worklog_freelancers(
        session=session,
        start_date=start_date,
        end_date=end_date,
        remittance_status=remittance_status,
    )


@router.get(
    "/{worklog_id}",
    response_model=WorkLogDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def read_worklog_detail(
    session: SessionDep, worklog_id: uuid.UUID
) -> WorkLogDetailPublic:
    """
    Retrieve a worklog with individual time entries.
    """
    return WorkLogService.get_worklog_detail(session=session, worklog_id=worklog_id)
