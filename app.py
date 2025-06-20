from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from datetime import datetime
import os

app = Flask(__name__)
Talisman(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Ticket model
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    parts = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Open')
    created_date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))

# Create the database
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def submit_ticket():
    if request.method == 'POST':
        new_ticket = Ticket(
            name=request.form.get('name'),
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            parts=request.form.get('parts'),
            due_date=request.form.get('due_date'),
            created_date=datetime.today().strftime("%Y-%m-%d")
        )
        db.session.add(new_ticket)
        db.session.commit()
        return redirect('/success')

    return render_template("form.html")

@app.route('/success')
def success():
    return "✅ Ticket submitted successfully."

@app.route('/tickets')
def view_tickets():
    tickets = Ticket.query.all()
    return render_template("tickets.html", tickets=tickets)

if __name__ == '__main__':
    app.run(debug=True)
