from fastapi import HTTPException, status


class TaskNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            detail="No task with this id found", status_code=status.HTTP_404_NOT_FOUND
        )


class AccessError(HTTPException):
    def __init__(self):
        super().__init__(
            detail="You don't have permission to edit this task",
            status_code=status.HTTP_403_FORBIDDEN,
        )
