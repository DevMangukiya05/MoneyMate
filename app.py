from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",     # your MySQL password (if any)
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


if __name__ == '__main__':
    app.run(debug=True)
