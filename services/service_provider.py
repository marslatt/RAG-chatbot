from services.rag_service import RagService 
from services.setup_service import SetupService
from services.llm_service import LlmService

class ServiceProvider:
    '''
    Services dependency provider
    '''
    def __init__(self) -> None:
        self.__rag_service = RagService() 
        self.__setup_service = SetupService() 
        self.__llm_service = LlmService()

    def rag_service(self) -> RagService:
        return self.__rag_service   

    def setup_service(self) -> SetupService:
        return self.__setup_service

    def llm_service(self) -> LlmService:
        return self.__llm_service  

service_provider = ServiceProvider()
