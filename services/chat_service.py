from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate 
from services.rag_service import RagService 
from config.constants import OPENAI_API_KEY, OPENAI_LLM
from fastapi import HTTPException 
from log import logger
import re

# https://python.langchain.com/v0.2/docs/how_to/qa_chat_history_how_to/
# https://python.langchain.com/docs/concepts/async/
# https://www.baeldung.com/cs/langchain-text-summarize

PDFNAME = r'^[\w,\s-]+\.[Pp][Dd][Ff]$'

class ChatService:  
    '''
    Service for performing history-aware QA and summarization tasks with LLM
    '''
    def __init__(self):
        self._llm = None
        self._qa_chain = None
        self._summ_chain = None
        self._parse_chain = None
        self._chat_history = []   
        self._rag_service = None

    def _create_qa_chain(self):
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
        contextualized_retriever = create_history_aware_retriever(self._llm, self._rag_service.get_retriever(), contextualized_prompt)

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
        document_chain = create_stuff_documents_chain(self._llm, qa_prompt)

        # Create retrieval chain that retrieves documents and then passes them on. 
        self._chain = create_retrieval_chain(contextualized_retriever, document_chain)

    def _create_summary_chain(self):
        '''
        Create chain for text summarization of list of documents.
        '''         
        map_prompt = PromptTemplate(
            input_variables=["text"],
            template=(
                "You are a precise summarization assistant. " 
                "Summarize the following content:\n\n{text}\n\n"  
                "Do NOT add information that is not explicitly provided in the text. "  
                "Preserve all names, dates, places, and numbers exactly as written. "
                "Do NOT paraphrase proper nouns of people, organizations, locations, etc. "
                "If details are unclear, omit them rather than inventing. "
                "Keep the meaning faithful to the original text. "
                "Maintain neutrality — do not add opinions or interpretations." 
            )
        )

        combine_prompt = PromptTemplate(
            input_variables=["text"],
            template=(
                "You are a precise summarization assistant.\n\n"  
                "Combine the following summaries into one coherent summary:\n\n{text}\n\n"  
                "Do NOT add information that is not explicitly provided in the text. "  
                "Keep ALL factual details from the input summaries.\n"
                "Preserve all names, dates, places, and numbers exactly as written.\n"
                "Do NOT paraphrase proper nouns of people, organizations, locations, etc.\n"
                "Merge overlapping points without losing detail.\n"
                "Keep the meaning faithful to the original text and ensure clarity and logical order."
            )
        )
 
        self._summ_chain = load_summarize_chain(
            self._llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True
        ) 

    def _create_parse_chain(self):
        """
        Create a history-aware chain that extracts a filename if the user wants to summarize a document.
        """ 
        parse_sys_prompt = (
            "You are an assistant that extracts filenames only when explicitly mentioned.\n\n"
            "Check if the user query requires summarization of a document.\n\n"
            "If true, extract a document filename ONLY if the user explicitly mentions one.\n"
            "Do not guess, infer, or hallucinate any filenames.\n"
            "If the user input does not clearly contain a filename, respond exactly with: name not found.\n\n"
            "Rules:\n"
            "1. If a filename is mentioned, return ONLY that filename (nothing else).\n"
            "2. A valid filename must come directly from the user input.\n"
            "3. If the filename has no extension, append .pdf.\n"
            "4. If no filename is in the input, return 'name not found'.\n"
            "5. If the user does not require summarization, return 'not for summary'."
        )
 
        parse_prompt = ChatPromptTemplate.from_messages([
            ("system", parse_sys_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}")   
        ])
 
        self._parse_chain = LLMChain(
            llm=self._llm,
            prompt=parse_prompt,
            output_key="filename"
        ) 

    def configure(self, rag_service: RagService):
        self._llm = ChatOpenAI(
            model=OPENAI_LLM,
            openai_api_key=OPENAI_API_KEY,
            temperature=0
        )
        self._rag_service = rag_service
        self._create_qa_chain()   
        self._create_summary_chain()  
        self._create_parse_chain()      
        logger.info("History-aware chat service for QA and summarization configured.")      

    def get_history(self) -> list: 
        return self._chat_history 
    
    def delete_history(self): 
        self._chat_history = [] 
  

    async def generate_answer(self, user_input) -> str:
        '''
        Generate response based on previous chat history and user input.
        '''
        try:            
            #result = await self._llm.ainvoke(self._parse_prompt.format(user_input=user_input))
            result = await self._parse_chain.ainvoke({
                "input": user_input,
                "chat_history": self._chat_history
            })
            parsed_input = result["filename"].strip()
            logger.info(f"Response after parsing \"{user_input}\": {parsed_input}") 
 
            # Summarization request    
            if bool(re.match(PDFNAME, parsed_input)):
                docs = self._rag_service.extract_doc(parsed_input) 
                if docs:
                    result = await self._summ_chain.ainvoke(
                        { "input_documents": docs }  # summarization chain's variable is always input_documents
                    ) 
                    answer = result["output_text"]   # summarization chain return {"output_text": "..."} 
                else:
                    answer = "Provided document was not found in the database. Ensure it is uploaded correctly!"                       
            
            # Handle QA chat
            else: 
                result = await self._chain.ainvoke({
                    "chat_history": self._chat_history, 
                    "input": user_input 
                })
                answer = result['answer'] 

            self._chat_history.append(("user", user_input)) 
            self._chat_history.append(("ai", answer))
            return answer
        except Exception as e:  
            err =  f"Error occured while generating response: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )      
      