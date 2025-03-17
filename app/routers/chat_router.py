from fastapi import Depends
from fastapi.routing import APIRouter, Request
from log.logger import logger
from services import service_provider 
from services.llm_service import LlmService 
from fastapi.responses import JSONResponse 
from fastapi.responses import HTMLResponse  
from templates import templates
import os

chat_router = APIRouter()  
  
@chat_router.get("/chat", response_class=HTMLResponse)
async def chat( 
    request: Request,
    llm_service: LlmService = Depends(service_provider.llm_service), 
    ) -> HTMLResponse:
    history = llm_service.get_history() 
    return templates.TemplateResponse(
        request=request, 
        name="chat.html",
        context={"history":history}  
    )  

@chat_router.post("/send") 
async def send(
    request: Request,
    llm_service: LlmService = Depends(service_provider.llm_service),
    ) -> JSONResponse:
    pass