from services.rag_service import RagService 
from services.setup_service import SetupService
from services.chat_service import ChatService
from services.ocr_service import OcrService

class ServiceProvider:
    '''
    Services dependency provider
    '''
    def __init__(self) -> None:
        self.__setup_service = SetupService() 
        self.__ocr_service = OcrService() 
        self.__rag_service = RagService()
        self.__chat_service = ChatService()        
        self._config_services()

    def _config_services(self): 
        self.__setup_service.configure()
        self.__ocr_service.configure()
        self.__rag_service.configure(self.__ocr_service)  
        self.__chat_service.configure(self.__rag_service) 

    def setup_service(self) -> SetupService:
        return self.__setup_service
    
    def ocr_service(self) -> OcrService:
        return self.__ocr_service      
    
    def rag_service(self) -> RagService:          
        return self.__rag_service 

    def chat_service(self) -> ChatService:
        return self.__chat_service  

service_provider = ServiceProvider()
