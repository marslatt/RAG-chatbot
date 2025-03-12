from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain.vectorstores.base import VectorStoreRetriever
from config.constants import OPENAI_API_KEY, OPENAI_LLM

# https://python.langchain.com/docs/concepts/async/

class LlmService:  
    '''
    Service for performing history-aware QA tasks with LLM
    '''
    def __init__(self):
        self.llm = None
        self.chain = None
        self.chat_history = []

    # TODO Move chain and history to ./chains/history_chain.py    

    def _create_chain(self, retriever: VectorStoreRetriever):
        '''
        Create conversational history-aware retrieval chain
        '''
        contextualized_prompt = ChatPromptTemplate.from_messages([
            ("system", "Based on chat history and user question, make the question understandable without history."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        # Create a chain that takes conversation history and returns documents. If there is no history, the input is just passed directly  
        # to the retriever. If there is history, the prompt and LLM will be used to generate a search query to be passed to the retriever.
        contextualized_retriever = create_history_aware_retriever(self.llm, retriever, contextualized_prompt)

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the user question based on the below context:\\n\\n{context}"),
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
        self.chain = self._create_chain(retriever)

    def generate_response(self, user_input):
        '''
        Generate response based on previous chat history and user input.
        '''
        response = self.chain.ainvoke(
            {
                "chat_history": self.chat_history,
                "input": user_input
            }
        )
        # TODO
        '''
        await run_in_executor(
            None, self.transform_documents, documents, **kwargs
        )
        '''

        answer = response['answer']
        self.chat_history.append("user", f"{user_input}")
        self.chat_history.append("ai", f"{answer}")
        return answer    
      