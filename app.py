from flask import Flask, render_template, request, redirect, url_for, session
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# login page - all
@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("login.html")

# dashboard - all
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# employee+
@app.route("/equipment")
def equipment_list():
    return render_template("equipment.html")

@app.route("/customers")
def customer_list():
    return render_template("customer_list.html")

@app.route("/rentals")
def rental_list():
    return render_template("rental_list.html")

@app.route("/rentals/create")
def create_rental():
    return render_template("create_rental.html")

# admin
@app.route("/equipment/manage")
def manage_equipment():
    return render_template("manage_equipment.html")

@app.route("/reports/revenue")
def revenue_reports():
    return render_template("revenue_reports.html")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)