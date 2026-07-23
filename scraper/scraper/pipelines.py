import os
import requests
import logging

logger = logging.getLogger(__name__)

class WebhookPipeline:
    def process_item(self, item, spider):
        job_id = getattr(spider, 'job_id', None)
        if not job_id:
            logger.warning("No job_id provided, skipping webhook post.")
            return item

        port = os.environ.get("PORT", "8000")
        webhook_url = f"http://127.0.0.1:{port}/api/v1/webhook/crawls/{job_id}"

        # item is typically a dict
        data = dict(item)
        data['job_id'] = job_id

        try:
            response = requests.post(webhook_url, json=data, timeout=5)
            if response.status_code != 200:
                logger.error(f"Failed to post to webhook: {response.text}")
        except Exception as e:
            logger.error(f"Webhook connection error: {e}")

        return item
