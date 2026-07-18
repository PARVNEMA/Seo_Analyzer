-- 1. Enable the pgvector extension to work with embedding vectors
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create a table to store chunks of text and their embeddings
CREATE TABLE IF NOT EXISTS public.crawl_results_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crawl_result_id UUID REFERENCES public.crawl_results(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(384) -- We use 384 for sentence-transformers like all-MiniLM-L6-v2
);

-- 3. Create an index for faster similarity searches (optional but recommended for large datasets)
CREATE INDEX IF NOT EXISTS idx_crawl_embeddings 
ON public.crawl_results_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- 4. Create a function to perform cosine similarity search
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(384),
  match_count INT DEFAULT 5,
  filter_metadata JSONB DEFAULT '{}'
) RETURNS TABLE (
  id UUID,
  crawl_result_id UUID,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    e.id,
    e.crawl_result_id,
    e.content,
    e.metadata,
    1 - (e.embedding <=> query_embedding) AS similarity
  FROM public.crawl_results_embeddings e
  WHERE e.metadata @> filter_metadata
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
