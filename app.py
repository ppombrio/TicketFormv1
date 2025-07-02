from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)
Talisman(app, content_security_policy={
    'default-src': ["'self'"],
    'style-src': ["'self'", 'https://cdn.jsdelivr.net'],
    'script-src': ["'self'", 'https://cdn.jsdelivr.net'],
})

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tickets.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or your SMTP provider
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

# Ticket model
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    parts = db.Column(db.String(200))
    location = db.Column(db.String(100))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Open')
    created_date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))

# Home page with form
@app.route('/', methods=['GET', 'POST'])
def submit_ticket():
    if request.method == 'POST':
        new_ticket = Ticket(
            name=request.form.get('name'),
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            parts=request.form.get('parts'),
            location=request.form.get('location'),
            priority=request.form.get('priority'),
            due_date=request.form.get('due_date'),
            created_date=datetime.today().strftime("%Y-%m-%d")
        )
        db.session.add(new_ticket)
        db.session.commit()

        # Send email notification
        msg = Message(subject="New Ticket Submitted",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=["your.email@example.com"],  # change this!
                      body=f"""
A new ticket has been submitted.

Name or Email: {new_ticket.name}
Title: {new_ticket.title}
Category: {new_ticket.category}
Priority: {new_ticket.priority}
Location: {new_ticket.location}
Description: {new_ticket.description}
Parts Needed: {new_ticket.parts}
Due Date: {new_ticket.due_date}
Submitted On: {new_ticket.created_date}
                      """)
        mail.send(msg)

        return redirect('/success')
    return render_template("form.html")

# Confirmation page
@app.route('/success')
def success():
    return "✅ Ticket submitted successfully."

# Admin view
@app.route('/tickets')
def view_tickets():
    tickets = Ticket.query.all()
    return render_template("tickets.html", tickets=tickets)

# CSV export
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

# One-time DB init
@app.route('/initdb')
def initdb():
    db.create_all()
    return "✅ Database initialized."

if __name__ == '__main__':
    app.run(debug=True)
