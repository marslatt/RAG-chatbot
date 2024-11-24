from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
# from chromadb.utils.embedding_functions import HuggingFaceEmbeddingFunction
# from langchain.embeddings import HuggingFaceEmbeddings
from chromadbx import DocumentSHA256Generator
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
# from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
import constants


class TxtChatBot:

    def __init__(self):
        self.docs = None
        self.retriever = None
        self.llm = None
        self.chain = None
        self.chat_history = []

    def load_and_split_docs(self):
        """
        Load and split documents
        """

        # path to the directory containing .txt documents
        docs_path = "." + os.sep + constants.DATA_DIR

        # load documents
        loader = DirectoryLoader(
            docs_path,
            glob='**/*.txt',
            loader_cls=TextLoader
        )
        raw_documents = loader.load()

        # split documents into chunks
        text_splitter = CharacterTextSplitter(
            separator=".",  # split on a full-stop
            chunk_size=1000,
            chunk_overlap=50  # overlap to avoid loss of information
        )

        self.docs = text_splitter.split_documents(raw_documents)

    def configure_retriever(self):
        """
        Set up Chroma vector database and retriever
        """

        # path to the directory containing .txt documents
        db_path = "." + os.sep + constants.CHROMA_DIR
        cln_name = "doc"

        # Chroma client to save and load the database from the local machine
        # data will be persisted automatically and loaded on start (if it exists)
        client = PersistentClient(path=db_path)

        '''
        # for cleaner reloading, delete old collection if exists
        try:
            client.get_collection(name=cln_name)
            client.delete_collection(name=cln_name)
        except Exception as err:
            # logger.logg(err)
            pass
        '''

        embedding_func = OpenAIEmbeddingFunction(api_key=constants.OPENAI_API_KEY)

        collection = client.get_or_create_collection(
            name=cln_name,
            embedding_function=embedding_func
        )

        unique_docs = list(set(doc.page_content for doc in self.docs))
        doc_ids = DocumentSHA256Generator(documents=unique_docs)

        try:
            collection.upsert(
                ids=doc_ids,
                documents=unique_docs,
            )
        except Exception as err:
            # logger.logg(err)
            # print(err)
            pass

        embeddings = OpenAIEmbeddings(openai_api_key=constants.OPENAI_API_KEY)

        db = Chroma(
            client=client,
            collection_name=cln_name,
            embedding_function=embeddings,
            persist_directory=db_path,
        )

        # self.retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        self.retriever = db.as_retriever()

    def configure_llm(self):
        """
        Create and configure LLM
        """

        self.llm = ChatOpenAI(
            model=constants.OPENAI_LLM,
            openai_api_key=constants.OPENAI_API_KEY
        )

    def create_chain(self):
        """
        Create conversational history-aware retrieval chain
        """

        # make the output appear as string
        # output_parser = StrOutputParser()

        contextualized_prompt = ChatPromptTemplate.from_messages([
            ("system", "Based on chat history and user question, make the question understandable without history."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        contextualized_retriever = create_history_aware_retriever(self.llm, self.retriever, contextualized_prompt)

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the user question based on the below context:\\n\\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        document_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        self.chain = create_retrieval_chain(contextualized_retriever, document_chain)

    def init_chatbot(self):
        """
        Build 'Chatbot' assistant
        """

        self.load_and_split_docs()
        self.configure_retriever()
        self.configure_llm()
        self.create_chain()

    def generate_response(self, user_input):
        """
        Perform history-aware QA task
        """

        # TODO check if chatbot was configured properly

        response = self.chain.invoke(
            {
                "chat_history": self.chat_history,
                "input": user_input
            }
        )

        answer = response['answer']
        self.chat_history.append(user_input)
        self.chat_history.append(answer)

        return answer

