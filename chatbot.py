from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
# from chromadb.utils.embedding_functions import HuggingFaceEmbeddingFunction
from chromadbx import DocumentSHA256Generator
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
# from langchain.llms import HuggingFacePipeline
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from datetime import datetime
import os
import constants


def load_and_split_docs():
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
    documents = text_splitter.split_documents(raw_documents)

    return documents


def init_chromadb(documents):
    """
    Set up Chroma vector database
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

    unique_docs = list(set(doc.page_content for doc in documents))
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

    # return db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return db.as_retriever()


def configure_llm():
    """
    Create and configure LLM
    """

    llm = ChatOpenAI(
        model=constants.OPENAI_LLM,
        openai_api_key=constants.OPENAI_API_KEY
    )

    return llm


def create_prompt():
    """
    Create and configure prompt
    """

    # system prompt template
    system_prompt = (
        "You are an AI assistant for question-answering tasks."
        "Given only the following context: {context}"
        "Answer the following question: {question}"
        "Use five sentences maximum and give concise answer."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
        ]
    )

    return prompt


def create_chain(llm, retriever):
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

    contextualized_retriever = create_history_aware_retriever(llm, retriever, contextualized_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user question based on the below context:\\n\\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])

    document_chain = create_stuff_documents_chain(llm, qa_prompt)

    retrieval_chain = create_retrieval_chain(contextualized_retriever, document_chain)

    return retrieval_chain


def ask_question(chain, user_input, chat_history):
    """
    Perform history-aware QA task
    """

    response = chain.invoke(
        {
            "chat_history": chat_history,
            "input": user_input
        }
    )

    return response['answer']


def main():
    """
    Build 'Chatbot' assistant with CLI Interface
    """

    print("\nHello! I am a chatbot. I can answer questions based on the content of a your documents.\n")

    txt_docs = load_and_split_docs()
    retriever = init_chromadb(txt_docs)
    openai_llm = configure_llm()
    conv_chain = create_chain(openai_llm, retriever)
    chat_history = []

    while True:
        current_datetime = datetime.now()
        user_input = input("Do you have any questions? To exit, type 'bye': ")

        answer = ask_question(conv_chain, user_input, chat_history)
        elapsed_time = datetime.now() - current_datetime

        print("\nChatbot: ", answer)
        print("\n Time elapsed: ", elapsed_time.total_seconds(), "seconds \n")

        if user_input.lower() == "bye":
            break
        else:
            chat_history.append(user_input)  # HumanMessage(content=user_input))
            chat_history.append(answer)  # AIMessage(content=answer))


if __name__ == '__main__':
    main()
