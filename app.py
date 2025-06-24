from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from datetime import datetime
import os

app = Flask(__name__)
Talisman(app, content_security_policy={
    'default-src': ["'self'"],
    'style-src': ["'self'", 'https://cdn.jsdelivr.net'],
    'script-src': ["'self'", 'https://cdn.jsdelivr.net'],

# Use PostgreSQL if DATABASE_URL is set; otherwise fall back to local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tickets.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ticket model
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    priority = db.Column(db.String(20))
    location = db.Column(db.String(200))
    urgent = db.Column(db.String(10))
    estimated_time = db.Column(db.Float)
    parts = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Open')
    created_date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))

@app.route('/download')
def download_csv():
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([col.name for col in Ticket.__table__.columns])
    for ticket in Ticket.query.all():
        writer.writerow([getattr(ticket, col.name) for col in Ticket.__table__.columns])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=tickets.csv"})

# Route to submit a ticket
@app.route('/', methods=['GET', 'POST'])
def submit_ticket():
    if request.method == 'POST':
        new_ticket = Ticket(
            name=request.form.get('name'),
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            priority=request.form.get('priority'),
            location=request.form.get('location'),
            urgent=request.form.get('urgent', 'No'),
            estimated_time=request.form.get('estimated_time') or None,
            parts=request.form.get('parts'),
            due_date=request.form.get('due_date'),
            created_date=datetime.today().strftime("%Y-%m-%d")
        )
        db.session.add(new_ticket)
        db.session.commit()
        return redirect('/success')
    return render_template("form.html")

# Confirmation page
@app.route('/success')
def success():
    return "✅ Ticket submitted successfully."

# Admin view of all tickets
@app.route('/tickets')
def view_tickets():
    tickets = Ticket.query.all()
    return render_template("tickets.html", tickets=tickets)

# One-time route to initialize database
@app.route('/initdb')
def initdb():
    db.create_all()
    return "✅ Database initialized."

if __name__ == '__main__':
    app.run(debug=True)
