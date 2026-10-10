import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'antigravity-campus-lost-found-secret-key-2026')
    DATABASE = os.path.join(BASE_DIR, 'campus_lost_found.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max image upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

CAMPUS_CENTER = {
    'lat': 12.971598,
    'lng': 77.594566
}

CAMPUS_LOCATION_COORDS = {
    'Central Library': {
        'lat': 12.971598,
        'lng': 77.594566,
        'desc': '2nd Floor Reading Hall, Book Stacks & Digital Archive'
    },
    'Main Canteen / Food Court': {
        'lat': 12.972300,
        'lng': 77.593600,
        'desc': 'Central Student Dining & Beverage Counters'
    },
    'Computer Science & Tech Block': {
        'lat': 12.970900,
        'lng': 77.595400,
        'desc': 'Coding Labs, Seminar Halls & IT Server Rooms'
    },
    'Science & Engineering Labs': {
        'lat': 12.972800,
        'lng': 77.595300,
        'desc': 'Physics, Chemistry & Circuit Practical Laboratories'
    },
    'Admin & Registration Block': {
        'lat': 12.971100,
        'lng': 77.593300,
        'desc': 'Security Desk Room 102 & Student Affairs Office'
    },
    'Main Auditorium & Hall': {
        'lat': 12.970300,
        'lng': 77.594200,
        'desc': 'Main Convocation Amphitheatre & Event Stage'
    },
    'Sports Complex & Gym': {
        'lat': 12.973300,
        'lng': 77.592600,
        'desc': 'Indoor Badminton, Gymnasium & Track Grounds'
    },
    'Campus Student Hostels': {
        'lat': 12.973700,
        'lng': 77.594700,
        'desc': 'Dormitory Resident Quarters & Mess Hall'
    },
    'Bus Bay & Parking Area': {
        'lat': 12.969700,
        'lng': 77.595700,
        'desc': 'Campus Transit Shuttle Station & Vehicle Parking'
    },
    'Campus Garden & Quadrangle': {
        'lat': 12.971900,
        'lng': 77.594300,
        'desc': 'Central Courtyard Lawn & Discussion Pavilion'
    }
}

CAMPUS_LOCATIONS = list(CAMPUS_LOCATION_COORDS.keys())

ITEM_CATEGORIES = [
    'Electronics & Gadgets',
    'Student IDs & Cards',
    'Keys & Wallets',
    'Books & Study Materials',
    'Bags & Backpacks',
    'Bottles & Tumblers',
    'Clothing & Accessories',
    'Calculators & Stationery',
    'Others'
]

