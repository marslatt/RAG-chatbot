from fastapi import APIRouter, Request 
from log import logger
from fastapi import HTTPException 
from schema import BaseResponse 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

templates = Jinja2Templates(directory="templates")

ping_router = APIRouter() 

''' 
@ping_router.get(path="/ping", response_model=BaseResponse)
async def ping(
    request: Request 
) -> BaseResponse:
    try:
        response = f"{request.app.title} - v.{request.app.version}" 
    except Exception as e: 
            err = f"Request cannot be completed: {str(e)}"
            logger.error(err)
            raise HTTPException(
            status_code=500,
            detail=err,
        )  
    return BaseResponse(data=response)  


response_model=HTMLResponse:
fastapi.exceptions.FastAPIError: Invalid args for response field! Hint: check that <class 'starlette.responses.HTMLResponse'> is a valid Pydantic 
field type. If you are using a return type annotation that is not a valid Pydantic field (e.g. Union[Response, dict, None]) you can disable 
generating the response model from the type annotation with the path operation decorator parameter response_model=None. 
Read more: https://fastapi.tiangolo.com/tutorial/response-model/
'''

@ping_router.get(path="/ping/", response_class=HTMLResponse)
async def htmlping(
    request: Request 
) -> HTMLResponse:
    title = request.app.title
    version = request.app.version 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    return templates.TemplateResponse(
        request=request, 
        name="ping.html", 
        context={"title": title, "version": version, "timestamp" : timestamp}
    )

 