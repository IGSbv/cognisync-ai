from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from knowledge_base import sync_knowledge_base, query_knowledge_base
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables to ensure the API key is available
load_dotenv()

# Initialize the Gemini LLM for final answer synthesis
# This uses the Gemini Pro model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", convert_system_message_to_human=True)

# This is the prompt template that instructs the AI how to behave
PROMPT_TEMPLATE = """
Answer the user's question based *only* on the following context:

{context}

---

Answer the user's question based on the above context: {question}
"""

app = FastAPI()

# CORS Middleware to allow frontend to connect
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    Root endpoint to check if the server is running.
    """
    return {"Status": "CogniSync AI Backend is Running"}

@app.post("/sync")
def sync_handler():
    """
    Endpoint to manually trigger the data sync from all MCP connectors.
    """
    return sync_knowledge_base()

@app.post("/chat")
def chat_handler(query: dict):
    """
    Main chat endpoint to handle user questions.
    """
    user_query = query.get('text')
    if not user_query:
        return {"sender": "ai", "text": "Error: No text provided in the request."}

    print(f"Received query: {user_query}")
    
    # 1. Query the knowledge base to get relevant context
    context_chunks = query_knowledge_base(user_query)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in context_chunks])

    # 2. Create a prompt with the context and user's question
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=user_query)
    
    # 3. Call the LLM to synthesize the final answer
    response = llm.invoke(prompt)
    
    ai_answer = response.content
    
    return {"sender": "ai", "text": ai_answer}