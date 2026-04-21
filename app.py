import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import Base, User, engine, db_session
from security import hash_password, check_password, generate_salt, generate_key, encrypt_data, decrypt_data


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def get_logged_in_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db_session.query(User).filter_by(id=user_id).first()


# all
@app.route("/", methods=["GET", "POST"])
def login():
    errors = []

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = db_session.query(User).filter_by(username=username).first()
        if not user or not check_password(user.password_hash, password, user.salt):
            flash("Invalid username or password.")
            return render_template("login.html", form_data=request.form)

        session["user_id"] = user.id
        return render_template("dashboard.html")
    return render_template("login.html", form_data={})

@app.route("/", methods=["GET", "POST"])
def register():
    user_id = session.get("user_id")
    if not user_id:
        return None
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