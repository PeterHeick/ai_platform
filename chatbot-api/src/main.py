import os
from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import chatbot
from fastapi.responses import FileResponse
from langchain_core.documents import Document
import uuid
import json
import jsonpickle

app = FastAPI()

documents = os.path.join(os.path.dirname(__file__), '../docs')

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
        unique_sources.add(d.metadata["source"])
    return list(unique_sources)


def custom_serializer(obj):
    if isinstance(obj, Document):
        return obj.__dict__
    elif isinstance(obj, list):
        return [custom_serializer(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: custom_serializer(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {key: custom_serializer(value) for key, value in obj.__dict__.items()}
    else:
        return obj

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

@app.get("/favicon.ico")
async def favicon():
    return "" # FileResponse("path/to/your/favicon.ico")
                        
@app.post("/query")
async def query_endpoint(request: Request, query_request: QueryRequest):
    query_type = request.query_params.get("type") 
    print("query " + query_request.query)
    session_id = get_session_id(request)

    print(f"query: {query_request.query}")
    print(f"session_id: {session_id}")
    result = chatbot(query_request.query, session_id)
    answer = result['answer']
    
    with open('result.json', 'w') as file:
      file.write(jsonpickle.encode(result, indent=2))
    answer = result["answer"]
    unique_sources_list = get_unique_sources(result)
    filenames = []
    for source in unique_sources_list:
        filenames.append(os.path.basename(source))

    return {"answer": answer, "docsource": filenames}
    
@app.get("/get_pdf/{filename}")
async def get_pdf(filename: str):
    print(f"Requested file: {filename}")

    document_path = os.path.join(documents, filename)
    print(f"Full path to file: {document_path}")

    if os.path.exists(document_path):
        return FileResponse(document_path, media_type="application/pdf")
    else:
        return {"error": "Fil ikke fundet"}