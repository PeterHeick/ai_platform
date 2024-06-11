from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import queryRetriever
import uuid

app = FastAPI()
retriever_chain = queryRetriever()

# Tilføj CORS-handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Juster dette for at specificere tilladte origins
    allow_credentials=True,
    allow_methods=["*"],  # Tillad alle metoder
    allow_headers=["*"],
)

# Gem sessioner i en dictionary
session_store = {}

def get_unique_sources(result):
    unique_sources = set()
    for d in result["context"]:
        unique_sources.add(d["metadata"]["source"])
    return list(unique_sources)


class QueryRequest(BaseModel):
    query: str

def get_session_id(request: Request):
    ip_address = request.client.host  # Hent IP-adresse
    user_agent = request.headers.get("User-Agent")  # Hent browser-ID

    # Kombiner IP og User-Agent for at skabe en mere unik session_id
    session_key = f"{ip_address}-{user_agent}"
    if session_key not in session_store:
        session_store[session_key] = str(uuid.uuid4())  # Generer ny session_id, hvis den ikke findes
    return session_store[session_key]

@app.post("/query")
async def query_endpoint(request: Request, query_request: QueryRequest):
    session_id = get_session_id(request)
    input_data = {"input": query_request.query}
    result = retriever_chain.invoke(input_data, config={"configurable": {"session_id": session_id}})
    answer = result["answer"]
    unique_sources_list = get_unique_sources(result)
    print(unique_sources_list)
    return {"answer": answer, "docsource": unique_sources_list}
    
