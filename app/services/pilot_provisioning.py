import os
from datetime import datetime, timedelta
from typing import Dict


class PilotProvisioningService:
    def __init__(self):
        self.base_url = os.getenv("STURNA_BASE_URL", "https://sturna-ai-s862.onrender.com")
        self.storage_backend = os.getenv("PILOT_STORAGE", "local")
        self.max_pilots = int(os.getenv("MAX_CONCURRENT_PILOTS", "50"))

    async def create_workspace(self, pilot_id: str, company_name: str) -> Dict:
        workspace = {
            "pilot_id": pilot_id,
            "company_name": company_name,
            "created_at": datetime.utcnow().isoformat(),
            "resources": {}
        }
        
        workspace["resources"]["database"] = await self._provision_database(pilot_id)
        workspace["resources"]["storage"] = await self._provision_storage(pilot_id, company_name)
        workspace["resources"]["api_keys"] = await self._generate_api_keys(pilot_id)
        workspace["resources"]["branding"] = await self._setup_branding(pilot_id, company_name)
        workspace["resources"]["frameworks"] = await self._configure_frameworks(pilot_id)
        workspace["resources"]["audit"] = await self._initialize_audit(pilot_id)
        
        print(f"[Provisioning] Workspace ready for {company_name} ({pilot_id})")
        
        return workspace

    async def _provision_database(self, pilot_id: str) -> Dict:
        schema_name = f"pilot_{pilot_id.lower()}"
        return {
            "schema": schema_name,
            "type": "isolated_schema",
            "status": "provisioned"
        }

    async def _provision_storage(self, pilot_id: str, company_name: str) -> Dict:
        bucket_name = f"sturna-pilot-{pilot_id.lower()}"
        return {
            "bucket": bucket_name,
            "type": self.storage_backend,
            "status": "provisioned"
        }

    async def _generate_api_keys(self, pilot_id: str) -> Dict:
        import secrets
        return {
            "read_key": f"sk_read_{secrets.token_urlsafe(8)}",
            "write_key": f"sk_write_{secrets.token_urlsafe(8)}",
            "expires_at": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "status": "active"
        }

    async def _setup_branding(self, pilot_id: str, company_name: str) -> Dict:
        return {
            "company_name": company_name,
            "status": "configured"
        }

    async def _configure_frameworks(self, pilot_id: str) -> Dict:
        return {
            "available": ["Reg_S_P", "EU_AI_Act", "SOC_2"],
            "status": "configured"
        }

    async def _initialize_audit(self, pilot_id: str) -> Dict:
        return {
            "status": "active"
        }

    async def deprovision_workspace(self, pilot_id: str) -> Dict:
        return {
            "pilot_id": pilot_id,
            "action": "deprovisioned",
            "deprovisioned_at": datetime.utcnow().isoformat()
        }