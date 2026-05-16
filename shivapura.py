from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__, template_folder='.')

# Use Vercel's allowed writable temporary directory
DB_FILE = '/tmp/shivapura.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Notices (
        notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS RatesAndTimings (
        rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        item_name TEXT NOT NULL,
        details TEXT NOT NULL,
        price_or_time TEXT NOT NULL)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS VillagePlaces (
        place_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        place_name TEXT NOT NULL,
        timings TEXT NOT NULL,
        description TEXT)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS CommercialShops (
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        shop_or_crop_name TEXT NOT NULL,
        contact_or_rate TEXT NOT NULL,
        details TEXT)''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS VillageWorkers (
        worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
        profession TEXT NOT NULL,
        worker_name TEXT NOT NULL,
        phone_number TEXT NOT NULL)''')

    # Seed initial data if the database tables are brand new
    cursor.execute("SELECT COUNT(*) FROM RatesAndTimings")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO RatesAndTimings (category, item_name, details, price_or_time) VALUES (?, ?, ?, ?)", [
            ('Bus', 'Shivapura ➔ Kudligi Town (7 km)', 'KSRTC Ordinary Schedule - Morning Bus', '07:45 AM'),
            ('Bus', 'Kudligi Town ➔ Shivapura (7 km)', 'KSRTC Ordinary Schedule - Afternoon Return', '01:30 PM'),
            ('Bus', 'Shivapura ➔ Hosapete Junction (60 km)', 'Direct Route via National Highway 50 (NH-50)', '06:30 AM'),
            ('Bus', 'Shivapura ➔ Toranagallu Junction (58 km)', 'Connecting Railway Route Express', '08:15 AM'),
            ('Auto', 'Shivapura Main Circle to Kudligi Bus Stand', 'Local Shared Auto (Per Seat Fare)', '₹30'),
            ('Auto', 'Shivapura Area to Private Farm/Mane', 'Private Auto Hire (Full Ride)', '₹100 - ₹150'),
            ('Water', 'RO Filter Water Plant (ಗ್ರಾಮದ ಶುದ್ಧ ಕುಡಿಯುವ ನೀರು)', 'Panchayat Plant - Can capacity: 20 Litres', '₹5 per Can')
        ])
        
        cursor.executemany("INSERT INTO VillagePlaces (category, place_name, timings, description) VALUES (?, ?, ?, ?)", [
            ('Info', 'Geographic Profile (ಗ್ರಾಮದ ವಿವರ)', 'PIN: 583135', 'Situated in Kudligi Taluk, Vijayanagara District (formerly Bellary District). Elevation: 533 meters above sea level. Located 7 km from Kudligi and 77 km from the district headquarters. Surrounded by Jagalur (South), Molakalmuru (East), and Sandur (North) Taluks. Flows in the vicinity of the Tungabhadra River.'),
            ('Panchayat', 'Shivapura Grama Panchayat Office', '10:00 AM - 05:30 PM', 'Administrative hub falling under Kudligi Vidhan Sabha constituency and Ballari Lok Sabha constituency.'),
            ('School', 'Government Higher Primary School Shivapura', '09:30 AM - 04:30 PM', 'Local village educational institution.'),
            ('Hospital', 'Primary Health Sub-Center (ಆರೋಗ್ಯ কেন্দ্র)', '09:00 AM - 01:00 PM', 'Basic healthcare, emergencies, and free government medical drops.'),
            ('Library', 'Grama Panchayat Public Library', '04:00 PM - 07:00 PM', 'Daily Kannada newspapers, magazines, and educational books for village youths.')
        ])
        
        cursor.executemany("INSERT INTO CommercialShops (category, shop_or_crop_name, contact_or_rate, details) VALUES (?, ?, ?, ?)", [
            ('Kirani', 'Sri Manjunatha Provision Store (ಕಿರಾಣಿ ಅಂಗಡಿ)', 'Call: 9876543201', 'Wholesale groceries, household utilities, and farm goods.'),
            ('Kirani', 'Basava Provision Store', 'Call: 8877665544', 'Daily essentials, milk, and fresh vegetables.'),
            ('Medical', 'Maruthi Medical & General Stores', 'Call: 9900112233', 'Emergency medicines and prescription drop access.'),
            ('Market', 'Groundnut (ಕಡಲೇಕಾಯಿ) - APMC Kudligi Rate', '₹6,800 - ₹7,500', 'Current estimated market rate tracking per Quintal (ಮಾರುಕಟ್ಟೆ ಧಾರಣೆ)'),
            ('Market', 'Maize (ಮೆಕ್ಕೆಜೋಳ) - APMC Kudligi Rate', '₹2,100 - ₹2,400', 'Current estimated market rate tracking per Quintal (ಮಾರುಕಟ್ಟೆ ಧಾರಣೆ)')
        ])
        
        cursor.executemany("INSERT INTO VillageWorkers (profession, worker_name, phone_number) VALUES (?, ?, ?)", [
            ('Electrician', 'Ramesh (BESCOM Line Operator)', '9448001122'),
            ('Waterman', 'Mallesh (Panchayat Water Supply)', '7766554433'),
            ('Auto Driver', 'Anand (Kudligi Route Specialist)', '9845511223')
        ])
        
        cursor.execute("INSERT INTO Notices (title, content) VALUES (?, ?)", 
                       ('ಶಿವಪುರ ಗ್ರಾಮ ಪೋರ್ಟಲ್ ಗೆ ಸುಸ್ವಾಗತ!', 'ನಮ್ಮ ಗ್ರಾಮದ ಬಸ್ ಸಮಯಗಳು, ಆಟೋ ದರಗಳು, ಪಂಚಾಯತ್ ಕಚೇರಿ ಮಾಹಿತಿ ಮತ್ತು ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ದರಗಳನ್ನು ಇಲ್ಲಿ ಮುಕ್ತವಾಗಿ ವೀಕ್ಷಿಸಿ.'))
        
        conn.commit()
    conn.close()

# Initialize the database file upon boot
init_sqlite_db()

@app.route('/')
def home():
    return render_template('shivapura.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u, p = data.get('username'), data.get('password')
    if u == "admin" and p == "shivapura123":
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 401

@app.route('/api/village-encyclopedia', methods=['GET'])
def get_village_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    notices = [dict(row) for row in cursor.execute("SELECT title, content, strftime('%d-%m-%Y', posted_date) as date FROM Notices ORDER BY notice_id DESC").fetchall()]
    rates = [dict(row) for row in cursor.execute("SELECT category, item_name, details, price_or_time FROM RatesAndTimings").fetchall()]
    places = [dict(row) for row in cursor.execute("SELECT category, place_name, timings, description FROM VillagePlaces").fetchall()]
    commercial = [dict(row) for row in cursor.execute("SELECT category, shop_or_crop_name, contact_or_rate, details FROM CommercialShops").fetchall()]
    workers = [dict(row) for row in cursor.execute("SELECT profession, worker_name, phone_number FROM VillageWorkers").fetchall()]
    
    conn.close()
    return jsonify({
        "notices": notices,
        "rates": rates,
        "places": places,
        "commercial": commercial,
        "workers": workers
    })

@app.route('/api/notices/add', methods=['POST'])
def add_notice():
    data = request.json
    t, c = data.get('title'), data.get('content')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Notices (title, content) VALUES (?, ?)", (t, c))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# Expose the app object directly for Vercel
app = app
