from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",     # your MySQL password
        database="moneymate"
    )

# ---------- USER ROUTES ----------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Signup successful"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# ---------- SALES ENTRY ROUTES ----------
@app.route('/save_entry', methods=['POST'])
def save_entry():
    data = request.json
    entry_date = data.get("entryDate")
    sales_amount = float(data.get("salesAmount", 0))
    expenses = float(data.get("expenses", 0))
    retailer_payments = float(data.get("retailerPayments", 0))
    profit = sales_amount - expenses - retailer_payments
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales_entries (entry_date, sales_amount, expenses, retailer_payments, profit)
        VALUES (%s, %s, %s, %s, %s)
    """, (entry_date, sales_amount, expenses, retailer_payments, profit))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Entry saved successfully", "profit": profit}), 201

@app.route('/get_entries', methods=['GET'])
def get_entries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sales_entries ORDER BY entry_date DESC")
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(entries), 200

# ---------- RETAILER ROUTES ----------
# Add new retailer
@app.route('/add_retailer', methods=['POST'])
def add_retailer():
    data = request.json
    name = data.get("name")
    phone = data.get("phone", "")
    notes = data.get("notes", "")
    opening_balance = float(data.get("openingBalance", 0))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO retailers (name, phone, notes, opening_balance) VALUES (%s, %s, %s, %s)",
        (name, phone, notes, opening_balance)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Retailer added successfully"}), 201

# Get all retailers
@app.route('/get_retailers', methods=['GET'])
def get_retailers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM retailers")
    retailers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(retailers), 200

# Add purchase
@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    data = request.json
    retailer_id = data.get("retailer_id")
    amount = float(data.get("amount", 0))
    purchase_date = data.get("purchase_date")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO purchases (retailer_id, amount, purchase_date)
        VALUES (%s, %s, %s)
    """, (retailer_id, amount, purchase_date))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Purchase recorded successfully"}), 201

# Add settlement
@app.route('/add_settlement', methods=['POST'])
def add_settlement():
    data = request.json
    retailer_id = data.get("retailer_id")
    amount = float(data.get("amount", 0))
    settlement_date = data.get("settlement_date")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settlements (retailer_id, amount, settlement_date)
        VALUES (%s, %s, %s)
    """, (retailer_id, amount, settlement_date))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Settlement recorded successfully"}), 201

# Retailer summary
@app.route('/retailer/<int:retailer_id>', methods=['GET'])
def retailer_summary(retailer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT SUM(amount) AS total_purchases FROM purchases WHERE retailer_id=%s", (retailer_id,))
    total_purchases = cursor.fetchone()["total_purchases"] or 0
    cursor.execute("SELECT SUM(amount) AS total_settlements FROM settlements WHERE retailer_id=%s", (retailer_id,))
    total_settlements = cursor.fetchone()["total_settlements"] or 0
    balance = total_purchases - total_settlements
    cursor.close()
    conn.close()
    return jsonify({
        "retailer_id": retailer_id,
        "total_purchases": total_purchases,
        "total_settlements": total_settlements,
        "balance": balance
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
