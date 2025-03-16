from fastapi import APIRouter, Request 
from log import logger
from fastapi import HTTPException 
# from schema import BaseResponse 
from fastapi.responses import HTMLResponse
from templates import templates
from datetime import datetime  

ping_router = APIRouter() 
 
@ping_router.get(path="/ping", response_class=HTMLResponse)
async def ping(
    request: Request 
) -> HTMLResponse:
    try:
        title = request.app.title
        version = request.app.version 
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    except Exception as e: 
        err = str(e)
        logger.error(f"Error occured while uploading document: {err}")
        raise HTTPException(
            status_code=500,
            detail=err,
        ) 
    return templates.TemplateResponse(
        request=request, 
        name="ping.html", 
        context={"title": title, "version": version, "timestamp" : timestamp}
    )

# TODO Pydantic validation
# @ping_router.get(path="/ping", response_model=BaseResponse)
# https://dev.to/jamesbmour/part-3-pydantic-data-models-4gnb

