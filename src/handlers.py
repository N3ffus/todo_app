from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


async def handler404(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        status_code=404,
    )


async def handler403(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="errors/403.html",
        status_code=403,
    )


async def handler401(request: Request, exc: HTTPException):
    return RedirectResponse("/login", status_code=302)
