"""
Task management.
- Admin: create tasks, assign to a user, view all tasks.
- User: view own tasks, update status pending -> completed.
- GET /tasks supports dynamic filtering via ?status= and ?assigned_to=
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_role, get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskOut, TaskStatusUpdate
from app.services.task_service import create_task, list_tasks, update_task_status
from app.services.activity_service import log_activity

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=201)
def create_task_route(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    assignee = db.query(User).filter(User.id == payload.assigned_to).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assigned user not found")

    task = create_task(
        db,
        title=payload.title,
        description=payload.description,
        assigned_to=payload.assigned_to,
        created_by=current_user.id,
    )
    log_activity(db, current_user.id, "TASK_CREATE", f"Created task #{task.id} for user #{assignee.id}")
    return task


@router.get("", response_model=list[TaskOut])
def get_tasks(
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dynamic filtering: /tasks?status=completed  /tasks?assigned_to=1
    Regular users are always scoped to their own tasks regardless of the
    assigned_to filter, to prevent viewing others' tasks.
    """
    if current_user.role.name != "admin":
        assigned_to = current_user.id

    return list_tasks(db, status=status, assigned_to=assigned_to)


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role.name != "admin" and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own tasks")

    updated = update_task_status(db, task, payload.status)
    log_activity(db, current_user.id, "TASK_UPDATE", f"Task #{task.id} -> {payload.status.value}")
    return updated
