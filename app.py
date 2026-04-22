import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from models import Base, User, engine, db_session
from security import hash_password, check_password, generate_salt


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
Base.metadata.create_all(engine)

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
        if not user and username:
            errors.append("user does not exist.")
            return render_template("Pages/Login.html", form_data=request.form, errors=errors)
        if not username:
            errors.append("Please enter a username.")
        if not check_password(user.password_hash, password, user.salt):
            errors.append("Incorrect password.")
        if errors:
            return render_template("Pages/Login.html", form_data=request.form, errors=errors)

        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("Pages/Login.html", form_data={}, errors=[])

@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []

    if request.method == "POST":
        firstname = request.form.get("firstname", "").strip()
        lastname = request.form.get("lastname", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmpassword = request.form.get("confirmpassword", "")

        if not firstname:
            errors.append("First name is required.")
        if not lastname:
            errors.append("Last name is required.")
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")
        if confirmpassword != password:
            errors.append("Password does not match.")

        existing_user = db_session.query(User).filter_by(username=username).first()
        if existing_user:
            errors.append("That username already exists.")

        if not errors:
            salt = generate_salt()

            new_user = User(
                firstname=firstname,
                lastname=lastname,
                username=username,
                password_hash=hash_password(password, salt),
                salt=salt,
            )
            db_session.add(new_user)
            db_session.commit()
            return redirect(url_for("login"))
          
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