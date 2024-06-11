import os
import sys
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
dbStore = "./chromadb"
model = "gpt-3.5-turbo-0125"
docDir = "docs"

llm = ChatOpenAI(model=model)
embedding_function = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=dbStore, embedding_function=embedding_function)

load_dotenv()

def split_text(documents: list[Document]):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    add_start_index=True
  )
  return text_splitter.split_documents(documents)

loader = DirectoryLoader(docDir)
documents = loader.load()
chunks = split_text(documents)
vectordb.add_documents(chunks)