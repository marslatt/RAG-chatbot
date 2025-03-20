from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain.vectorstores.base import VectorStoreRetriever
from config.constants import OPENAI_API_KEY, OPENAI_LLM
from log import logger

# https://python.langchain.com/v0.2/docs/how_to/qa_chat_history_how_to/
# https://python.langchain.com/docs/concepts/async/

class LlmService:  
    '''
    Service for performing history-aware QA tasks with LLM
    '''
    def __init__(self):
        self.llm = None
        self.chain = None
        self.chat_history = []   

    def _create_chain(self, retriever: VectorStoreRetriever):
        '''
        Create conversational history-aware retrieval chain
        '''
        cntx_sys_prompt = "Given a chat history and the latest user question " \
                          "which might reference context in the chat history, " \
                          "formulate a standalone question which can be understood " \
                          "without the chat history. Do NOT answer the question, " \
                          "just reformulate it if needed and otherwise return it as is."
        contextualized_prompt = ChatPromptTemplate.from_messages([
            ("system", cntx_sys_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create a chain that takes conversation history and returns documents. If there is no history, the input is just passed directly  
        # to the retriever. If there is history, the prompt and LLM will be used to generate a search query to be passed to the retriever.
        contextualized_retriever = create_history_aware_retriever(self.llm, retriever, contextualized_prompt)

        qa_sys_prompt = "You are an assistant for question-answering tasks. " \
                        "Use the following pieces of retrieved context to answer " \
                        "the question. If you don't know the answer, say that you " \
                        "don't know. Use three sentences maximum and keep the " \
                        "answer concise.\n\n{context}"
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_sys_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create a chain for passing a list of documents to the LLM model.
        document_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        # Create retrieval chain that retrieves documents and then passes them on. 
        self.chain = create_retrieval_chain(contextualized_retriever, document_chain)

    def configure_llm(self, retriever: VectorStoreRetriever):
        self.llm = ChatOpenAI(
            model=OPENAI_LLM,
            openai_api_key=OPENAI_API_KEY
        )
        self._create_chain(retriever)   
        logger.info("LLM initialized and retrieval chain configured.")      

    def get_history(self) -> list: 
        return self.chat_history 
    
    def delete_history(self): 
        self.chat_history = []
        # TODO Delete Chroma collection of uploaded files too

    async def generate_answer(self, user_input) -> str:
        '''
        Generate response based on previous chat history and user input.
        '''
        response = await self.chain.ainvoke(
            {
                "chat_history": self.chat_history,
                "input": user_input
            }
        )
        answer = response['answer']
        self.chat_history.append(("user", user_input))
        self.chat_history.append(("ai", answer))
        return answer    
      