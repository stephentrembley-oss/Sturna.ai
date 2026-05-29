import os
from datetime import datetime
from typing import Dict, Optional


class LinkedInOutreachService:
    def __init__(self):
        self.base_url = os.getenv("STURNA_BASE_URL", "https://sturna-ai-s862.onrender.com")
        self.daily_limit = int(os.getenv("LINKEDIN_DAILY_LIMIT", "50"))

    async def send_connection_request(self, lead_id: int, profile: Dict) -> Dict:
        print(f"[LinkedIn] Connection request prepared for {profile.get('first_name')} {profile.get('last_name')}")
        return {
            "status": "queued",
            "lead_id": lead_id,
            "scheduled_for": datetime.utcnow().isoformat()
        }

    async def send_follow_up(self, lead_id: int, profile: Dict, step: int) -> Dict:
        print(f"[LinkedIn] Follow-up #{step} prepared for lead {lead_id}")
        return {"status": "scheduled", "step": step}