#!/usr/bin/env python3
"""
Sturna.ai Pre-Deploy Check
P0 Sprint - Day 5
"""
import sys
import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(check_name, status, message=""):
    icon = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
    color = Colors.GREEN if status == "pass" else Colors.RED if status == "fail" else Colors.YELLOW
    print(f"{color}{icon} {check_name}{Colors.END}")
    if message:
        print(f"   {message}")

def main():
    print(f"\n{Colors.BLUE}Sturna.ai Pre-Deploy Check{Colors.END}\n")
    
    checks = []
    
    # Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print_status("Python Version", "pass", f"{version.major}.{version.minor}")
        checks.append(True)
    else:
        print_status("Python Version", "fail")
        checks.append(False)
    
    # Check key files exist
    required_files = [
        "app/models/lead.py",
        "app/models/pilot.py",
        "app/api/routes/lead_gen.py",
        "app/api/routes/pilot_onboarding.py",
        "frontend/pilot_dashboard.html"
    ]
    
    missing = [f for f in required_files if not Path(f).exists()]
    if not missing:
        print_status("Required Files", "pass")
        checks.append(True)
    else:
        print_status("Required Files", "fail", f"Missing: {missing}")
        checks.append(False)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print(f"{Colors.GREEN}Ready for deployment{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}Fix issues before deploying{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())