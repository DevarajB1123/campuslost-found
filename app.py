import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config, CAMPUS_LOCATIONS, ITEM_CATEGORIES, CAMPUS_LOCATION_COORDS, CAMPUS_CENTER
from database import get_db, init_db
from smart_matcher import find_smart_matches, detect_potential_duplicates, compute_match_score

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper: check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in as Administrator.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Administrator privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for templates
@app.context_processor
def inject_global_data():
    unread_notifs = 0
    current_user = None
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (session['user_id'],))
        unread_notifs = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        current_user = cursor.fetchone()
        conn.close()

    maps_key = session.get('user_google_maps_key') or app.config.get('GOOGLE_MAPS_API_KEY', '')

    return dict(
        current_user=current_user,
        unread_notifs=unread_notifs,
        campus_locations=CAMPUS_LOCATIONS,
        campus_location_coords=CAMPUS_LOCATION_COORDS,
        campus_center=CAMPUS_CENTER,
        google_maps_api_key=maps_key,
        item_categories=ITEM_CATEGORIES,
        current_year=datetime.now().year
    )

# -------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        usn = request.form.get('usn', '').strip().upper()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        department = request.form.get('department', 'General')
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'student')

        if not name or not email or not usn or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        # Admin key check if registering as admin
        if role == 'admin':
            admin_code = request.form.get('admin_code', '')
            if admin_code != 'CAMPUS-ADMIN-2026':
                flash('Invalid Campus Admin Security Passcode.', 'danger')
                return render_template('register.html')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR usn = ?", (email, usn))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            flash('An account with this Email or Student ID / USN already exists.', 'warning')
            return render_template('register.html')

        pw_hash = generate_password_hash(password)
        cursor.execute("""
        INSERT INTO users (name, email, usn, password_hash, role, department, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, usn, pw_hash, role, department, phone))
        conn.commit()
        user_id = cursor.lastrowid

        # Welcome notification
        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, link, type)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, 'Welcome to Campus Lost & Found', 'Your verified campus account is ready. Report lost items or search for found items anytime.', '/browse', 'system'))
        conn.commit()
        conn.close()

        session['user_id'] = user_id
        session['user_name'] = name
        session['role'] = role
        session['email'] = email

        flash(f'Welcome aboard, {name}! Your campus account has been activated.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login_id = request.form.get('login_id', '').strip().lower()
        password = request.form.get('password', '')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = ? OR UPPER(usn) = UPPER(?)", (login_id, login_id))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']
            flash(f'Signed in successfully as {user["name"]}.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid credentials. Please verify your Email/USN and password.', 'danger')

    return render_template('login.html')

@app.route('/quick-login/<role_or_name>')
def quick_login(role_or_name):
    """Convenience shortcut for demonstrations and testing."""
    conn = get_db()
    cursor = conn.cursor()
    if role_or_name == 'admin':
        cursor.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1")
    elif role_or_name == 'alex':
        cursor.execute("SELECT * FROM users WHERE email LIKE 'alex%' LIMIT 1")
    elif role_or_name == 'priya':
        cursor.execute("SELECT * FROM users WHERE email LIKE 'priya%' LIMIT 1")
    elif role_or_name == 'marcus':
        cursor.execute("SELECT * FROM users WHERE email LIKE 'marcus%' LIMIT 1")
    else:
        cursor.execute("SELECT * FROM users LIMIT 1")

    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['role'] = user['role']
        session['email'] = user['email']
        flash(f'Logged in as {user["name"]} ({user["role"].capitalize()}).', 'info')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('index'))

# -------------------------------------------------------------
# HOME DASHBOARD
# -------------------------------------------------------------

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()

    # Statistics
    cursor.execute("SELECT COUNT(*) FROM items WHERE status != 'ARCHIVED'")
    total_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'LOST' AND status = 'OPEN'")
    open_lost = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'FOUND' AND status IN ('OPEN', 'CLAIM_PENDING')")
    open_found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'RETURNED'")
    returned_items = cursor.fetchone()[0]

    # Recovery rate %
    recovery_rate = round((returned_items / total_items * 100) if total_items > 0 else 0)

    # Recent items (latest 6)
    cursor.execute("""
    SELECT i.*, u.name as reporter_name, u.role as reporter_role
    FROM items i
    JOIN users u ON i.user_id = u.id
    WHERE i.status != 'ARCHIVED'
    ORDER BY i.created_at DESC LIMIT 6
    """)
    recent_items = [dict(row) for row in cursor.fetchall()]

    # Hotspot stats by location
    cursor.execute("""
    SELECT location, COUNT(*) as count
    FROM items
    WHERE status != 'ARCHIVED'
    GROUP BY location
    ORDER BY count DESC LIMIT 4
    """)
    top_locations = cursor.fetchall()

    # Smart matches count for logged in user
    user_match_count = 0
    if 'user_id' in session:
        cursor.execute("SELECT * FROM items WHERE user_id = ? AND status != 'ARCHIVED'", (session['user_id'],))
        my_items = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM items WHERE user_id != ? AND status != 'ARCHIVED'", (session['user_id'],))
        other_items = [dict(r) for r in cursor.fetchall()]

        for item in my_items:
            matches = find_smart_matches(item, other_items, min_threshold=50)
            user_match_count += len(matches)

    conn.close()

    return render_template(
        'index.html',
        total_items=total_items,
        open_lost=open_lost,
        open_found=open_found,
        returned_items=returned_items,
        recovery_rate=recovery_rate,
        recent_items=recent_items,
        top_locations=top_locations,
        user_match_count=user_match_count
    )

# -------------------------------------------------------------
# BROWSE & SEARCH
# -------------------------------------------------------------

@app.route('/browse')
def browse():
    q = request.args.get('q', '').strip()
    item_type = request.args.get('type', 'ALL').upper()
    category = request.args.get('category', 'ALL')
    location = request.args.get('location', 'ALL')
    status = request.args.get('status', 'ALL').upper()
    sort = request.args.get('sort', 'newest')

    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT i.*, u.name as reporter_name, u.role as reporter_role,
           (SELECT COUNT(*) FROM saved_items s WHERE s.item_id = i.id AND s.user_id = ?) as is_saved
    FROM items i
    JOIN users u ON i.user_id = u.id
    WHERE i.status != 'ARCHIVED'
    """
    params = [session.get('user_id', 0)]

    if q:
        query += " AND (i.title LIKE ? OR i.description LIKE ? OR i.location LIKE ?)"
        term = f"%{q}%"
        params.extend([term, term, term])

    if item_type in ('LOST', 'FOUND'):
        query += " AND i.type = ?"
        params.append(item_type)

    if category != 'ALL':
        query += " AND i.category = ?"
        params.append(category)

    if location != 'ALL':
        query += " AND i.location = ?"
        params.append(location)

    if status != 'ALL':
        query += " AND i.status = ?"
        params.append(status)

    if sort == 'oldest':
        query += " ORDER BY i.created_at ASC"
    elif sort == 'views':
        query += " ORDER BY i.view_count DESC"
    else:
        query += " ORDER BY i.created_at DESC"

    cursor.execute(query, params)
    items = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        'browse.html',
        items=items,
        q=q,
        item_type=item_type,
        category=category,
        location=location,
        status=status,
        sort=sort
    )

# -------------------------------------------------------------
# REPORT ITEM (LOST OR FOUND)
# -------------------------------------------------------------

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_item():
    default_type = request.args.get('type', 'LOST').upper()
    if default_type not in ('LOST', 'FOUND'):
        default_type = 'LOST'

    if request.method == 'POST':
        item_type = request.form.get('type', default_type).upper()
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        location = request.form.get('location', '').strip()
        item_date = request.form.get('item_date', '').strip()
        item_time = request.form.get('item_time', '').strip()
        description = request.form.get('description', '').strip()
        private_details = request.form.get('private_details', '').strip()
        contact_method = request.form.get('contact_method', 'In-App Handover Chat').strip()

        if not title or not category or not location or not item_date or not description:
            flash('Please fill in all mandatory fields.', 'danger')
            return render_template('report.html', default_type=item_type)

        image_path = ''
        file = request.files.get('image')
        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(f"{session['user_id']}_{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_path = filename
            else:
                flash('Unsupported image format. Allowed: JPG, PNG, WEBP, GIF.', 'warning')

        # Fallback category SVG if no image uploaded
        if not image_path:
            cat_lower = category.lower()
            if 'bottle' in cat_lower or 'tumbler' in cat_lower:
                image_path = 'bottle_blue.svg'
            elif 'wallet' in cat_lower or 'card' in cat_lower:
                image_path = 'wallet_leather.svg'
            elif 'calculator' in cat_lower:
                image_path = 'calculator_casio.svg'
            elif 'electronics' in cat_lower or 'gadget' in cat_lower:
                image_path = 'macbook_laptop.svg'
            elif 'key' in cat_lower:
                image_path = 'keys_batman.svg'
            elif 'id' in cat_lower:
                image_path = 'id_card.svg'

        # Resolve latitude and longitude from form or location lookup
        lat = request.form.get('latitude', type=float)
        lng = request.form.get('longitude', type=float)
        if not lat or not lng:
            coords = CAMPUS_LOCATION_COORDS.get(location, CAMPUS_CENTER)
            lat = coords['lat']
            lng = coords['lng']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO items (
            user_id, type, title, category, description, private_details,
            location, latitude, longitude, item_date, item_time, contact_method, image_path, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
        """, (
            session['user_id'], item_type, title, category, description,
            private_details, location, lat, lng, item_date, item_time, contact_method, image_path
        ))
        conn.commit()
        new_item_id = cursor.lastrowid

        # Scan for instant smart matches
        cursor.execute("SELECT * FROM items WHERE id = ?", (new_item_id,))
        new_item = dict(cursor.fetchone())

        cursor.execute("SELECT * FROM items WHERE id != ? AND status != 'ARCHIVED'", (new_item_id,))
        all_candidates = [dict(r) for r in cursor.fetchall()]

        matches = find_smart_matches(new_item, all_candidates, min_threshold=55)

        # Notify user and opposite owners if high match found
        for match in matches:
            matched_item = match['item']
            score = match['match_score']
            if score >= 65:
                # Notify creator
                cursor.execute("""
                INSERT INTO notifications (user_id, title, message, link, type)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    session['user_id'],
                    f"Possible Match ({score}%) Found!",
                    f"Your reported {item_type.lower()} item '{title}' has a strong match: '{matched_item['title']}' reported in {matched_item['location']}.",
                    f"/item/{matched_item['id']}",
                    'match'
                ))
                # Notify the other reporter
                cursor.execute("""
                INSERT INTO notifications (user_id, title, message, link, type)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    matched_item['user_id'],
                    f"Smart Match ({score}%) for your report",
                    f"Someone reported a matching {item_type.lower()} item '{title}' at {location}.",
                    f"/item/{new_item_id}",
                    'match'
                ))

        conn.commit()
        conn.close()

        flash(f"Successfully published your {item_type} report: '{title}'.", 'success')
        return redirect(url_for('item_detail', item_id=new_item_id))

    return render_template('report.html', default_type=default_type)

# -------------------------------------------------------------
# ITEM DETAILS
# -------------------------------------------------------------

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    conn = get_db()
    cursor = conn.cursor()

    # Increment view count
    cursor.execute("UPDATE items SET view_count = view_count + 1 WHERE id = ?", (item_id,))
    conn.commit()

    cursor.execute("""
    SELECT i.*, u.name as reporter_name, u.email as reporter_email, u.role as reporter_role,
           u.department as reporter_dept, u.usn as reporter_usn
    FROM items i
    JOIN users u ON i.user_id = u.id
    WHERE i.id = ?
    """, (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        flash('The requested item was not found.', 'warning')
        return redirect(url_for('browse'))

    item = dict(item)

    # Check if saved by current user
    is_saved = False
    user_claim = None
    if 'user_id' in session:
        cursor.execute("SELECT id FROM saved_items WHERE user_id = ? AND item_id = ?", (session['user_id'], item_id))
        is_saved = cursor.fetchone() is not None

        cursor.execute("SELECT * FROM claims WHERE item_id = ? AND claimant_id = ?", (item_id, session['user_id']))
        row = cursor.fetchone()
        if row:
            user_claim = dict(row)

    # Existing claims on this item (visible to reporter or admin)
    item_claims = []
    if 'user_id' in session and (session['user_id'] == item['user_id'] or session.get('role') == 'admin'):
        cursor.execute("""
        SELECT c.*, u.name as claimant_name, u.email as claimant_email, u.usn as claimant_usn, u.department as claimant_dept
        FROM claims c
        JOIN users u ON c.claimant_id = u.id
        WHERE c.item_id = ?
        ORDER BY c.created_at DESC
        """, (item_id,))
        item_claims = [dict(r) for r in cursor.fetchall()]

    # Smart Matching suggestions
    cursor.execute("SELECT * FROM items WHERE id != ? AND status != 'ARCHIVED'", (item_id,))
    other_items = [dict(r) for r in cursor.fetchall()]
    smart_matches = find_smart_matches(item, other_items, min_threshold=45)[:3]

    conn.close()

    return render_template(
        'item_detail.html',
        item=item,
        is_saved=is_saved,
        user_claim=user_claim,
        item_claims=item_claims,
        smart_matches=smart_matches
    )

# -------------------------------------------------------------
# CLAIM AND VERIFICATION WORKFLOW
# -------------------------------------------------------------

@app.route('/item/<int:item_id>/claim', methods=['POST'])
@login_required
def claim_item(item_id):
    proof_description = request.form.get('proof_description', '').strip()
    identifying_answers = request.form.get('identifying_answers', '').strip()
    contact_note = request.form.get('contact_note', '').strip()

    if not proof_description:
        flash('Please provide sufficient proof details to verify ownership.', 'danger')
        return redirect(url_for('item_detail', item_id=item_id))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        flash('Item not found.', 'warning')
        return redirect(url_for('browse'))

    if item['user_id'] == session['user_id']:
        conn.close()
        flash('You cannot claim an item that you reported yourself.', 'warning')
        return redirect(url_for('item_detail', item_id=item_id))

    # Check if existing pending claim
    cursor.execute("SELECT id FROM claims WHERE item_id = ? AND claimant_id = ?", (item_id, session['user_id']))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        flash('You have already submitted a claim for this item.', 'info')
        return redirect(url_for('item_detail', item_id=item_id))

    # Insert claim
    cursor.execute("""
    INSERT INTO claims (item_id, claimant_id, proof_description, identifying_answers, contact_note, status)
    VALUES (?, ?, ?, ?, ?, 'PENDING')
    """, (item_id, session['user_id'], proof_description, identifying_answers, contact_note))
    claim_id = cursor.lastrowid

    # Update item status to CLAIM_PENDING if currently OPEN
    if item['status'] == 'OPEN':
        cursor.execute("UPDATE items SET status = 'CLAIM_PENDING' WHERE id = ?", (item_id,))

    # Notify finder / reporter
    cursor.execute("""
    INSERT INTO notifications (user_id, title, message, link, type)
    VALUES (?, ?, ?, ?, ?)
    """, (
        item['user_id'],
        f"New Claim Request for '{item['title']}'",
        f"{session['user_name']} submitted an ownership verification claim. Please review their answers in the Claims Center.",
        '/claims',
        'claim'
    ))

    # Also notify admins
    cursor.execute("SELECT id FROM users WHERE role = 'admin'")
    for admin_row in cursor.fetchall():
        if admin_row['id'] != item['user_id']:
            cursor.execute("""
            INSERT INTO notifications (user_id, title, message, link, type)
            VALUES (?, ?, ?, ?, ?)
            """, (
                admin_row['id'],
                f"Ownership Claim Filed on Item #{item_id}",
                f"Claimant {session['user_name']} filed a claim for {item['title']}.",
                '/claims',
                'claim'
            ))

    # Initial greeting in handover message
    cursor.execute("""
    INSERT INTO messages (claim_id, item_id, sender_id, recipient_id, message)
    VALUES (?, ?, ?, ?, ?)
    """, (
        claim_id, item_id, session['user_id'], item['user_id'],
        f"Hi, I submitted an ownership claim for '{item['title']}'. Looking forward to coordinating the verification and safe handover."
    ))

    conn.commit()
    conn.close()

    flash('Ownership claim successfully submitted. The reporter/admin has been notified to verify your proof.', 'success')
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/claims')
@login_required
def claims():
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    conn = get_db()
    cursor = conn.cursor()

    # 1. Claims submitted BY me
    cursor.execute("""
    SELECT c.*, i.title as item_title, i.type as item_type, i.location as item_location,
           i.image_path as item_image, i.status as item_status, u.name as reporter_name
    FROM claims c
    JOIN items i ON c.item_id = i.id
    JOIN users u ON i.user_id = u.id
    WHERE c.claimant_id = ?
    ORDER BY c.created_at DESC
    """, (user_id,))
    my_claims = [dict(r) for r in cursor.fetchall()]

    # 2. Claims received on items reported BY me (or ALL claims if admin)
    if is_admin:
        cursor.execute("""
        SELECT c.*, i.title as item_title, i.type as item_type, i.location as item_location,
               i.image_path as item_image, i.status as item_status, i.private_details,
               u.name as claimant_name, u.email as claimant_email, u.usn as claimant_usn,
               u.department as claimant_dept, rep.name as reporter_name
        FROM claims c
        JOIN items i ON c.item_id = i.id
        JOIN users u ON c.claimant_id = u.id
        JOIN users rep ON i.user_id = rep.id
        ORDER BY c.created_at DESC
        """)
    else:
        cursor.execute("""
        SELECT c.*, i.title as item_title, i.type as item_type, i.location as item_location,
               i.image_path as item_image, i.status as item_status, i.private_details,
               u.name as claimant_name, u.email as claimant_email, u.usn as claimant_usn,
               u.department as claimant_dept
        FROM claims c
        JOIN items i ON c.item_id = i.id
        JOIN users u ON c.claimant_id = u.id
        WHERE i.user_id = ?
        ORDER BY c.created_at DESC
        """, (user_id,))
    incoming_claims = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return render_template(
        'claims.html',
        my_claims=my_claims,
        incoming_claims=incoming_claims,
        is_admin=is_admin
    )

@app.route('/claim/<int:claim_id>/action', methods=['POST'])
@login_required
def claim_action(claim_id):
    action = request.form.get('action', '').upper()
    decision_note = request.form.get('decision_note', '').strip()

    if action not in ('APPROVED', 'REJECTED', 'RETURNED'):
        flash('Invalid claim decision action.', 'danger')
        return redirect(url_for('claims'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT c.*, i.user_id as item_owner_id, i.title as item_title, i.id as item_id,
           u.name as claimant_name
    FROM claims c
    JOIN items i ON c.item_id = i.id
    JOIN users u ON c.claimant_id = u.id
    WHERE c.id = ?
    """, (claim_id,))
    claim = cursor.fetchone()

    if not claim:
        conn.close()
        flash('Claim record not found.', 'warning')
        return redirect(url_for('claims'))

    # Only item owner or admin can decide
    is_owner = claim['item_owner_id'] == session['user_id']
    is_admin = session.get('role') == 'admin'

    if not (is_owner or is_admin):
        conn.close()
        flash('You are not authorized to decide on this claim.', 'danger')
        return redirect(url_for('claims'))

    # Update claim
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE claims
    SET status = ?, decision_note = ?, decided_by = ?, updated_at = ?
    WHERE id = ?
    """, (action, decision_note, session['user_id'], now, claim_id))

    # If approved or returned, update item status
    if action == 'RETURNED':
        cursor.execute("UPDATE items SET status = 'RETURNED', resolved_at = ? WHERE id = ?", (now, claim['item_id']))
    elif action == 'APPROVED':
        # Mark other pending claims on same item as rejected or keep pending
        cursor.execute("UPDATE items SET status = 'CLAIM_PENDING' WHERE id = ?", (claim['item_id'],))
    elif action == 'REJECTED':
        # If no other pending claims, reset item status to OPEN
        cursor.execute("SELECT COUNT(*) FROM claims WHERE item_id = ? AND status = 'PENDING' AND id != ?", (claim['item_id'], claim_id))
        pending_count = cursor.fetchone()[0]
        if pending_count == 0:
            cursor.execute("UPDATE items SET status = 'OPEN' WHERE id = ?", (claim['item_id'],))

    # Send Notification to Claimant
    status_label = "Approved" if action == 'APPROVED' else ("Marked as Returned" if action == 'RETURNED' else "Declined")
    notif_msg = f"Your ownership claim for '{claim['item_title']}' was {status_label}."
    if decision_note:
        notif_msg += f" Note: {decision_note}"

    cursor.execute("""
    INSERT INTO notifications (user_id, title, message, link, type)
    VALUES (?, ?, ?, ?, ?)
    """, (
        claim['claimant_id'],
        f"Claim {status_label}: {claim['item_title']}",
        notif_msg,
        f"/item/{claim['item_id']}",
        'approval' if action in ('APPROVED', 'RETURNED') else 'system'
    ))

    conn.commit()
    conn.close()

    flash(f"Claim #{claim_id} marked as {action}.", 'success')
    return redirect(url_for('claims'))

# -------------------------------------------------------------
# IN-APP HANDOVER MESSAGING
# -------------------------------------------------------------

@app.route('/messages/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item_messages(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT i.*, u.name as reporter_name, u.email as reporter_email
    FROM items i
    JOIN users u ON i.user_id = u.id
    WHERE i.id = ?
    """, (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        flash('Item not found.', 'warning')
        return redirect(url_for('browse'))

    item = dict(item)

    # Determine communication participants:
    # If current user is reporter, they can chat with claimant(s).
    # If current user is not reporter, they are communicating with reporter.
    current_user_id = session['user_id']
    partner_id = request.args.get('with', type=int)

    if current_user_id == item['user_id']:
        if not partner_id:
            # Pick latest claimant
            cursor.execute("SELECT claimant_id FROM claims WHERE item_id = ? ORDER BY created_at DESC LIMIT 1", (item_id,))
            claimant = cursor.fetchone()
            if claimant:
                partner_id = claimant['claimant_id']
            else:
                conn.close()
                flash('No claim or chat partner found for this item yet.', 'info')
                return redirect(url_for('item_detail', item_id=item_id))
    else:
        partner_id = item['user_id']

    cursor.execute("SELECT * FROM users WHERE id = ?", (partner_id,))
    chat_partner = cursor.fetchone()

    if not chat_partner:
        conn.close()
        flash('Chat recipient could not be found.', 'warning')
        return redirect(url_for('item_detail', item_id=item_id))

    chat_partner = dict(chat_partner)

    # Handle sending message
    if request.method == 'POST':
        message_text = request.form.get('message', '').strip()
        if message_text:
            cursor.execute("""
            INSERT INTO messages (item_id, sender_id, recipient_id, message)
            VALUES (?, ?, ?, ?)
            """, (item_id, current_user_id, partner_id, message_text))

            # Notify recipient
            cursor.execute("""
            INSERT INTO notifications (user_id, title, message, link, type)
            VALUES (?, ?, ?, ?, ?)
            """, (
                partner_id,
                f"New Handover Message from {session['user_name']}",
                f"{session['user_name']} sent a message regarding '{item['title']}'",
                f"/messages/{item_id}?with={current_user_id}",
                'message'
            ))
            conn.commit()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                conn.close()
                return jsonify({'success': True})
            return redirect(url_for('item_messages', item_id=item_id, **({'with': partner_id} if current_user_id == item['user_id'] else {})))

    # Fetch conversation messages
    cursor.execute("""
    SELECT m.*, u.name as sender_name, u.role as sender_role
    FROM messages m
    JOIN users u ON m.sender_id = u.id
    WHERE m.item_id = ?
      AND ((m.sender_id = ? AND m.recipient_id = ?) OR (m.sender_id = ? AND m.recipient_id = ?))
    ORDER BY m.created_at ASC
    """, (item_id, current_user_id, partner_id, partner_id, current_user_id))
    messages = [dict(r) for r in cursor.fetchall()]

    # Mark as read
    cursor.execute("""
    UPDATE messages SET is_read = 1
    WHERE item_id = ? AND recipient_id = ? AND sender_id = ?
    """, (item_id, current_user_id, partner_id))
    conn.commit()

    conn.close()

    return render_template(
        'messages.html',
        item=item,
        chat_partner=chat_partner,
        messages=messages
    )

# -------------------------------------------------------------
# SMART MATCHES RADAR
# -------------------------------------------------------------

@app.route('/matches')
@login_required
def smart_matches_view():
    conn = get_db()
    cursor = conn.cursor()

    user_id = session['user_id']

    # Get user's open items
    cursor.execute("SELECT * FROM items WHERE user_id = ? AND status != 'ARCHIVED'", (user_id,))
    my_items = [dict(r) for r in cursor.fetchall()]

    # Get complementary items from others
    cursor.execute("SELECT * FROM items WHERE user_id != ? AND status != 'ARCHIVED'", (user_id,))
    other_items = [dict(r) for r in cursor.fetchall()]

    all_matched_pairs = []
    for my_item in my_items:
        matches = find_smart_matches(my_item, other_items, min_threshold=45)
        for m in matches:
            all_matched_pairs.append({
                'my_item': my_item,
                'matched_item': m['item'],
                'score': m['match_score'],
                'reasons': m['reasons']
            })

    # Sort descending by match score
    all_matched_pairs.sort(key=lambda x: x['score'], reverse=True)

    conn.close()

    return render_template('matches.html', match_pairs=all_matched_pairs, my_items_count=len(my_items))

# -------------------------------------------------------------
# CAMPUS MAP
# -------------------------------------------------------------

@app.route('/map')
def campus_map():
    selected_zone = request.args.get('zone', 'ALL')

    conn = get_db()
    cursor = conn.cursor()

    # Get count of items per campus location
    cursor.execute("""
    SELECT location,
           SUM(CASE WHEN type = 'LOST' AND status = 'OPEN' THEN 1 ELSE 0 END) as lost_count,
           SUM(CASE WHEN type = 'FOUND' AND status IN ('OPEN', 'CLAIM_PENDING') THEN 1 ELSE 0 END) as found_count,
           SUM(CASE WHEN status = 'RETURNED' THEN 1 ELSE 0 END) as returned_count,
           COUNT(*) as total_count
    FROM items
    WHERE status != 'ARCHIVED'
    GROUP BY location
    """)
    zone_stats = {row['location']: dict(row) for row in cursor.fetchall()}

    # Items in selected zone
    if selected_zone != 'ALL':
        cursor.execute("""
        SELECT i.*, u.name as reporter_name
        FROM items i
        JOIN users u ON i.user_id = u.id
        WHERE i.location = ? AND i.status != 'ARCHIVED'
        ORDER BY i.created_at DESC
        """, (selected_zone,))
    else:
        cursor.execute("""
        SELECT i.*, u.name as reporter_name
        FROM items i
        JOIN users u ON i.user_id = u.id
        WHERE i.status != 'ARCHIVED'
        ORDER BY i.created_at DESC LIMIT 12
        """)
    zone_items = [dict(r) for r in cursor.fetchall()]

    # All items with coordinates for Google Maps markers
    cursor.execute("""
    SELECT i.id, i.title, i.type, i.category, i.location, i.latitude, i.longitude,
           i.image_path, i.status, i.item_date, u.name as reporter_name
    FROM items i
    JOIN users u ON i.user_id = u.id
    WHERE i.status != 'ARCHIVED'
    """)
    map_markers = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return render_template(
        'map.html',
        zone_stats=zone_stats,
        zone_items=zone_items,
        selected_zone=selected_zone,
        map_markers=map_markers
    )

@app.route('/api/map-markers')
def api_map_markers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT i.id, i.title, i.type, i.category, i.location, i.latitude, i.longitude,
           i.image_path, i.status, i.item_date, u.name as reporter_name
    FROM items i
    JOIN users u ON i.user_id = u.id
    WHERE i.status != 'ARCHIVED'
    """)
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()

    buildings = []
    for loc_name, coords in CAMPUS_LOCATION_COORDS.items():
        buildings.append({
            'name': loc_name,
            'lat': coords['lat'],
            'lng': coords['lng'],
            'desc': coords.get('desc', '')
        })

    return jsonify({
        'center': CAMPUS_CENTER,
        'buildings': buildings,
        'items': items
    })

@app.route('/api/set-maps-key', methods=['POST'])
def api_set_maps_key():
    data = request.get_json() or {}
    key = data.get('api_key', '').strip()
    session['user_google_maps_key'] = key
    return jsonify({'success': True, 'key_set': bool(key)})

# -------------------------------------------------------------
# USER PROFILE & MY REPORTS
# -------------------------------------------------------------

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())

    # User's items
    cursor.execute("SELECT * FROM items WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    my_items = [dict(r) for r in cursor.fetchall()]

    # User's saved items
    cursor.execute("""
    SELECT i.*, u.name as reporter_name
    FROM saved_items s
    JOIN items i ON s.item_id = i.id
    JOIN users u ON i.user_id = u.id
    WHERE s.user_id = ?
    ORDER BY s.created_at DESC
    """, (user_id,))
    saved_items = [dict(r) for r in cursor.fetchall()]

    # Feedback ratings given to or by user
    cursor.execute("""
    SELECT f.*, u.name as reviewer_name
    FROM feedback f
    JOIN users u ON f.user_id = u.id
    ORDER BY f.created_at DESC LIMIT 5
    """)
    recent_feedbacks = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return render_template(
        'profile.html',
        user=user,
        my_items=my_items,
        saved_items=saved_items,
        recent_feedbacks=recent_feedbacks
    )

@app.route('/saved')
@login_required
def saved_items():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT i.*, u.name as reporter_name
    FROM saved_items s
    JOIN items i ON s.item_id = i.id
    JOIN users u ON i.user_id = u.id
    WHERE s.user_id = ?
    ORDER BY s.created_at DESC
    """, (user_id,))
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return render_template('browse.html', items=items, is_bookmarks_view=True)

# -------------------------------------------------------------
# NOTIFICATIONS
# -------------------------------------------------------------

@app.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (user_id,))
    all_notifs = [dict(r) for r in cursor.fetchall()]

    # Mark all read
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    return render_template('notifications.html', notifications=all_notifs)

# -------------------------------------------------------------
# ADMIN DASHBOARD
# -------------------------------------------------------------

@app.route('/admin')
@admin_required
def admin_panel():
    conn = get_db()
    cursor = conn.cursor()

    # KPI counts
    cursor.execute("SELECT COUNT(*) FROM items")
    total_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'RETURNED'")
    returned_items = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'PENDING'")
    pending_claims = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Moderation items list
    cursor.execute("""
    SELECT i.*, u.name as reporter_name, u.email as reporter_email, u.usn as reporter_usn
    FROM items i
    JOIN users u ON i.user_id = u.id
    ORDER BY i.created_at DESC LIMIT 20
    """)
    all_items = [dict(r) for r in cursor.fetchall()]

    # Recent claims list
    cursor.execute("""
    SELECT c.*, i.title as item_title, u.name as claimant_name
    FROM claims c
    JOIN items i ON c.item_id = i.id
    JOIN users u ON c.claimant_id = u.id
    ORDER BY c.created_at DESC LIMIT 15
    """)
    claims_list = [dict(r) for r in cursor.fetchall()]

    # Users list
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 25")
    users_list = [dict(r) for r in cursor.fetchall()]

    # Feedback list
    cursor.execute("""
    SELECT f.*, u.name as reviewer_name
    FROM feedback f
    JOIN users u ON f.user_id = u.id
    ORDER BY f.created_at DESC LIMIT 10
    """)
    feedbacks = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return render_template(
        'admin.html',
        total_items=total_items,
        returned_items=returned_items,
        pending_claims=pending_claims,
        total_users=total_users,
        items=all_items,
        claims=claims_list,
        users=users_list,
        feedbacks=feedbacks
    )

@app.route('/admin/item/<int:item_id>/moderate', methods=['POST'])
@admin_required
def admin_moderate_item(item_id):
    action = request.form.get('action') # 'ARCHIVE', 'DELETE', 'RESTORE'
    conn = get_db()
    cursor = conn.cursor()

    if action == 'DELETE':
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        flash(f'Report #{item_id} permanently removed.', 'warning')
    elif action == 'ARCHIVE':
        cursor.execute("UPDATE items SET status = 'ARCHIVED' WHERE id = ?", (item_id,))
        flash(f'Report #{item_id} archived.', 'info')
    elif action == 'RESTORE':
        cursor.execute("UPDATE items SET status = 'OPEN' WHERE id = ?", (item_id,))
        flash(f'Report #{item_id} restored to active listings.', 'success')

    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

# -------------------------------------------------------------
# AJAX / API ENDPOINTS
# -------------------------------------------------------------

@app.route('/api/check-duplicates', methods=['POST'])
def api_check_duplicates():
    data = request.get_json() or {}
    new_item = {
        'title': data.get('title', ''),
        'category': data.get('category', ''),
        'type': data.get('type', 'LOST'),
        'description': data.get('description', ''),
        'location': data.get('location', ''),
        'item_date': data.get('item_date', '')
    }

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE status != 'ARCHIVED' AND type = ?", (new_item['type'],))
    existing = [dict(r) for r in cursor.fetchall()]
    conn.close()

    duplicates = detect_potential_duplicates(new_item, existing, threshold=60)
    results = []
    for d in duplicates[:3]:
        results.append({
            'id': d['item']['id'],
            'title': d['item']['title'],
            'score': d['score'],
            'location': d['item']['location'],
            'date': d['item']['item_date']
        })

    return jsonify({'duplicates': results})

@app.route('/api/save-item/<int:item_id>', methods=['POST'])
@login_required
def api_toggle_save(item_id):
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM saved_items WHERE user_id = ? AND item_id = ?", (user_id, item_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("DELETE FROM saved_items WHERE user_id = ? AND item_id = ?", (user_id, item_id))
        is_saved = False
    else:
        cursor.execute("INSERT INTO saved_items (user_id, item_id) VALUES (?, ?)", (user_id, item_id))
        is_saved = True

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'is_saved': is_saved})

@app.route('/api/feedback/<int:claim_id>', methods=['POST'])
@login_required
def api_submit_feedback(claim_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Please select a star rating between 1 and 5.', 'warning')
        return redirect(url_for('claims'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO feedback (claim_id, user_id, rating, comment)
    VALUES (?, ?, ?, ?)
    """, (claim_id, session['user_id'], rating, comment))
    conn.commit()
    conn.close()

    flash('Thank you for rating your recovery experience!', 'success')
    return redirect(url_for('claims'))

# Initialize database on app startup if needed
with app.app_context():
    init_db()

if __name__ == '__main__':
    print("=" * 60)
    print("  CAMPUS LOST & FOUND - ANTIGRAVITY WEB APPLICATION")
    print("  Server running on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
