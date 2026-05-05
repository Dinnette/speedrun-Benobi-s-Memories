from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

app = Flask(__name__)
app.secret_key = "secret_key"

# --- DB INIT ---
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS runs (
    id SERIAL PRIMARY KEY,
    pseudo TEXT,
    temps REAL,
    statut TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# --- HOME (classement validé) ---
@app.route('/')
def index():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT pseudo, temps FROM runs WHERE statut='valide' ORDER BY temps ASC")
    runs = c.fetchall()
    conn.close()
    return render_template('index.html', runs=runs)

# --- SOUMETTRE RUN ---
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        temps = request.form['temps']

        conn = get_db_connection()
        c = conn.cursor()

        c.execute(
            "INSERT INTO runs (pseudo, temps, statut) VALUES (%s, %s, %s)",
            (pseudo, temps, 'en_attente')
        )

        conn.commit()
        c.close()
        conn.close()

        return redirect('/')

    return render_template('submit.html')

# --- LOGIN ADMIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == "admin123":
            session['admin'] = True
            return redirect('/admin')
    return render_template('login.html')

# --- ADMIN PANEL ---
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM runs WHERE statut='en_attente'")
    pending = c.fetchall()

    c.execute("SELECT * FROM runs WHERE statut='valide'")
    valid = c.fetchall()

    conn.close()

    return render_template('admin.html', pending=pending, valid=valid)

# --- VALIDER ---
@app.route('/validate/<int:id>')
def validate(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE runs SET statut='valide' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# --- REFUSER ---
@app.route('/reject/<int:id>')
def reject(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM runs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# --- SUPPRIMER ---
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM runs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)


# ================= HTML FILES (STYLÉ) =================

# templates/index.html
"""
<!DOCTYPE html>
<html>
<head>
<title>Speedrun Leaderboard</title>
<style>
body {background:#0f172a; color:white; font-family:Arial; text-align:center;}
h1 {color:#38bdf8;}
table {margin:auto; border-collapse:collapse; width:60%; background:#1e293b;}
th, td {padding:12px; border-bottom:1px solid #334155;}
th {background:#020617;}
tr:hover {background:#334155;}
a {color:#38bdf8; text-decoration:none;}
.button {background:#38bdf8; padding:10px; border-radius:8px; color:black; display:inline-block; margin:10px;}
</style>
</head>
<body>
<h1>🏆 Speedrun Leaderboard</h1>
<a class="button" href="/submit">➕ Submit Run</a>
<table>
<tr><th>#</th><th>Pseudo</th><th>Temps</th></tr>
{% for run in runs %}
<tr>
<td>{{ loop.index }}</td>
<td>{{ run[0] }}</td>
<td>{{ run[1] }} s</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

# templates/submit.html
"""
<!DOCTYPE html>
<html>
<body style="background:#0f172a;color:white;text-align:center;font-family:Arial;">
<h1>Submit Run</h1>
<form method="post">
<input name="pseudo" placeholder="Pseudo"><br><br>
<input name="temps" placeholder="Temps (secondes)"><br><br>
<button>Envoyer</button>
</form>
</body>
</html>
"""

# templates/login.html
"""
<!DOCTYPE html>
<html>
<body style="background:#0f172a;color:white;text-align:center;font-family:Arial;">
<h1>Admin Login</h1>
<form method="post">
<input type="password" name="password" placeholder="Mot de passe"><br><br>
<button>Connexion</button>
</form>
</body>
</html>
"""

# templates/admin.html
"""
<!DOCTYPE html>
<html>
<body style="background:#0f172a;color:white;font-family:Arial;text-align:center;">
<h1>Admin Panel</h1>

<h2>Runs en attente</h2>
{% for run in pending %}
<p>{{ run[1] }} - {{ run[2] }}s 
<a href="/validate/{{ run[0] }}">✅</a> 
<a href="/reject/{{ run[0] }}">❌</a></p>
{% endfor %}

<h2>Runs validés</h2>
{% for run in valid %}
<p>{{ run[1] }} - {{ run[2] }}s 
<a href="/delete/{{ run[0] }}">🗑</a></p>
{% endfor %}

</body>
</html>
"""
