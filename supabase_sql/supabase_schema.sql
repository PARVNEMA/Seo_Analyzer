-- Create crawl_jobs table
CREATE TABLE IF NOT EXISTS public.crawl_jobs (
    id TEXT PRIMARY KEY,
    target_url TEXT NOT NULL,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create crawl_results table
CREATE TABLE IF NOT EXISTS public.crawl_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id TEXT REFERENCES public.crawl_jobs(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    meta_description TEXT,
    headers JSONB,
    total_images INTEGER DEFAULT 0,
    missing_alt_images INTEGER DEFAULT 0,
    total_links INTEGER DEFAULT 0,
    broken_links INTEGER DEFAULT 0,
    text_content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Optional: Add Row Level Security (RLS) policies if you have authentication enabled.
-- If you are just testing locally/from backend, you might not need these, but it's good practice.
-- ALTER TABLE public.crawl_jobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.crawl_results ENABLE ROW LEVEL SECURITY;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_crawl_results_job_id ON public.crawl_results(job_id);
