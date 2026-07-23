import asyncio
import os
from app.services.embedding_service import process_and_store_embeddings

def run_test():
    try:
        res = process_and_store_embeddings(
            crawl_result_id='00000000-0000-0000-0000-000000000000',
            text_content='This is a dummy text to test if embeddings are generated correctly.',
            title='Test Title',
            meta_description='Test Meta'
        )
        print('Result:', res)
    except Exception as e:
        print('Error:', e)

run_test()
