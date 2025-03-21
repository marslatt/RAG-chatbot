from fastapi import Depends
from fastapi.routing import APIRouter, Request
from log.logger import logger
from services import service_provider 
from services.llm_service import LlmService 
from services.rag_service import RagService 
from fastapi.responses import JSONResponse 
from fastapi.responses import HTMLResponse  
from templates import templates
from typing import Dict

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

# TODO Add Pydantic data class
@chat_router.post("/send") 
async def send(
    data: Dict[str, str],
    request: Request,
    llm_service: LlmService = Depends(service_provider.llm_service),
) -> JSONResponse:
    try:
        received_text = data.get("text", "")
        if not received_text:
            raise Exception("No text provided or the text is empty.")    
        ai_msg = await llm_service.generate_answer(received_text)
        return JSONResponse(status_code=200, content={"message": ai_msg}) 
    except Exception as e:
        err = f"Error occured while generating response: {str(e)}"
        logger.error(err)
        return JSONResponse(status_code=422, content={"error": err}) # 422 Unprocessable Content  

@chat_router.delete('/delete')
async def delete(
    request: Request,    
    llm_service: LlmService = Depends(service_provider.llm_service),
    rag_service: RagService = Depends(service_provider.rag_service),
) -> JSONResponse:    
    try:
        llm_service.delete_history()
        rag_service.delete_docs()
        return JSONResponse(status_code=200, content={"message": "History successfully deleted."})  # 200 OK
    except Exception as e:
        err = f"Error occured while deleting history: {str(e)}"
        logger.error(err)
        return JSONResponse(status_code=400, content={"error": err})  # 400 Bad Request
