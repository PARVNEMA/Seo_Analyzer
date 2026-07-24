import logging
import os
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.supabase import get_supabase_client

logger = logging.getLogger(__name__)

# Initialize the embedding model (using Hugging Face API to avoid local downloads)
# Set HUGGINGFACEHUB_API_TOKEN in your .env file
embedding_model = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

def process_and_store_embeddings(
    crawl_result_id: str,
    text_content: str,
    title: str = None,
    meta_description: str = None,
    metadata: Dict[str, Any] = None
):
    """
    Takes a single crawl result, combines its title, meta_description and text_content,
    chunks it, generates embeddings, and stores them asynchronously into the Supabase pgvector table.
    """
    try:
        if not text_content or not text_content.strip():
            logger.warning(f"No text content found for crawl_result_id {crawl_result_id}. Skipping embeddings.")
            return

        logger.info(f"Starting embedding generation for crawl_result_id {crawl_result_id}...")

        # Combine title, meta description and text content
        combined_parts = []
        if title:
            combined_parts.append(f"Title: {title.strip()}")
        if meta_description:
            combined_parts.append(f"Meta Description: {meta_description.strip()}")

        combined_parts.append(f"Content:\n{text_content.strip()}")

        combined_text = "\n\n".join(combined_parts)

        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

        # Split combined text into chunks
        chunks = text_splitter.split_text(combined_text)
        if not chunks:
            logger.warning("Text splitting resulted in zero chunks. Skipping.")
            return

        logger.info(f"Created {len(chunks)} chunks. Generating embeddings...")

        # Generate embeddings for each chunk sequentially to avoid HF API 429 rate limits
        try:
            import threading
            if not hasattr(embedding_model, '_lock'):
                embedding_model._lock = threading.Lock()

            with embedding_model._lock:
                embeddings = embedding_model.embed_documents(chunks)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return

        # Prepare data for insertion
        records_to_insert = []
        base_meta = metadata or {}

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_meta = base_meta.copy()
            chunk_meta["chunk_index"] = i

            records_to_insert.append({
                "crawl_result_id": crawl_result_id,
                "content": chunk,
                "metadata": chunk_meta,
                "embedding": embedding
            })

        logger.info(f"Saving {len(records_to_insert)} embeddings to Supabase...")

        # Save to Supabase
        supabase = get_supabase_client()
        # insert returns data, count
        result = supabase.table("crawl_results_embeddings").insert(records_to_insert).execute()
        logger.info(f"Successfully saved embeddings for crawl_result_id {crawl_result_id}.")
        return result
    except Exception as e:
        logger.error(f"FATAL ERROR in embeddings for {crawl_result_id}: {e}")
        return None
