import sys, os
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
import PyPDF2
import jsonpickle
from dotenv import load_dotenv
load_dotenv()

dbStore = os.path.join(os.path.dirname(__file__), '../../chromadb')
model = "gpt-4o"
# model = "gpt-3.5-turbo"

llm = ChatOpenAI(model=model)
embedding_function = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=dbStore, embedding_function=embedding_function)
retriever = vectordb.as_retriever()
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Funktion til at hente dokumenter fra ChromaDB baseret på forespørgsel
def history_retriever():
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
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    return history_aware_retriever


def history_rag_chain(history_aware_retriever):
    # Besvar det nye spørgsmål på baggrund af de fundne dokumenter
    qa_system_prompt = (
    """
      You are a helpful assistant for question-answering tasks.
      Use the following pieces of retrieved context to answer 
      Use only information from the context to answer
      the question. keep the answer concise. 
      If you don't know the answer, just say that you don't know.
      Conversation with the user should be in danish.
      Keep the answer to no more than 50 words.
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
    return rag_chain


def chatbot(query: str = None, session_id: str = None):
    
    history_aware_retriever = history_retriever()
    
    docs = history_aware_retriever.invoke({"input": query})

    with open("docs.json", "w") as f:
      f.write(jsonpickle.encode(docs))
      
    rag_chain = history_rag_chain(history_aware_retriever)
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    input_data = {
       # "chat_history": chat_history,
       "input": query,
    }
    result = conversational_rag_chain.invoke(
      input_data, config={"configurable": {"session_id": session_id}}
    ) 
    
    verification_prompt = """
    You are a helpful assistant tasked with verifying the alignment between a question, an answer,
    and the retrieved documents.
    Your goal is to ensure that the answer can be derived from the documents

    And that the documents can appropriately address the question.
    Please analyze the provided question, answer, and the enclosed documents.
    Based on the following criteria:

    1. The documents contain sufficient information to answer the question.
    2. The answer is directly supported by the information in the documents.

    If both criteria are met, respond with "yes". If either criterion is not met, respond with "no".

    Question: {question}
    Answer: {answer}

    Check that the answer to the question is found in this document:
    <documents>
      {context}
    </documents>

    Your response should be "yes" or "no".
    """

    with open("result.json", "w") as f:
      f.write(jsonpickle.encode(result))
    response = {"context": [], "answer": result["answer"]}
    list_of_documents = ""
    i = 1
    for d in result["context"]:
      start_index = d.metadata["start_index"]
      relevant_chunk = get_chunk_from_start_index(d.metadata["source"], start_index)
      list_of_documents += f"Document {i}:\n" + relevant_chunk + "\n\n"

    documents = Document(page_content=list_of_documents, metadata={"source": ""})
    prompt = ChatPromptTemplate.from_messages(
      [
        ("system", verification_prompt),
        ("human", "{question}"),
        AIMessage(content="{answer}"),
      ]
    )

    verification_chain = create_stuff_documents_chain(llm, prompt)

    input_data = {
        "context": [documents],
        "question": query,
        "answer": result["answer"],
    }
    answer = verification_chain.invoke(input_data)
    if answer == "yes":
      response = result

    with open("verification.txt", "w") as f:
      f.write(f"Verification answer: {answer}\nquestion: {query}\nanswer: {result['answer']}\ncontext: {documents}")

    with open("response.json", "w") as f:
      f.write(jsonpickle.encode(response))
    return  response

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

def read_pdf(file_path):
    # Åbn PDF-filen i binær læse-tilstand
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        all_text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            all_text += text + "\n"
        
        return all_text

def get_chunk_from_start_index(file_path, start_index):
    text = read_pdf(file_path)
    return get_text_around_start_index(text, start_index)
  
def format_multiline_answer(answer: str, indentation: int = 4) -> str:
    import re
    indent = " " * indentation
    # Split svaret ved linjeskift og tilføj indrykning til hver linje
    lines = answer.split('\n')
    formatted_lines = [indent + line for line in lines]
    return '\n'.join(formatted_lines)

if __name__ == "__main__":
    session_id = "test_session"
    # chat_history = []

    print("Type exit to exit")
    while True:
        user_input = input(">> ")
        if user_input.lower() == 'exit':
            break
        
        result = chatbot(user_input, session_id)
        answer = result['answer']
        
        with open("output.txt", "a") as f:
          f.write(f"User: {user_input}\n")
          f.write(f"Assistant: {answer}\n\n")
          f.write("Context:\n")
          for d in result["context"]:
            # formatted_source = format_multiline_answer(d.metadata["source"], indentation=4)
            f.write("  source:\n")
            f.write(d["metadata"]["source"])

          updated_history = store[session_id]
          for message in updated_history.messages:
            f.write(message.content)

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
