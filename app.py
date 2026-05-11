import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
# TODO: add return page for returning equipment for customers

from models import Base, engine, db_session, User, Customer, Equipment, Rental
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
    session.clear()
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

# all
@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    errors = []

    as_role = request.form.get("as_role", "customer")
    if as_role not in ["employee", "admin"]:
        as_role = "customer"
    print(as_role)

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
                access=as_role
            )
            print(as_role)
            db_session.add(new_user)
            db_session.commit()

            if as_role == "customer":
                new_customer = Customer(
                    firstname = firstname,
                    lastname = lastname,
                    user_id = new_user.id
                )
                db_session.add(new_customer)
                db_session.commit()
            return redirect(url_for("login"))
        return render_template("Pages/Register.html", errors=errors, form_data=request.form)
    return render_template("Pages/Register.html", errors=[], form_data={})

# all
@app.route("/dashboard")
def dashboard():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("Pages/Dashboard.html", user=user)

# all
@app.route("/equipment")
def equipment_list():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for("login"))
    equipment = db_session.query(Equipment).all()
    return render_template("Pages/EquipmentList.html", equipment=equipment)

# employee+
@app.route("/customers")
def customer_list():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for("login"))
    if user.access == "customer":
        return redirect(url_for("dashboard"))

    customers = db_session.query(Customer).all()
    return render_template("Pages/CustomerList.html", customers=customers)

# all (customers can only view their own rentals)
@app.route("/rentals")
def rental_list():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for("login"))

    if user.access == "customer":
        customer = db_session.query(Customer).filter_by(user_id=user.id).first()
        rentals = db_session.query(Rental).filter_by(customer_id=customer.id).all()
        return render_template("Pages/RentalList.html", rentals=rentals)

    rentals = db_session.query(Rental).all()
    return render_template("Pages/RentalList.html", rentals=rentals)

# all (employees and admins must provide a customer account for rental)
@app.route("/rentals/create", methods=["GET", "POST"])
def create_rental():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for("login"))

    equipment = db_session.query(Equipment).all()
    if request.method == "GET":
        return render_template("Pages/CreateRental.html", user=user, errors=[], equipment=equipment)

    errors = []
    if user.access != "customer":
        customer_id = request.form.get("customer_id")
        customer = db_session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            errors.append("Customer not found")
            return render_template("Pages/CreateRental.html", user=user, errors=errors, equipment=equipment)

    else:
        customer = db_session.query(Customer).filter_by(user_id=user.id).first()

    selected_equipment_id = request.form.get("equipment_id")
    quantity = int(request.form.get("quantity"))
    selected_equipment =  db_session.query(Equipment).filter_by(id=selected_equipment_id).first()

    if quantity > selected_equipment.stock:
        errors.append("Quantity exceeds stock")
        return render_template("Pages/CreateRental.html", user=user, errors=errors, equipment=equipment)
    else:
        selected_equipment.stock -= quantity

    new_rental = Rental(
        equipment_id = selected_equipment_id,
        customer_id = customer.id,
        quantity = quantity,
        price = quantity * selected_equipment.price
    )
    db_session.add_all([new_rental, selected_equipment])
    db_session.commit()
    flash("Rental added successfully")
    return redirect(url_for("dashboard"))

# admin
@app.route("/equipment/manage", methods=["GET","POST"])
def manage_equipment():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for("login"))
    if user.access in ["customer", "employee"]:
        return redirect(url_for("dashboard"))
    if request.method == "GET":
        return render_template("Pages/ModifyEquipment.html", user=user, errors=[])

    errors = []
    name = request.form.get("name")
    price = request.form.get("price")
    stock = request.form.get("stock")

    equipment = db_session.query(Equipment).all()
    names = []
    for e in equipment:
        names.append(e.name)
    if name in names:
        errors.append("Equipment with this name already exists")
        return render_template("Pages/ModifyEquipment.html", user=user, errors=errors)

    new_equipment = Equipment(
        name = name,
        price = price,
        stock = stock
    )
    db_session.add(new_equipment)
    db_session.commit()
    flash("Equipment added successfully")
    return redirect(url_for("dashboard"))

# admin
@app.route("/reports/revenue")
def revenue_reports():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for("login"))
    if user.access in ["customer", "employee"]:
        return redirect(url_for("dashboard"))
    return render_template("Pages/RevenueReports.html")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)