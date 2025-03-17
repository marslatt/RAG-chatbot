''' 
from app.routers import ping_router, rag_router
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request  
from services.service_provider import service_provider
from fastapi.staticfiles import StaticFiles  
from log import logger
from fastapi.responses import HTMLResponse, RedirectResponse 
from templates import templates
from starlette.exceptions import HTTPException as StarletteHTTPException

# https://fastapi.tiangolo.com/tutorial/bigger-applications
# https://fastapi.tiangolo.com/tutorial/dependencies
# https://fastapi.tiangolo.com/advanced/events/
# https://fastapi.tiangolo.com/tutorial/handling-errors/#override-request-validation-exceptions
'''

from app.routers import ping_router, rag_router
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request 
from services.service_provider import service_provider
from fastapi.staticfiles import StaticFiles  
from log import logger
from fastapi.responses import HTMLResponse, RedirectResponse 
from templates import templates
from starlette.exceptions import HTTPException as StarletteHTTPException

# https://fastapi.tiangolo.com/tutorial/bigger-applications
# https://fastapi.tiangolo.com/tutorial/dependencies
# https://fastapi.tiangolo.com/advanced/events/
# https://stackoverflow.com/questions/77041522/fastapi-lifespan-event-in-docker-container-running-not-executing-the-shutdown

# Executed once at startup, before the application starts receiving requests. Useful for setting up resources 
# that are neccessary for the entire app, and that are shared among requests.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup lifespan routine.
    try:
        rag_service = service_provider.rag_service()
        rag_service.configure_db()
        llm_service = service_provider.llm_service()
        llm_service.configure_llm(rag_service.get_retriever())
    except Exception as e:
        err = f"Error occured while creating FastAPI app: {str(e)}"
        logger.error(err)
        raise HTTPException(
            status_code=500, # 500 Internal Server Error
            detail=err,
        )
    yield
    # Clean up and release the resources.  
    setup_service = service_provider.setup_service()
    setup_service.delete_dirs()
    logger.info("Finished cleaning all allocated resources. Application in shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAGChatbotApp",
        summary="A simple chatbot with RAG, using FastAPI, LangChain and OpenAI.",
        version="0.0.1",
        lifespan=lifespan,
    ) 

    app.mount("/css", StaticFiles(directory="templates/css"), name="css")
    app.include_router(router=ping_router) 
    app.include_router(router=rag_router)
    return app

app = create_app() 

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    e: Exception,
    )-> HTMLResponse:
    err = f"{str(request.url)} - {str(e)}"
    logger.error(err)  
    return templates.TemplateResponse(
            request=request, 
            status_code=404, # 404 Not Found
            name="error.html", 
            context={"message": str(e)} 
        )     
 