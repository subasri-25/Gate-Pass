from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Users
users = {
    "student": {"password": "123", "role": "student"},
    "admin": {"password": "admin", "role": "admin"}
}

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Pending")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login_check', methods=['POST'])
def login_check():
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]["password"] == password:
        session['role'] = users[username]["role"]

        if session['role'] == "admin":
            return redirect('/admin')
        else:
            return redirect('/student')
    return "Invalid Login ❌"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/student')
def student():
    if session.get('role') != "student":
        return redirect('/login')

    requests = Request.query.all()
    return render_template("student.html", requests=requests)

@app.route('/admin')
def admin():
    if session.get('role') != "admin":
        return redirect('/login')

    requests = Request.query.all()
    return render_template("admin.html", requests=requests)

@app.route('/apply', methods=['POST'])
def apply():
    if session.get('role') != "student":
        return redirect('/login')

    data = Request(
        name=request.form['name'],
        reason=request.form['reason']
    )
    db.session.add(data)
    db.session.commit()
    return redirect('/student')

@app.route('/approve/<int:id>')
def approve(id):
    if session.get('role') != "admin":
        return redirect('/login')

    req = Request.query.get(id)
    req.status = "Approved"
    db.session.commit()
    return redirect('/admin')

@app.route('/deny/<int:id>')
def deny(id):
    if session.get('role') != "admin":
        return redirect('/login')

    req = Request.query.get(id)
    req.status = "Denied"
    db.session.commit()
    return redirect('/admin')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)