from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.auth.router import router as auth_router
from src.auth.security import is_authorized
from src.handlers import handler401, handler403, handler404
from src.todo.models import Task
from src.todo.router import router as todo_router
from src.todo.utils import StatusEnum

app = FastAPI(title="TodoApp")


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


app.include_router(auth_router)
app.include_router(todo_router)

app.add_exception_handler(404, handler404)
app.add_exception_handler(403, handler403)
app.add_exception_handler(401, handler401)
app.add_exception_handler(405, handler404)


@app.get("/")
async def main(request: Request):
    username = is_authorized(request)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"username": username},
    )


@app.get("/login")
async def login_page(request: Request):
    if is_authorized(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
    )


@app.get("/register")
async def register_page(request: Request):
    if is_authorized(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
    )
