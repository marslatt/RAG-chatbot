from fastapi import Depends
from fastapi.routing import APIRouter, Request
from log.logger import logger
from services import service_provider 
from services.llm_service import LlmService 
from fastapi.responses import JSONResponse 
from fastapi.responses import HTMLResponse  
from templates import templates
from typing import Dict
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
    data: Dict[str, str],
    request: Request,
    llm_service: LlmService = Depends(service_provider.llm_service),
    ) -> JSONResponse: 
    # TODO 
    received_text = data.get("text", "")
    if not received_text:
        return JSONResponse(
            content={"message": "No text provided or the text is empty."}, 
            status_code=400
        )

    return JSONResponse(status_code=200, content={"message": "AI message"}) 