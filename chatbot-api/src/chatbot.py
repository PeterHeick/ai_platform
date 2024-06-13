import sys, os
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
import PyPDF2
from dotenv import load_dotenv
load_dotenv()

dbStore = os.path.join(os.path.dirname(__file__), '../../chromadb')
model = "gpt-3.5-turbo-0125"

llm = ChatOpenAI(model=model)
embedding_function = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=dbStore, embedding_function=embedding_function)
store = {}

# Funktion til at hente dokumenter fra ChromaDB baseret på forespørgsel
def queryRetriever():
    
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    contextualize_q_system_prompt = (
      "Given a chat history and the latest user question "
      "which might reference context in the chat history, "
      "formulate a standalone question which can be understood "
      "without the chat history. Do NOT answer the question, "
      "just reformulate it if needed and otherwise return it as is."
    )

    # Find dokumenter baseret på historik og det nye spørgsmål
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    retriever = vectordb.as_retriever()
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    # Besvar det nye spørgsmål på baggrund af de fundne dokumenter
    qa_system_prompt = (
    """
      You are a helpful assistant for question-answering tasks.
      Use the following pieces of retrieved context to answer 
      Use only information from the context to answer
      the question. keep the answer concise. 
      If you don't know the answer, just say that you don't know.
      Conversation with the user should be in danish
      \n\n
      {context}
    """
    )
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_rag_chain

def get_text_around_start_index(text, start_index, chars_before=200, chars_after=1000):
    """
    Udskriver teksten omkring et givet startindeks.

    Args:
        text: Teksten, der skal søges i.
        start_index: Startindekset for den ønskede tekst.
        chars_before: Antal tegn før startindekset, der skal inkluderes.
        chars_after: Antal tegn efter startindekset, der skal inkluderes.
    """

    start = max(0, start_index - chars_before)  # Start ikke før begyndelsen af teksten
    end = start_index + chars_after
    return text[start:end]

def get_chunk_from_start_index(file_path, start_index):
    with open(file_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return get_text_around_start_index(text, start_index)
  
if __name__ == "__main__":
    retriever_chain = queryRetriever()
    session_id = "test_session"
    # chat_history = []

    print("Type exit to exit")
    while True:
        user_input = input(">> ")
        if user_input.lower() == 'exit':
            break
        
        input_data = {
            # "chat_history": chat_history,
            "input": user_input,
        }
        result = retriever_chain.invoke(input_data, config={"configurable": {"session_id": session_id}})  
        answer = result['answer']
        
        print(result)
        for d in result["context"]:
            print(d.metadata["source"])

        updated_history = store[session_id]
        for message in updated_history.messages:
            print(message)

        # for document in result["context"]:
        #   file_path = document.metadata["source"]
        #   start_index = document.metadata["start_index"]
        #   print("---")
        #   print(file_path)
        #   relevant_chunk = get_chunk_from_start_index(file_path, start_index)
        #   print(relevant_chunk)
        #   print()

        # # Opdater chat-historikken
        # chat_history.append({"role": "user", "content": user_input})
        # chat_history.append({"role": "assistant", "content": answer})
