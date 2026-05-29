import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class AuditFinding:
    category: str
    severity: str
    description: str
    remediation: str
    deadline: str


class AuditReportService:
    def __init__(self):
        self.base_url = os.getenv("STURNA_BASE_URL", "https://sturna-ai-s862.onrender.com")

    async def generate_report(self, pilot_id: str, framework: str) -> Dict:
        report_id = f"AUDIT_{pilot_id}_{framework}_{datetime.utcnow().strftime('%Y%m%d')}"

        findings = [
            AuditFinding(
                category="AI System Inventory",
                severity="high",
                description="Incomplete inventory of AI systems",
                remediation="Complete full AI inventory scan",
                deadline=(datetime.utcnow() + timedelta(days=7)).isoformat()
            )
        ]

        signature = self._sign_report(report_id, findings)

        return {
            "report_id": report_id,
            "pilot_id": pilot_id,
            "framework": framework,
            "status": "completed",
            "compliance_score": 78,
            "findings_count": len(findings),
            "cryptographic_signature": signature,
            "pdf_url": f"{self.base_url}/reports/{report_id}.pdf",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _sign_report(self, report_id: str, findings: List) -> str:
        data = f"{report_id}:{len(findings)}:{datetime.utcnow().isoformat()}"
        return f"STURNA_SIG_{hashlib.sha256(data.encode()).hexdigest()[:32].upper()}"