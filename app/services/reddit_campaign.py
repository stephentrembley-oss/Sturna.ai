import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class RedditCampaignService:
    def __init__(self):
        self.base_url = os.getenv("STURNA_BASE_URL", "https://sturna-ai-s862.onrender.com")

    async def create_post(self, subreddit: str, template_key: str, custom_title: Optional[str] = None) -> Dict:
        print(f"[Reddit] Post queued for r/{subreddit} using template: {template_key}")
        return {
            "status": "queued",
            "subreddit": subreddit,
            "template": template_key,
            "scheduled_for": datetime.utcnow().isoformat()
        }

    async def schedule_campaign(
        self, 
        campaign_name: str, 
        subreddits: List[str], 
        template_key: str, 
        interval_hours: int = 6
    ) -> Dict:
        results = []
        base_time = datetime.utcnow()

        for i, subreddit in enumerate(subreddits):
            post_time = base_time + timedelta(hours=i * interval_hours)
            result = await self.create_post(subreddit, template_key)
            result["scheduled_for"] = post_time.isoformat()
            result["campaign"] = campaign_name
            results.append(result)

        return {
            "campaign": campaign_name,
            "posts_scheduled": len(results),
            "results": results
        }