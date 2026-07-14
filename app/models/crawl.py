from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(String, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    job_type = Column(String, nullable=False) # 'crawl' or 'crawl-seo'
    status = Column(String, default="pending") # 'pending', 'running', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)

class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String)
    meta_description = Column(String)
    headers = Column(JSON) # JSON storing H1-H6 tags
    total_images = Column(Integer)
    missing_alt_images = Column(Integer)
    total_links = Column(Integer)
    broken_links = Column(Integer)
    text_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
