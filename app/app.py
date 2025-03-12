from app.routers import ping_router, data_router
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException 
from services.service_provider import service_provider, LlmService, RagService
from log import logger

# https://fastapi.tiangolo.com/tutorial/bigger-applications
# https://fastapi.tiangolo.com/tutorial/dependencies
# https://fastapi.tiangolo.com/advanced/events/

# Executed once at startup, before the application starts receiving requests. Useful for setting up resources 
# that are neccessary for the entire app, and that are shared among requests.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup lifespan routine.
    try:
        rag_service: RagService = service_provider.rag_service()
        rag_service.configure_db()
        llm_service: LlmService = service_provider.llm_service()
        llm_service.configure_llm(rag_service.get_retriever())
    except Exception as e:
        err = f"Error occured while creating FastAPI app: {str(e)}"
        logger.error(err)
        raise HTTPException(
        status_code=500,
        detail=err,
        )
    yield
    # Clean up and release the resources.  
    # TODO: delete db collection and files   

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAGChatbotApp",
        summary="A simple chatbot with RAG, using FastAPI, LangChain and OpenAI.",
        version="0.0.1",
        lifespan=lifespan,
    ) 

    app.include_router(router=ping_router) 
    app.include_router(router=data_router)
    return app

app = create_app()    