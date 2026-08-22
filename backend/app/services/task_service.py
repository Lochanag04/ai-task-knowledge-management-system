"""
Task management queries, including the dynamic filtering used by
GET /tasks.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus


def create_task(db: Session, title: str, description: str | None, assigned_to: int, created_by: int) -> Task:
    task = Task(
        title=title,
        description=description,
        assigned_to=assigned_to,
        created_by=created_by,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
) -> list[Task]:
    query = db.query(Task)
    if status is not None:
        query = query.filter(Task.status == status)
    if assigned_to is not None:
        query = query.filter(Task.assigned_to == assigned_to)
    return query.order_by(Task.created_at.desc()).all()


def update_task_status(db: Session, task: Task, status: TaskStatus) -> Task:
    task.status = status
    db.commit()
    db.refresh(task)
    return task
