import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import our MCP connectors
from mcp_connectors import get_jira_tickets, get_notion_page_content

# Ensure GEMINI_API_KEY is in your .env file
# This will use the "embedding-001" model by default
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# This will create the directory if it doesn't exist
persist_directory = "./chroma_db"
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def sync_knowledge_base():
    """
    Fetches data from all MCP connectors and syncs it to the vector store.
    """
    print("Starting knowledge base sync...")
    
    # NOTE: Replace "KAN" with your actual Jira Project Key
    jira_project_key = "KAN"
    
    # 1. Fetch data from sources
    jira_data = get_jira_tickets(jira_project_key)
    notion_data = get_notion_page_content(os.getenv("NOTION_PAGE_ID"))
    
    # 2. Split documents into smaller chunks
    jira_chunks = text_splitter.create_documents([jira_data], metadatas=[{"source": "Jira"}])
    notion_chunks = text_splitter.create_documents([notion_data], metadatas=[{"source": "Notion"}])
    all_chunks = jira_chunks + notion_chunks
    
    # 3. Add to the vector store
    vector_store.add_documents(documents=all_chunks) # Embedding function is already part of the vector store
    vector_store.persist()
    
    print(f"Sync complete. Added {len(all_chunks)} chunks to the knowledge base.")
    return {"status": "success", "chunks_added": len(all_chunks)}

def query_knowledge_base(query_text: str):
    """
    Queries the knowledge base to find relevant context for a user's question.
    """
    print(f"Querying knowledge base for: {query_text}")
    results = vector_store.similarity_search(query_text, k=4)
    return results