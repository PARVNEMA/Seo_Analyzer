import logging
from typing import Optional, List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from app.db.supabase import get_supabase_client
from app.core.llm_factory import get_llm

logger = logging.getLogger(__name__)

# Same embedding model used for storing
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def ask_seo_question(query: str, match_count: int = 5, filter_metadata: Optional[Dict] = None) -> str:
    """
    Takes a user query, retrieves relevant SEO context from Supabase pgvector,
    and uses the configured LLM (e.g. Groq) to generate an answer.
    """
    logger.info(f"Generating embedding for query: '{query}'")
    
    # 1. Embed the query
    query_embedding = embedding_model.embed_query(query)
    
    # 2. Retrieve relevant chunks from Supabase
    supabase = get_supabase_client()
    
    rpc_params = {
        "query_embedding": query_embedding,
        "match_count": match_count,
        "filter_metadata": filter_metadata or {}
    }
    
    try:
        response = supabase.rpc("match_documents", rpc_params).execute()
        documents = response.data
    except Exception as e:
        logger.error(f"Failed to query Supabase RPC match_documents: {e}")
        return f"Sorry, I encountered a database error while retrieving context: {str(e)}"
        
    if not documents:
        return "I couldn't find any relevant SEO data to answer your question."
        
    # 3. Construct the context
    context_parts = []
    for doc in documents:
        # doc structure based on SQL: id, crawl_result_id, content, metadata, similarity
        content = doc.get("content", "")
        context_parts.append(f"---\nRelevant Snippet:\n{content}")
        
    context_str = "\n".join(context_parts)
    
    # 4. Generate answer using LLM
    llm = get_llm()
    
    system_prompt = (
        "You are an expert SEO assistant. Your task is to answer the user's question based "
        "only on the provided context retrieved from crawled website pages. If the context does not "
        "contain the answer, say that you don't have enough information.\n\n"
        f"Context:\n{context_str}"
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    logger.info("Sending prompt to LLM...")
    try:
        llm_response = llm.invoke(messages)
        return llm_response.content if hasattr(llm_response, "content") else str(llm_response)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return f"Sorry, I encountered an error generating the answer: {str(e)}"
