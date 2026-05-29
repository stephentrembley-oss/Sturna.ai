import os
import httpx
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict
import re

class NurtureEngine:
    """
    Production email nurture system for Sturna.ai.
    Sends real emails via Resend API with verified domain.
    """

    def __init__(self, db: Session):
        self.db = db
        self.api_key = os.getenv("EMAIL_API_KEY")  # Your Resend API key from Render
        self.from_email = os.getenv("NURTURE_FROM_EMAIL", "stephen@sturna.ai")
        self.from_name = os.getenv("NURTURE_FROM_NAME", "Stephen Trembley")
        self.base_url = os.getenv("STURNA_BASE_URL", "https://octomind-9fce.polsia.app")

    # ─── Email 1: Demo Follow-Up ─────────────────────────────────────────────

    async def send_demo_followup(self, lead_id: int, custom_data: Optional[Dict] = None):
        from app.models.lead import Lead
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead or not lead.email:
            print(f"[Nurture] Lead {lead_id} has no email. Skipping.")
            return {"status": "skipped", "reason": "no_email"}
        
        subject = f"{lead.first_name}, your compliance scan results are ready"
        
        body = f"""Hi {lead.first_name},

You just saw Sturna.ai identify compliance gaps in real-time. Here's what that means:
The gaps we found are exactly what regulators look for first.
SEC examiners, OCR auditors, and SOC 2 assessors all start with the same questions:
•  Where is your AI system inventory?
•  Can you prove human review happened?
•  Do you have evidence for every decision?
Most firms answer "we're working on it." Sturna generates the evidence in minutes.
Your next step:
I've reserved a pilot slot for {lead.company} — 14 days, full platform access, no commitment.
We'll generate your Reg S-P and EU AI Act evidence package together.
Book 15 minutes: {self.base_url}/demo/schedule?lead={lead_id}
Evidence first. No trust required.
Stephen Trembley
Founder, Sturna.ai
"""
        result = await self._send_email(lead.email, subject, body, "demo_followup", lead_id)
        
        # Schedule Email 2 in 48 hours
        if result.get("status") == "sent":
            await self._schedule_next(lead_id, "scanner_results", delay_hours=48)
        
        return result

    # ─── Email 2: Scanner Results / Reg S-P Urgency ─────────────────────────

    async def send_scanner_results(self, lead_id: int, custom_data: Optional[Dict] = None):
        from app.models.lead import Lead
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead or not lead.email:
            return {"status": "skipped", "reason": "no_email"}
        
        subject = f"Reg S-P deadline: {lead.first_name}, you have 72 hours to prove AI oversight"
        
        body = f"""Hi {lead.first_name},

The June 3 Reg S-P deadline is 72 hours away. Here's what SEC examiners are asking RIAs right now:
"Show us your AI oversight evidence."
Not your policy document. Not your intention to comply. The actual evidence:
•  Signed human review logs with timestamps
•  AI system inventory with risk scores
•  Explainability records for every automated decision
•  Chain-of-custody audit trails
If you don't have these ready, you're not alone. Most RIAs are scrambling.
What Sturna.ai generated for a similar firm last week:
•  47-page compliance evidence package
•  100% audit-ready formatting
•  Zero findings in their SEC review
This isn't theoretical. It's what we ship.
Your pilot starts today:
{self.base_url}/pilot/start?lead={lead_id}
14 days. Full evidence generation. No commitment.
Stephen Trembley
Founder, Sturna.ai
P.S. — If you're already prepared for June 3, reply "ready" and I'll send you our SOC 2 Type II prep checklist instead.
"""
        result = await self._send_email(lead.email, subject, body, "scanner_results", lead_id)
        
        if result.get("status") == "sent":
            await self._schedule_next(lead_id, "pilot_welcome", delay_hours=72)
        
        return result

    # ─── Email 3: Pilot Welcome or Final Push ────────────────────────────────

    async def send_pilot_welcome(self, lead_id: int, custom_data: Optional[Dict] = None):
        from app.models.lead import Lead
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead or not lead.email:
            return {"status": "skipped", "reason": "no_email"}
        
        if lead.status == "pilot_signed":
            subject = f"Welcome to your Sturna.ai pilot, {lead.first_name}"
            body = f"""Hi {lead.first_name},

Your Sturna.ai pilot is live. Here's what happens next:
Hour 1: Platform access + compliance scan setup
Day 1: First evidence package generated (Reg S-P or EU AI Act)
Day 7: Full AI system inventory + risk classification
Day 14: Complete audit-ready documentation + handoff
Your pilot workspace: {self.base_url}/pilot/workspace?pid={lead_id}
What to expect:
•  Every finding is backed by verifiable evidence
•  Every report is formatted for regulator submission
•  Every action is logged with immutable audit trails
I'll check in on Day 3 to review your first evidence package.
Stephen Trembley
Founder, Sturna.ai
"""
        else:
            subject = f"Last call: RIA pilot slots close Friday, {lead.first_name}"
            body = f"""Hi {lead.first_name},
I'm closing RIA pilot registrations this Friday. Here's why this matters:
The firms that started their pilot 2 weeks ago are already submitting evidence to regulators.
Not planning to. Not preparing for. Actually submitting.
One RIA generated their entire Reg S-P compliance package in 3 days. Their CCO told me: "This is what we should have built internally."
What you get in the pilot:
•  Full platform access (all 112 compliance domains)
•  Custom evidence generation for your specific regulatory framework
•  1:1 walkthrough with me on Day 1 and Day 7
•  Audit-ready documentation you can submit immediately
Start here: {self.base_url}/pilot/start?lead={lead_id}
Friday is the cutoff. After that, we're focused on enterprise deployments only.
Stephen Trembley
Founder, Sturna.ai
"""
        
        return await self._send_email(lead.email, subject, body, "pilot_welcome", lead_id)

    # ─── Evidence Download Follow-Up ─────────────────────────────────────────

    async def send_evidence_followup(self, lead_id: int, custom_data: Optional[Dict] = None):
        from app.models.lead import Lead
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead or not lead.email:
            return {"status": "skipped", "reason": "no_email"}
        
        subject = f"{lead.first_name}, here's your next compliance evidence package"
        
        body = f"""Hi {lead.first_name},

You downloaded your first evidence package. Here's what most firms do next:
If you started with Reg S-P: Generate your EU AI Act evidence next. The overlap is 60% — we auto-map it.
If you started with EU AI Act: Add SOC 2 Type II evidence. Same platform, different framework.
If you started with HIPAA: Expand to state privacy laws (CCPA, CPRA, VCDPA).
Your evidence library: {self.base_url}/evidence/library?lead={lead_id}
Every package you generate builds on the last. By Week 3, most firms have 4 complete regulatory frameworks ready for submission.
Question for you: Which regulator is asking for evidence first? Reply and I'll prioritize that framework in your next scan.
Stephen Trembley
Founder, Sturna.ai
"""
        
        return await self._send_email(lead.email, subject, body, "evidence_followup", lead_id)

    # ─── Core Email Sender (Resend API) ──────────────────────────────────────

    async def _send_email(self, to_email: str, subject: str, body: str, 
                          email_type: str, lead_id: int = 0) -> Dict:
        """Send email via Resend API with verified domain."""
        
        if not self.api_key:
            print(f"[Nurture] NO API KEY — Would send to {to_email}:")
            print(f"  Subject: {subject[:60]}...")
            return {"status": "simulated", "reason": "no_api_key"}
        
        # Convert text to HTML
        html_body = self._text_to_html(body)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": f"{self.from_name} <{self.from_email}>",
                        "to": [to_email],
                        "subject": subject,
                        "text": body,
                        "html": html_body,
                        "tags": [
                            {"name": "sturna-nurture", "value": email_type},
                            {"name": "lead_id", "value": str(lead_id)}
                        ]
                    },
                    timeout=30.0
                )
            
            if response.status_code in [200, 202]:
                data = response.json()
                message_id = data.get("id")
                
                # Log to database
                self._log_email(lead_id, email_type, to_email, subject, "sent", message_id)
                
                print(f"[Nurture] ✅ SENT: {email_type} -> {to_email} (ID: {message_id})")
                
                return {
                    "status": "sent",
                    "provider": "resend",
                    "message_id": message_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                error_text = response.text
                print(f"[Nurture] ❌ FAILED: {response.status_code} — {error_text}")
                self._log_email(lead_id, email_type, to_email, subject, "failed")
                return {
                    "status": "failed", "error": f"Resend API error: {response.status_code}", "details": error_text
                }
                
        except Exception as e:
            print(f"[Nurture] ❌ EXCEPTION: {e}")
            self._log_email(lead_id, email_type, to_email, subject, "failed")
            return {"status": "failed", "error": str(e)}

    # ─── Helpers ─────────────────────────────────────────────────────────────

    def _text_to_html(self, text: str) -> str:
        """Convert plain text to styled HTML."""
        html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html = html.replace("\n", "<br>")
        html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
        
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sturna.ai</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.6; font-size: 15px; }}
strong {{ color: #00d4aa; }}
a {{ color: #00d4aa; text-decoration: none; }}
hr {{ margin: 40px 0; border: none; border-top: 1px solid #e5e5e5; }}
.footer {{ font-size: 13px; color: #666; margin-top: 40px; }}
.footer a {{ color: #00d4aa; }}
</style>
</head>
<body>
{html}
<hr>
<div class="footer">
<p><strong>Sturna.ai</strong> — Compliance Intelligence, Verified by Design</p>
<p><a href="{self.base_url}">{self.base_url}</a></p>
<p style="font-size: 11px; color: #999; margin-top: 20px;">This email was sent because you engaged with Sturna.ai compliance content. Reply STOP to unsubscribe.</p>
</div>
</body>
</html>"""
    
    def _log_email(self, lead_id: int, email_type: str, to_email: str, 
                   subject: str, status: str, message_id: str = None):
        """Log email to database."""
        from app.models.lead import OutreachLog
        log = OutreachLog(
            lead_id=lead_id,
            channel="email",
            action=email_type,
            status=status,
            message_preview=f"{subject[:100]}...",
            sent_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
    
    async def _schedule_next(self, lead_id: int, next_email_type: str, delay_hours: int):
        """Schedule next email in sequence."""
        # Production: Use Celery with Redis, or APScheduler
        # For now, log the scheduled task
        print(f"[Nurture] Scheduled: {next_email_type} for lead {lead_id} in {delay_hours}h")
        # TODO: Implement with Celery or background task queue