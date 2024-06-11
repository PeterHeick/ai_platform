
# Chatbot API Server med ChromaDB Integration

## Beskrivelse

Denne applikation er en chatbot API server designet som en mikroservice. Den håndterer forespørgsler og giver svar baseret på specifikke dokumenter såsom GDPR-regler, regler for hvidvask eller firmaspecifikke dokumenter. Disse dokumenter gemmes i en ChromaDB, og chat-historikken overlever kun den enkelte session.

## Funktioner

- **API til chat-forespørgsler**: Modtager beskeder og returnerer svar.
- **ChromaDB integration**: Gemmer og henter dokumenter fra en ChromaDB instans.
- **Session-baseret chat-historik**: Gemmer chat-historik kun for den aktuelle session.

## Installation

Før du starter, skal du sørge for at have følgende installeret:

- Python 3.8 til 3.11
- Docker
- Docker Compose

## Opsætning

1. **Clone repository**:
   ```sh
   git clone <repository-url>
   cd chatbot-api
   ```

2. Opret et virtuelt miljø i projektmappen:
    ```sh
    python -m venv venv
    ```

3. **Installer afhængigheder**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Byg og start Docker-containere**:
   ```sh
   docker-compose up --build
   ```

Dette vil starte både ChromaDB og chatbot API serveren.

## Brug

Når Docker-containere kører, vil API'en være tilgængelig på `http://localhost:5000`.

### Eksempel på API-opkald

- **POST /chat**:
  - Request Body: `{ "message": "Hej, hvordan kan du hjælpe mig?" }`
  - Response Body: `{ "response": "Dette er et svar fra chatbotten" }`

Du kan teste API'en ved at sende POST-forespørgsler til `http://localhost:5000/chat` med værktøjer som `curl`, `Postman` eller integrerede tests.

## Struktur

```plaintext
chatbot-api/
├── chromadb/
├── docs/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── chromadb_client.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chatbot_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat_history.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_db.py
│   ├── test_services.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Udvikling og Test

1. **Installer afhængigheder**:
   Hvis du arbejder udenfor Docker, kan du installere Python-afhængigheder:
   ```sh
   pip install -r requirements.txt
   ```

2. ## Kør tests

For at teste funktionaliteten i `chromadb_client.py`, skal du følge disse trin:

### Start ChromaDB Server

Før du kører testene, skal du starte ChromaDB serveren.

1. Installer ChromaDB ved at følge instruktionerne i hoveddelen af README.md.
2. Start ChromaDB serveren:
    ```sh
    chroma run --host localhost --port 8000 --path ./chromadb
    ```

### Kør testene

1. Sørg for at du har alle afhængigheder installeret:
    ```sh
    pip install -r requirements.txt
    ```

2. Kør testene ved at bruge `unittest`:
    ```sh
    python -m unittest discover -s tests
    ```

Testene vil kontrollere, om dokumenterne er korrekt indekseret, om forespørgsler returnerer resultater, og om nye dokumenter bliver indekseret korrekt.


## Bidrag

Bidrag er velkomne! Følg venligst standard udviklingsworkflow med pull requests.

## Licens

Dette projekt er licenseret under MIT-licensen.

### Resumé af samtale om prompt, retriever history og RAG chain

**Formål:**
Koden omformulerer spørgsmål for at gøre dem forståelige uden chat-historik og henter relevante dokumenter fra ChromaDB til at besvare brugerens spørgsmål.

**Hovedkomponenter:**

1. **Retriever:** 
   - Initialiseres med `retriever = chromadb.as_retriever()`.
   - Bruges til at hente dokumenter fra ChromaDB.

2. **Prompts:**
   - **Contextualize Question Prompt:**
     ```python
     contextualize_q_system_prompt = (
         "Given a chat history and the latest user question..."
     )
     contextualize_q_prompt = ChatPromptTemplate.from_messages([
         ("system", contextualize_q_system_prompt),
         ("placeholder", "{chat_history}"),
         ("human", "{input}"),
     ])
     ```
     - Omformulerer spørgsmålet for at gøre det selvstændigt og forståeligt uden tidligere chat-historik.

   - **Answer Prompt:**
     ```python
     system_prompt = (
         "You are an assistant for question-answering tasks..."
         "{context}"
     )
     answer_prompt = ChatPromptTemplate.from_messages([
         ("system", system_prompt),
         ("placeholder", "{chat_history}"),
         ("human", "{input}"),
     ])
     ```
     - Bruges til at generere svar baseret på den hentede kontekst.

3. **Chains:**
   - **History-aware retriever chain:**
     ```python
     retriever_chain = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
     ```
     - Kombinerer LLM, retriever og prompt for at hente relevante dokumenter baseret på omformulerede spørgsmål.

   - **Question-answer chain:**
     ```python
     question_answer_chain = create_stuff_documents_chain(llm, answer_prompt)
     ```

   - **RAG (Retrieval-Augmented Generation) chain:**
     ```python
     rag_chain = create_retrieval_chain(retriever_chain, question_answer_chain)
     ```
     - Kombinerer retrieval og question-answer processerne for at levere endelige svar.

**Flow:**
1. Bruger stiller et spørgsmål.
2. `retriever_chain` omformulerer spørgsmålet og henter relevante dokumenter fra ChromaDB.
3. Dokumenterne bruges som kontekst i `answer_prompt`.
4. `question_answer_chain` genererer et svar.
5. `rag_chain` kombinerer begge processer for at levere det endelige svar.

**Opsummering:**
Koden bruger en række kæder til at omformulere spørgsmål, hente dokumenter fra ChromaDB, og generere præcise svar baseret på de hentede dokumenter. `retriever_chain` håndterer omformulering og hentning af dokumenter, mens `question_answer_chain` og `rag_chain` kombinerer retrieval og besvarelse af spørgsmål.

Dette resumé kan hjælpe dig med at forstå og huske, hvordan koden fungerer om nogle måneder.
