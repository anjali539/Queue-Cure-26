import sqlite3
from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# =========================
# DATABASE SETUP
# =========================

def init_db():

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_no INTEGER,
        name TEXT,
        priority TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        current_token INTEGER,
        consultation_time INTEGER       
    )
    """)

    cur.execute("SELECT * FROM settings")

    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO settings(id,current_token,consultation_time) VALUES(1,0,5)"
        )

    conn.commit()
    conn.close()

init_db()

# =========================
# RECEPTIONIST DASHBOARD
# =========================

@app.route("/")
def receptionist():

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM patients
        ORDER BY
        CASE
        WHEN priority='Emergency' THEN 0
        ELSE 1
        END,
    token_no
    """)
    patients = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM patients")
    total_patients = cur.fetchone()[0]

    cur.execute(
        "SELECT current_token FROM settings WHERE id=1"
    )

    current_token = cur.fetchone()[0]

    cur.execute(
    "SELECT name FROM patients WHERE token_no=?",
    (current_token,)
    )

    patient = cur.fetchone()

    if patient:
        current_patient = patient[0]
    else:
        current_patient = "No Patient"

    cur.execute(
        """
        SELECT COUNT(*)
        FROM patients
        WHERE token_no <= ?
        """,
        (current_token,)
    )

    completed_patients = cur.fetchone()[0]

    waiting_patients = total_patients - completed_patients

    cur.execute(
    "SELECT consultation_time FROM settings WHERE id=1"
    )

    consultation_time = cur.fetchone()[0]
    conn.close()
    return render_template(
        "receptionist.html",
        patients=patients,
        current_token=current_token,
        total_patients=total_patients,
        current_patient=current_patient,
        completed_patients=completed_patients,
        waiting_patients=waiting_patients,
        consultation_time=consultation_time
    )

# =========================
# ADD PATIENT
# =========================

@app.route("/add_patient", methods=["POST"])
def add_patient():

    name = request.form["name"]
    priority = request.form["priority"]

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    # Duplicate Patient Check

    cur.execute(
        "SELECT * FROM patients WHERE name=?",
        (name,)
    )

    existing = cur.fetchone()

    if existing:
        conn.close()
        return "Patient Already Exists"

    cur.execute(
        "SELECT MAX(token_no) FROM patients"
    )

    result = cur.fetchone()[0]

    next_token = 1 if result is None else result + 1

    cur.execute(
        """
        INSERT INTO patients
        (token_no,name,priority)
        VALUES (?,?,?)
        """,
        (next_token, name, priority)
    )

    conn.commit()
    conn.close()

    socketio.emit("queue_updated")

    return redirect("/")

# =========================
# DELETE PATIENT
# =========================

@app.route("/delete_patient/<int:id>")
def delete_patient(id):

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM patients WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    socketio.emit("queue_updated")

    return redirect("/")

# =========================
# CALL NEXT TOKEN
# =========================
@app.route("/set_time", methods=["POST"])
def set_time():

    consultation_time = request.form["consultation_time"]

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE settings
        SET consultation_time=?
        WHERE id=1
        """,
        (consultation_time,)
    )

    conn.commit()
    conn.close()
    print("QUEUE UPDATED EVENT SENT")
    socketio.emit("queue_updated")

    return redirect("/")

@app.route("/call_next")
def call_next():

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT current_token FROM settings WHERE id=1"
    )

    current = cur.fetchone()[0]

    cur.execute("""
    SELECT token_no
    FROM patients
    WHERE token_no > ?
    ORDER BY    
    CASE
    WHEN priority='Emergency' THEN 0
    ELSE 1
    END,
    token_no
    LIMIT 1
    """, (current,))

    next_patient = cur.fetchone()

    if next_patient:
        current = next_patient[0]

    cur.execute(
        """
        UPDATE settings
        SET current_token=?
        WHERE id=1
        """,
        (current,)
    )

    conn.commit()
    conn.close()

    print("QUEUE UPDATED EVENT SENT")
    socketio.emit("queue_updated")

    return redirect("/")
@app.route("/reset")
def reset():

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM patients")

    cur.execute("""
    UPDATE settings
    SET current_token = 0
    WHERE id = 1
    """)

    conn.commit()
    conn.close()

    return redirect("/")
# =========================
# PATIENT VIEW
# =========================

@app.route("/patient")
def patient():

    conn = sqlite3.connect("queue.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT current_token FROM settings WHERE id=1"
    )

    current_token = cur.fetchone()[0]
    cur.execute(
        "SELECT name FROM patients WHERE token_no=?",
        (current_token,)
    )

    patient = cur.fetchone()

    if patient:
        current_patient = patient[0]
    else:
        current_patient = "No Patient"

    cur.execute(
        """
        SELECT COUNT(*)
        FROM patients
        WHERE token_no > ?
        """,
        (current_token,)
    )

    tokens_ahead = cur.fetchone()[0]

    cur.execute(
    "SELECT consultation_time FROM settings WHERE id=1"
)

    consultation_time = cur.fetchone()[0]

    wait_time = tokens_ahead * consultation_time

    cur.execute("SELECT COUNT(*) FROM patients")
    total_patients = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE token_no <= ?
        """, (current_token,))

    completed_patients = cur.fetchone()[0]

    if total_patients > 0:
        progress = int((completed_patients / total_patients) * 100)
    else:
        progress = 0

    conn.close()

    return render_template(
        "patient.html",
        current_token=current_token,
         current_patient=current_patient,
        tokens_ahead=tokens_ahead,
        wait_time=wait_time,
        progress=progress
    )

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    socketio.run(app, debug=True)