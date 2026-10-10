import os
import sqlite3
from werkzeug.security import generate_password_hash
from database import get_db, init_db
from config import Config

def seed_sample_images():
    """Create SVG illustration icons for seeded items in static/uploads/"""
    uploads_dir = Config.UPLOAD_FOLDER
    os.makedirs(uploads_dir, exist_ok=True)

    sample_svgs = {
        'bottle_blue.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
            <defs>
                <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00f2fe"/>
                    <stop offset="100%" stop-color="#4facfe"/>
                </linearGradient>
            </defs>
            <rect width="400" height="400" fill="#111827"/>
            <circle cx="200" cy="200" r="140" fill="#1e293b" opacity="0.6"/>
            <!-- Bottle Body -->
            <rect x="150" y="130" width="100" height="180" rx="20" fill="url(#g1)"/>
            <!-- Cap -->
            <rect x="170" y="80" width="60" height="40" rx="8" fill="#38bdf8"/>
            <rect x="180" y="65" width="40" height="15" rx="5" fill="#0284c7"/>
            <!-- Accent details -->
            <path d="M 170 170 Q 200 190 230 170" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.7"/>
            <circle cx="175" cy="240" r="14" fill="#fbbf24"/>
            <text x="200" y="355" fill="#94a3b8" font-family="sans-serif" font-size="14" text-anchor="middle">Hydro Flask 750ml</text>
        </svg>''',

        'wallet_leather.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
            <defs>
                <linearGradient id="gw" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#334155"/>
                    <stop offset="100%" stop-color="#0f172a"/>
                </linearGradient>
            </defs>
            <rect width="400" height="400" fill="#111827"/>
            <circle cx="200" cy="200" r="140" fill="#1e293b" opacity="0.6"/>
            <!-- Wallet Fold -->
            <rect x="110" y="140" width="180" height="120" rx="14" fill="url(#gw)" stroke="#475569" stroke-width="3"/>
            <!-- Stitching and flap -->
            <path d="M 110 170 L 290 170" stroke="#64748b" stroke-width="2" stroke-dasharray="6,4"/>
            <rect x="240" y="180" width="40" height="40" rx="6" fill="#1e293b" stroke="#00f2fe" stroke-width="2"/>
            <circle cx="260" cy="200" r="5" fill="#00f2fe"/>
            <!-- Cards peeking -->
            <rect x="130" y="125" width="70" height="25" rx="4" fill="#3b82f6" opacity="0.8"/>
            <rect x="145" y="115" width="70" height="25" rx="4" fill="#a855f7" opacity="0.8"/>
            <text x="200" y="355" fill="#94a3b8" font-family="sans-serif" font-size="14" text-anchor="middle">Black Leather Wallet</text>
        </svg>''',

        'calculator_casio.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
            <defs>
                <linearGradient id="gc" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#1e293b"/>
                    <stop offset="100%" stop-color="#090d16"/>
                </linearGradient>
            </defs>
            <rect width="400" height="400" fill="#111827"/>
            <!-- Calc Body -->
            <rect x="130" y="80" width="140" height="240" rx="18" fill="url(#gc)" stroke="#38bdf8" stroke-width="2"/>
            <!-- Display -->
            <rect x="145" y="105" width="110" height="45" rx="6" fill="#042f2e" stroke="#14b8a6" stroke-width="1.5"/>
            <text x="245" y="138" fill="#2dd4bf" font-family="monospace" font-size="20" text-anchor="end">fx-991EX</text>
            <!-- Solar cell -->
            <rect x="210" y="90" width="45" height="10" rx="2" fill="#78350f"/>
            <!-- Keypad grid -->
            <g fill="#334155" rx="3">
                <rect x="145" y="165" width="22" height="16" rx="3"/>
                <rect x="175" y="165" width="22" height="16" rx="3"/>
                <rect x="205" y="165" width="22" height="16" rx="3"/>
                <rect x="233" y="165" width="22" height="16" rx="3"/>

                <rect x="145" y="195" width="22" height="16" rx="3"/>
                <rect x="175" y="195" width="22" height="16" rx="3"/>
                <rect x="205" y="195" width="22" height="16" rx="3"/>
                <rect x="233" y="195" width="22" height="16" rx="3"/>

                <rect x="145" y="225" width="22" height="16" rx="3"/>
                <rect x="175" y="225" width="22" height="16" rx="3"/>
                <rect x="205" y="225" width="22" height="16" rx="3"/>
                <rect x="233" y="225" width="22" height="16" rx="3"/>

                <rect x="145" y="255" width="22" height="16" rx="3" fill="#0284c7"/>
                <rect x="175" y="255" width="22" height="16" rx="3"/>
                <rect x="205" y="255" width="22" height="16" rx="3"/>
                <rect x="233" y="255" width="22" height="16" rx="3" fill="#ef4444"/>

                <rect x="145" y="285" width="52" height="18" rx="3"/>
                <rect x="205" y="285" width="50" height="18" rx="3" fill="#10b981"/>
            </g>
            <text x="200" y="355" fill="#94a3b8" font-family="sans-serif" font-size="14" text-anchor="middle">Casio Scientific Calculator</text>
        </svg>''',

        'macbook_laptop.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
            <defs>
                <linearGradient id="gm" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#38bdf8"/>
                    <stop offset="100%" stop-color="#a855f7"/>
                </linearGradient>
            </defs>
            <rect width="400" height="400" fill="#111827"/>
            <!-- Screen lid -->
            <rect x="100" y="110" width="200" height="135" rx="10" fill="#0f172a" stroke="#64748b" stroke-width="2"/>
            <rect x="110" y="120" width="180" height="115" rx="4" fill="url(#gm)" opacity="0.8"/>
            <!-- Apple logo mark -->
            <circle cx="200" cy="175" r="16" fill="#ffffff" opacity="0.85"/>
            <!-- Base keyboard deck -->
            <path d="M 70 245 L 330 245 L 310 265 L 90 265 Z" fill="#334155"/>
            <rect x="165" y="250" width="70" height="8" rx="3" fill="#64748b"/>
            <text x="200" y="355" fill="#94a3b8" font-family="sans-serif" font-size="14" text-anchor="middle">Apple MacBook Air M2</text>
        </svg>''',

        'id_card.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
            <rect width="400" height="400" fill="#111827"/>
            <!-- Lanyard -->
            <path d="M 170 30 L 195 120 M 230 30 L 205 120" stroke="#3b82f6" stroke-width="6"/>
            <!-- Clip -->
            <rect x="190" y="115" width="20" height="15" rx="3" fill="#94a3b8"/>
            <!-- Card Body -->
            <rect x="120" y="130" width="160" height="190" rx="12" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
            <!-- Top bar -->
            <rect x="120" y="130" width="160" height="35" rx="10" fill="#2563eb"/>
            <text x="200" y="152" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="11" text-anchor="middle">CAMPUS SMART PASS</text>
            <!-- Photo placeholder -->
            <rect x="140" y="175" width="50" height="55" rx="6" fill="#334155"/>
            <circle cx="165" cy="195" r="14" fill="#64748b"/>
            <!-- Text lines -->
            <rect x="200" y="180" width="60" height="8" rx="2" fill="#94a3b8"/>
            <rect x="200" y="195" width="50" height="6" rx="2" fill="#64748b"/>
            <rect x="200" y="208" width="55" height="6" rx="2" fill="#64748b"/>
            <!-- Barcode -->
            <rect x="140" y="250" width="120" height="20" fill="#ffffff" opacity="0.9"/>
            <text x="200" y="355" fill="#94a3b8" font-family="sans-serif" font-size="14" text-anchor="middle">Student ID RFID Card</text>
        </svg>''',

        'keys_batman.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
            <rect width="400" height="400" fill="#111827"/>
            <circle cx="200" cy="150" r="30" fill="none" stroke="#e2e8f0" stroke-width="6"/>
            <!-- Batman keychain badge -->
            <rect x="150" y="180" width="100" height="50" rx="12" fill="#0f172a" stroke="#fbbf24" stroke-width="3"/>
            <path d="M 170 205 Q 185 190 200 215 Q 215 190 230 205 Q 215 225 200 215 Q 185 225 170 205 Z" fill="#fbbf24"/>
            <!-- Hanging keys -->
            <path d="M 185 175 L 170 280 L 180 285 L 180 270 L 175 255" stroke="#94a3b8" stroke-width="6" fill="none"/>
            <path d="M 215 175 L 230 290 L 220 295 L 222 275 L 228 260" stroke="#cbd5e1" stroke-width="6" fill="none"/>
            <text x="200" y="355" fill="#94a3b8" font-family="sans-serif" font-size="14" text-anchor="middle">Keys on Batman Keychain</text>
        </svg>'''
    }

    for filename, content in sample_svgs.items():
        filepath = os.path.join(uploads_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())

def seed_database():
    """Populate database with default campus users, reports, claims, and messages."""
    init_db()
    seed_sample_images()
    conn = get_db()
    cursor = conn.cursor()

    # Clear existing data for clean setup
    cursor.execute("DELETE FROM feedback")
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM notifications")
    cursor.execute("DELETE FROM saved_items")
    cursor.execute("DELETE FROM claims")
    cursor.execute("DELETE FROM items")
    cursor.execute("DELETE FROM users")
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
    except sqlite3.OperationalError:
        pass

    # 1. Users
    pw_admin = generate_password_hash('Admin@123')
    pw_student = generate_password_hash('Student@123')

    users_data = [
        ('Campus Security Desk', 'admin@campus.edu', 'ADMIN-001', pw_admin, 'admin', 'Security & Student Affairs', '+1 (555) 019-2834'),
        ('Alex Chen', 'alex.chen@campus.edu', '1MS21CS042', pw_student, 'student', 'Computer Science & Eng', '+1 (555) 012-3456'),
        ('Priya Sharma', 'priya.sharma@campus.edu', '1MS21EC088', pw_student, 'student', 'Electronics & Comm Eng', '+1 (555) 019-7722'),
        ('Marcus Vance', 'marcus.vance@campus.edu', '1MS22ME015', pw_student, 'student', 'Mechanical Engineering', '+1 (555) 018-9943'),
        ('Sara Connor', 'sara.connor@campus.edu', '1MS22IS073', pw_student, 'student', 'Information Science Eng', '+1 (555) 017-5511')
    ]

    cursor.executemany("""
    INSERT INTO users (name, email, usn, password_hash, role, department, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, users_data)

    cursor.execute("SELECT id, email FROM users")
    user_rows = cursor.fetchall()
    user_ids = {}
    for r in user_rows:
        em = r['email']
        if 'admin' in em: user_ids['admin'] = r['id']
        elif 'alex' in em: user_ids['alex'] = r['id']
        elif 'priya' in em: user_ids['priya'] = r['id']
        elif 'marcus' in em: user_ids['marcus'] = r['id']
        elif 'sara' in em: user_ids['sara'] = r['id']

    # 2. Items
    items_data = [
        # (user_id, type, title, category, description, private_details, location, item_date, item_time, contact_method, image_path, status)
        (
            user_ids['alex'], 'LOST',
            'Midnight Blue Hydro Flask Water Bottle 750ml',
            'Bottles & Tumblers',
            'Lost my dark blue wide-mouth Hydro Flask bottle on the ground floor eating area. Has a black flex cap.',
            'Contains a prominent yellow sticker with "Code & Coffee" on the top lid, plus a dent on the lower rim.',
            'Main Canteen / Food Court',
            '2026-10-07', '13:15',
            'In-App Handover Chat',
            'bottle_blue.svg',
            'OPEN'
        ),
        (
            user_ids['priya'], 'FOUND',
            'Navy Blue Insulated Tumbler / Water Bottle',
            'Bottles & Tumblers',
            'Found an insulated metallic navy blue water bottle left on Table #4 near the juice corner after lunchtime.',
            'Has stickers including a yellow tech sticker, with a minor dent on the bottom base rim.',
            'Main Canteen / Food Court',
            '2026-10-07', '13:40',
            'In-App Handover Chat',
            'bottle_blue.svg',
            'OPEN'
        ),
        (
            user_ids['marcus'], 'LOST',
            'Black Leather Bi-fold Wallet with ID & Cards',
            'Keys & Wallets',
            'Misplaced my black leather wallet while studying on the 2nd floor silent reading zone. Contains college card and transit passes.',
            'Inside card slot holds Student ID 1MS22ME015 and a transit pass ending in digits 4492.',
            'Central Library',
            '2026-10-08', '16:00',
            'Central Campus Security Desk',
            'wallet_leather.svg',
            'OPEN'
        ),
        (
            user_ids['admin'], 'FOUND',
            'Black Men\'s Leather Wallet with Campus Passes',
            'Keys & Wallets',
            'Handed over to Security Desk. Genuine black leather wallet found under study booth #14 in Central Library.',
            'Contains student card belonging to Department of Mechanical Eng and blue transit card.',
            'Central Library',
            '2026-10-08', '17:30',
            'Central Campus Security Desk',
            'wallet_leather.svg',
            'CLAIM_PENDING'
        ),
        (
            user_ids['sara'], 'FOUND',
            'Scientific Calculator Casio fx-991EX ClassWiz',
            'Calculators & Stationery',
            'Left on Physics Lab bench #4 next to the optics experiment setup. Genuine Casio ClassWiz model.',
            'Has personal initials "S.V." handwritten in silver metallic paint pen inside the sliding protective cover.',
            'Science & Engineering Labs',
            '2026-10-06', '15:20',
            'In-App Handover Chat',
            'calculator_casio.svg',
            'OPEN'
        ),
        (
            user_ids['marcus'], 'LOST',
            'Casio Scientific Calculator fx-991EX with Slide Cover',
            'Calculators & Stationery',
            'Lost my calculator during physics lab exam on Tuesday. Very urgent for engineering semester test.',
            'Initials "S.V." written inside the cover with silver pen, battery compartment seal slightly worn.',
            'Science & Engineering Labs',
            '2026-10-06', '14:50',
            'In-App Handover Chat',
            'calculator_casio.svg',
            'OPEN'
        ),
        (
            user_ids['admin'], 'FOUND',
            'Apple MacBook Air M2 in Space Grey Sleeve',
            'Electronics & Gadgets',
            'High-value laptop left on table row 3 in Computer Science Seminar Hall after the AI Guest Lecture. Safe at Security Desk.',
            'Silver GitHub Octocat sticker on lower left corner; lock screen display is a violet cosmic nebula.',
            'Computer Science & Tech Block',
            '2026-10-09', '11:00',
            'Central Campus Security Desk',
            'macbook_laptop.svg',
            'OPEN'
        ),
        (
            user_ids['priya'], 'LOST',
            'Campus RFID Student Smart Card with ECE Lanyard',
            'Student IDs & Cards',
            'Dropped my college smart ID card on the stairs leading to Main Auditorium during morning orientation.',
            'Blood group O+ indicated on the rear hologram, lanyard has tiny enamel cat pin.',
            'Main Auditorium & Hall',
            '2026-10-05', '10:15',
            'In-App Handover Chat',
            'id_card.svg',
            'RETURNED'
        ),
        (
            user_ids['alex'], 'FOUND',
            'Set of 3 Keys on Batman Heavy Metal Keychain',
            'Keys & Wallets',
            'Found on motorcycle parking stand B near the campus entrance. 3 keys attached to heavy Batman metal emblem.',
            'One Honda motorbike key, two small brass Godrej cabinet keys, ring has small red rubber band.',
            'Bus Bay & Parking Area',
            '2026-10-08', '09:30',
            'In-App Handover Chat',
            'keys_batman.svg',
            'OPEN'
        )
    ]

    # Add coordinates dynamically from CAMPUS_LOCATION_COORDS
    from config import CAMPUS_LOCATION_COORDS
    items_with_coords = []
    for item in items_data:
        loc = item[6]
        coords = CAMPUS_LOCATION_COORDS.get(loc, {'lat': 12.9716, 'lng': 77.5946})
        items_with_coords.append((
            item[0], item[1], item[2], item[3], item[4], item[5],
            item[6], coords['lat'], coords['lng'],
            item[7], item[8], item[9], item[10], item[11]
        ))

    cursor.executemany("""
    INSERT INTO items (
        user_id, type, title, category, description, private_details,
        location, latitude, longitude, item_date, item_time, contact_method, image_path, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, items_with_coords)

    # 3. Claims
    cursor.execute("SELECT id, title FROM items")
    item_rows = cursor.fetchall()
    wallet_found_id = item_rows[3]['id']
    id_card_id = item_rows[7]['id']

    # Marcus Vance claiming the found wallet
    cursor.execute("""
    INSERT INTO claims (item_id, claimant_id, proof_description, identifying_answers, contact_note, status, decision_note, decided_by)
    VALUES (?, ?, ?, ?, ?, 'PENDING', '', NULL)
    """, (
        wallet_found_id,
        user_ids['marcus'],
        'This is my wallet lost on 2nd floor library. Contains my Mechanical Eng student ID and transit card ending 4492.',
        'Transit card ending digits: 4492. Also has an old movie ticket from PVR in the cash compartment.',
        'I can meet at Security Desk anytime between 2 PM and 5 PM.'
    ))
    wallet_claim_id = cursor.lastrowid

    # Priya Sharma's returned item claim
    cursor.execute("""
    INSERT INTO claims (item_id, claimant_id, proof_description, identifying_answers, contact_note, status, decision_note, decided_by)
    VALUES (?, ?, ?, ?, ?, 'RETURNED', 'Verified student photo ID and handed over in person.', ?)
    """, (
        id_card_id,
        user_ids['priya'],
        'My RFID ID card with Priya Sharma and USN 1MS21EC088.',
        'Blood group O+ on the back, small enamel cat pin on lanyard.',
        'Received safely from Admin front desk.',
        user_ids['admin']
    ))
    card_claim_id = cursor.lastrowid

    # 4. In-App Handover Messages (Marcus Vance & Admin regarding Claim on Wallet)
    messages_data = [
        (wallet_claim_id, wallet_found_id, user_ids['marcus'], user_ids['admin'], 'Hello, I submitted a claim for the black leather wallet found in the Library. I provided the card numbers in the claim verification.', 1),
        (wallet_claim_id, wallet_found_id, user_ids['admin'], user_ids['marcus'], 'Hello Marcus. We checked the private details and they match the student ID in the wallet. Please bring your physical library card or another photo ID to the Security Desk Room 102.', 1),
        (wallet_claim_id, wallet_found_id, user_ids['marcus'], user_ids['admin'], 'Thank you so much! I will come right after my 3 PM lecture.', 0)
    ]

    cursor.executemany("""
    INSERT INTO messages (claim_id, item_id, sender_id, recipient_id, message, is_read)
    VALUES (?, ?, ?, ?, ?, ?)
    """, messages_data)

    # 5. Notifications
    notifs = [
        (user_ids['alex'], 'Smart Match Found!', 'A Navy Blue Insulated Tumbler was reported found in Main Canteen matching your lost item report.', f'/item/{item_rows[1]["id"]}', 'match', 0),
        (user_ids['priya'], 'Smart Match Alert', 'Alex Chen reported a lost Midnight Blue Hydro Flask that closely matches your found report.', f'/item/{item_rows[0]["id"]}', 'match', 0),
        (user_ids['marcus'], 'Claim Received by Admin', 'Your claim on Black Men\'s Leather Wallet is under review by Security Desk.', '/claims', 'claim', 1),
        (user_ids['admin'], 'New Claim Pending', 'Marcus Vance submitted an ownership claim for Black Men\'s Leather Wallet.', '/claims', 'claim', 0),
        (user_ids['priya'], 'Item Returned Successfully', 'Your Campus RFID Student Smart Card was marked as Returned. Thank you for using Campus Lost & Found!', f'/item/{id_card_id}', 'approval', 1)
    ]

    cursor.executemany("""
    INSERT INTO notifications (user_id, title, message, link, type, is_read)
    VALUES (?, ?, ?, ?, ?, ?)
    """, notifs)

    # 6. Saved items
    cursor.execute("INSERT INTO saved_items (user_id, item_id) VALUES (?, ?)", (user_ids['alex'], item_rows[6]['id']))
    cursor.execute("INSERT INTO saved_items (user_id, item_id) VALUES (?, ?)", (user_ids['marcus'], wallet_found_id))

    # 7. Feedback
    cursor.execute("""
    INSERT INTO feedback (claim_id, user_id, rating, comment)
    VALUES (?, ?, 5, 'Found my ID card within 3 hours! Super smooth verification process at the Admin desk.')
    """, (card_claim_id, user_ids['priya']))

    conn.commit()
    conn.close()
    print("Database seeded with sample campus users, items, smart matches, claims and chats.")

if __name__ == '__main__':
    seed_database()
