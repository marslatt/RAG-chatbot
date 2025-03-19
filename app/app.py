from app.routers import ping_router, rag_router, chat_router
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request 
from services.service_provider import service_provider
from fastapi.staticfiles import StaticFiles  
from log import logger
from fastapi.responses import HTMLResponse, RedirectResponse 
from templates import templates
from starlette.exceptions import HTTPException as StarletteHTTPException

# https://fastapi.tiangolo.com/tutorial/bigger-applications
# https://fastapi.tiangolo.com/tutorial/dependencies
# https://fastapi.tiangolo.com/advanced/events/
# https://fastapi.tiangolo.com/tutorial/handling-errors
# https://stackoverflow.com/questions/77041522/fastapi-lifespan-event-in-docker-container-running-not-executing-the-shutdown

# Executed once at startup, before the application starts receiving requests. Useful for setting up resources 
# that are neccessary for the entire app, and that are shared among requests.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup lifespan routine.
    try:
        setup_service = service_provider.setup_service()
        setup_service.create_dirs()
        setup_service.validate_api_key() 
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
    # Clean up and release allocated resources.  # TODO 
    setup_service.delete_dirs()
    logger.info("Finished clean up of allocated resources. Application is shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAGChatbotApp",
        summary="A simple chatbot with RAG, using FastAPI, LangChain, ChromaDB.",
        version="0.0.1",
        lifespan=lifespan,
    ) 
    app.mount("/css", StaticFiles(directory="templates/css"), name="css")
    app.include_router(router=ping_router) 
    app.include_router(router=rag_router)
    app.include_router(router=chat_router)
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

@app.get("/")
async def root():
    return RedirectResponse(url="/chat")