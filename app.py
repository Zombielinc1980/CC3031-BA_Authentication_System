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
            errors.append("Invalid username or password.")
            return render_template("Pages/Login.html", form_data=request.form, errors=errors)

        session["user_id"] = user.id
        return render_template("Pages/Dashboard.html")
    return render_template("Pages/Login.html", form_data={}, errors=[])

@app.route("/", methods=["GET", "POST"])
def register():
    errors = []

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        existing_user = db_session.query(User).filter_by(username=username).first()
        if existing_user:
            errors.append("That username already exists.")

        salt = generate_salt()

        if not errors:
            new_user = User(
                username=username,
                password_hash=hash_password(password, salt),
                salt=salt,
                encryption_key=generate_key()
            )
            db_session.add(new_user)
            db_session.commit()
            return render_template("Pages/Login.html")
          
        return render_template("Pages/Register.html", errors=errors, form_data=request.form)
      
    return render_template("Pages/Register.html", errors=[], form_data={})


# dashboard - all
@app.route("/dashboard")
def dashboard():
    return render_template("Pages/Dashboard.html")

# employee+
@app.route("/equipment")
def equipment_list():
    return render_template("Pages/Equipment.html")

@app.route("/customers")
def customer_list():
    return render_template("Pages/CustomerList.html")

@app.route("/rentals")
def rental_list():
    return render_template("Pages/RentalList.html")

@app.route("/rentals/create")
def create_rental():
    return render_template("Pages/CreateRental.html")

# admin
@app.route("/equipment/manage")
def manage_equipment():
    return render_template("Pages/ManageEquipment.html")

@app.route("/reports/revenue")
def revenue_reports():
    return render_template("Pages/RevenueReports.html")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)