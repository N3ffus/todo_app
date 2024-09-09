from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.security import get_user_from_token, oauth2_scheme
from src.database import get_async_session
from src.todo.exceptions import AccessError, TaskNotFoundError
from src.todo.models import Task
from src.todo.schemas import TaskScheme
from src.todo.utils import (SortingEnum, StatusEnum, get_last_page,
                            get_pages_list)

router = APIRouter(
    prefix="/todos",
    tags=["Todo"],
    dependencies=[Depends(get_user_from_token), Depends(oauth2_scheme)],
)

templates = Jinja2Templates(directory="templates")


@router.post("/")
async def create_task(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    username: str = Depends(get_user_from_token),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.username == username)
    user = await session.scalar(stmt)

    new_task = Task(
        title=title,
        status=StatusEnum.not_started,
        description=description,
        author=user,
    )
    session.add(new_task)
    await session.commit()
    stmt = select(func.count()).select_from(Task).where(Task.user_id == user.id)
    length = await session.scalar(stmt)
    last_page = get_last_page(length, limit=10)
    return RedirectResponse(
        f"/todos?page={last_page}", status_code=status.HTTP_302_FOUND
    )


@router.post("/{task_id}")
async def update_task(
    task_id: int,
    title: Annotated[str, Form()],
    task_status: Annotated[StatusEnum, Form()],
    description: Annotated[str, Form()] = "",
    username: str = Depends(get_user_from_token),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.username == username)
    user = await session.scalar(stmt)

    task = await session.get(Task, task_id)

    if not task:
        raise TaskNotFoundError
    if task.user_id != user.id:
        raise AccessError

    task.title = title
    task.status = task_status
    task.description = description
    await session.commit()
    return RedirectResponse("/todos?page=1", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{task_id}")
async def delete_task(
    task_id: int,
    username: str = Depends(get_user_from_token),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.username == username)
    user = await session.scalar(stmt)

    stmt = select(Task).where(Task.id == task_id)
    task = await session.scalar(stmt)

    if not task:
        raise TaskNotFoundError
    if task.user_id != user.id:
        raise AccessError

    await session.delete(task)
    await session.commit()
    return RedirectResponse("/todos?page=1", status_code=status.HTTP_302_FOUND)


@router.get("/")
async def get_tasks(
    request: Request,
    page: int = 1,
    sorting: SortingEnum = SortingEnum.by_date,
    limit: int = 10,
    username: str = Depends(get_user_from_token),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.username == username)
    user = await session.scalar(stmt)

    if sorting == SortingEnum.by_date:
        stmt = (
            select(Task)
            .where(Task.user_id == user.id)
            .order_by(desc(Task.updated_at))
            .offset((page - 1) * limit)
            .limit(limit)
        )
    elif sorting == SortingEnum.by_title:
        stmt = (
            select(Task)
            .where(Task.user_id == user.id)
            .order_by("title")
            .offset((page - 1) * limit)
            .limit(limit)
        )
    elif sorting == SortingEnum.by_status:
        stmt = (
            select(Task)
            .where(Task.user_id == user.id)
            .order_by("status")
            .offset((page - 1) * limit)
            .limit(limit)
        )
    tasks = await session.scalars(stmt)
    stmt = select(func.count()).select_from(Task).where(Task.user_id == user.id)
    length = await session.scalar(stmt)
    data = []
    for task in tasks:
        data.append(task)
    pages = get_pages_list(length, page, limit)
    last_page = get_last_page(length, limit)

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": data,
            "page": page,
            "limit": limit,
            "total": len(data),
            "pages": pages,
            "current_page": page,
            "status": StatusEnum,
            "username": username,
            "last_page": last_page,
            "sorting": sorting,
            "sorts": SortingEnum,
        },
    )


@router.get("/{task_id}")
async def get_task(
    request: Request,
    task_id: int,
    username: str = Depends(get_user_from_token),
    session: AsyncSession = Depends(get_async_session),
):
    task = await session.get(Task, task_id)

    return templates.TemplateResponse(
        request=request,
        name="task.html",
        context={
            "task_id": task_id,
            "title": task.title,
            "description": task.description,
            "username": username,
            "task_status": task.status,
            "status": StatusEnum,
        },
    )
