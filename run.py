#!/usr/bin/env python3
"""
Campus Lost & Found - Application Entrypoint
Run this script to launch the local web server.
"""

from app import app
from seed_data import seed_database
import os
from config import Config

if __name__ == '__main__':
    # Initialize database with pre-populated campus data if DB doesn't exist
    if not os.path.exists(Config.DATABASE):
        print("[*] Database not detected. Seeding sample campus data...")
        seed_database()

    print("\n" + "=" * 65)
    print("   🌌 CAMPUS LOST & FOUND - ANTIGRAVITY WEB APPLICATION")
    print("=" * 65)
    print("   ✓ Smart Item Matching Engine: Active")
    print("   ✓ Confidential Ownership Verification Shield: Active")
    print("   ✓ In-App Handover Coordination Chat: Active")
    print("   ✓ Interactive Campus Vector Map: Active")
    print("   ✓ Admin Control Center & Moderation: Active")
    print("-" * 65)
    print("   👉 Open your browser at: http://127.0.0.1:5000")
    print("=" * 65 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=True)
