from flask import Flask, request, jsonify, render_template
import pymysql

app = Flask(__name__, template_folder='.')

# Production Database Bindings
db_config = {
    'host': 'localhost',
    'user': 'root',       
    'password': 'vsvs',       # Change this to your MySQL password if different
    'database': 'shivapura_encyclopedia',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**db_config)

@app.route('/')
def home():
    return render_template('shivapura.html')

# Admin Authentication
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u, p = data.get('username'), data.get('password')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Admins WHERE username=%s AND password_hash=%s", (u, p))
            if cur.fetchone():
                return jsonify({"status": "success"})
            return jsonify({"status": "fail"}), 401
    finally:
        conn.close()

# The ultimate open endpoint that sends all factual data sections at once
@app.route('/api/village-encyclopedia', methods=['GET'])
def get_village_data():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT title, content, DATE_FORMAT(posted_date, '%d-%m-%Y') as date FROM Notices ORDER BY notice_id DESC")
            notices = cur.fetchall()
            
            cur.execute("SELECT category, item_name, details, price_or_time FROM RatesAndTimings")
            rates = cur.fetchall()
            
            cur.execute("SELECT category, place_name, timings, description FROM VillagePlaces")
            places = cur.fetchall()
            
            cur.execute("SELECT category, shop_or_crop_name, contact_or_rate, details FROM CommercialShops")
            commercial = cur.fetchall()
            
            cur.execute("SELECT profession, worker_name, phone_number FROM VillageWorkers")
            workers = cur.fetchall()
            
            return jsonify({
                "notices": notices,
                "rates": rates,
                "places": places,
                "commercial": commercial,
                "workers": workers
            })
    finally:
        conn.close()

# Administrative action to add a new live announcement
@app.route('/api/notices/add', methods=['POST'])
def add_notice():
    data = request.json
    t, c = data.get('title'), data.get('content')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Notices (title, content) VALUES (%s, %s)", (t, c))
            conn.commit()
            return jsonify({"status": "success"})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)