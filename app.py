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

# Utility to convert query results into list of dicts
def fetchall_dict(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

@app.before_request
def log_request():
    print("➡️ Request:", request.method, request.path)

# ---------------------------
# Signup and login endpoints
# ---------------------------

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


# ---------------------------
# Get all customers
# ---------------------------
@app.route("/customers", methods=["GET"])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, notes FROM customers")
    customers = fetchall_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(customers)


# ---------------------------
# Add new customer
# ---------------------------
@app.route("/customers", methods=["POST"])
def add_customer():
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")
    notes = data.get("notes", "")
    opening_balance = float(data.get("openingBalance", 0))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers (name, phone, notes) VALUES (%s, %s, %s)",
        (name, phone, notes)
    )
    conn.commit()
    customer_id = cursor.lastrowid

    # Add opening balance if needed
    if opening_balance > 0:
        cursor.execute(
            "INSERT INTO transactions (customer_id, date, type, amount, notes) VALUES (%s, CURDATE(), 'debit', %s, 'Opening Balance')",
            (customer_id, opening_balance)
        )
        conn.commit()

    cursor.close()
    conn.close()
    return jsonify({"success": True, "id": customer_id})


# ---------------------------
# Get transactions for customer
# ---------------------------
@app.route("/customers/<int:customer_id>/transactions", methods=["GET"])
def get_transactions(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_id, date, type, amount, notes FROM transactions WHERE customer_id = %s ORDER BY date DESC", (customer_id,))
    transactions = fetchall_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(transactions)


# ---------------------------
# Add transaction
# ---------------------------
@app.route("/transactions", methods=["POST"])
def add_transaction():
    data = request.get_json()
    customer_id = data.get("customerId")
    date = data.get("date")
    tx_type = data.get("type")
    amount = float(data.get("amount"))
    notes = data.get("notes", "")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (customer_id, date, type, amount, notes) VALUES (%s, %s, %s, %s, %s)",
        (customer_id, date, tx_type, amount, notes)
    )
    conn.commit()
    tx_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"success": True, "id": tx_id})


if __name__ == '__main__':
    app.run(debug=True)
