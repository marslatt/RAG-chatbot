from app.routers import ping_router
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI

# https://fastapi.tiangolo.com/tutorial/bigger-applications
# https://fastapi.tiangolo.com/tutorial/dependencies
# https://fastapi.tiangolo.com/advanced/events/

# executed once at startup, before the application starts receiving requests
# useful for setting up resources that you need to use for the whole app, and that are shared among requests
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup lifespan routine
    yield
    # Clean up  and release the resources     

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAGChatbotApp",
        summary="A simple chatbot with RAG, using FastAPI, LangChain and OpenAI.",
        version="0.0.1",
        lifespan=lifespan,
    ) 

    app.include_router(router=ping_router) 

    return app

app = create_app()    