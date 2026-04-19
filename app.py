from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "change_me"

# INIT DB
def init_db():
    conn = sqlite3.connect('runs.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo TEXT,
            temps REAL,
            statut TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# HOME
@app.route('/')
def index():
    conn = sqlite3.connect('runs.db')
    c = conn.cursor()
    c.execute("SELECT pseudo, temps FROM runs WHERE statut='valide' ORDER BY temps ASC")
    runs = c.fetchall()
    conn.close()
    return render_template('index.html', runs=runs)

# SUBMIT
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        temps = request.form['temps']

        conn = sqlite3.connect('runs.db')
        c = conn.cursor()
        c.execute("INSERT INTO runs (pseudo, temps, statut) VALUES (?, ?, 'en_attente')",
                  (pseudo, temps))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('submit.html')

# LOGIN ADMIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == "admin123":
            session['admin'] = True
            return redirect('/admin')
    return render_template('login.html')

# ADMIN PAGE
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    conn = sqlite3.connect('runs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM runs WHERE statut='en_attente'")
    runs = c.fetchall()
    conn.close()

    return render_template('admin.html', runs=runs)

# VALIDATE
@app.route('/validate/<int:id>')
def validate(id):
    conn = sqlite3.connect('runs.db')
    c = conn.cursor()
    c.execute("UPDATE runs SET statut='valide' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# REJECT
@app.route('/reject/<int:id>')
def reject(id):
    conn = sqlite3.connect('runs.db')
    c = conn.cursor()
    c.execute("DELETE FROM runs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)