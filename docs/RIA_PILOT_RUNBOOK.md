# Sturna.ai RIA Pilot Runbook
**Target Date:** June 3, 2026

## Objective
Successfully onboard RIA pilot participants with compliance evidence generation.

## Pre-Launch Checklist

- [ ] Set EMAIL_PROVIDER=resend and EMAIL_API_KEY in Render
- [ ] Verify domain in Resend
- [ ] Run python scripts/pre_deploy_check.py
- [ ] Test pilot signup flow
- [ ] Test nurture email trigger

## Key Endpoints

- POST /api/pilot/signup
- GET /api/pilot/workspace/{pilot_id}
- GET /api/lead-gen/nurture/test
- GET /api/trust/shields

## Success Metrics
- Pilot signups
- Evidence packages generated
- Nurture emails delivered