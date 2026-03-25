from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField
from wtforms.validators import InputRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_login import UserMixin
from wtforms import FileField
from wtforms.validators import InputRequired
import os
from werkzeug.utils import secure_filename


main = Blueprint("main", __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
#login_manager.login_view = 'login'  #redirect users to login page if not logged in

bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = "your_secret_key_here"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brew.db'  #SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\753336\\OneDrive - New College Swindon\\SQLiteDatabaseBrowserPortable\\zoo.db'

#C:\Users\753336\OneDrive - New College Swindon\SQLiteDatabaseBrowserPortable
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap()
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#database model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(150), nullable=False, unique=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    house_number = db.Column(db.String(25))
    street_name = db.Column(db.String(35), nullable=False)
    country = db.Column(db.String(35), nullable=False)
    post_code = db.Column(db.String(7), nullable=False)

#WTForms form
class Register(FlaskForm):
    email_address = EmailField("Email Address:", validators=[InputRequired(), Length(min=4)])
    first_name = StringField("First Name:", validators=[InputRequired(), Length(max=25)])
    last_name = StringField("Last Name:", validators=[InputRequired(), Length(max=25)])
    password = PasswordField("Password:", validators=[InputRequired(), Length(min=8, max=25)])
    house_number = StringField("House Number:", validators=[InputRequired(), Length(max=25)])
    street_name = StringField("Street Name:", validators=[InputRequired(), Length(max=35)])
    country = StringField("Country:", validators=[InputRequired(), Length(max=35)])
    post_code = StringField("Post Code:", validators=[InputRequired(), Length(max=7)])

class VisitDB(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    image = db.Column(db.String(300), nullable=True)  # NEW FIELD

    def __repr__(self):
        return f"<ProductDB: {self.id}, {self.name}, {self.price}, {self.category}, {self.description}, {self.image}>"


class CurrentVisit:
    def __init__(self, name, price, category, description, image):
        self.name = name
        self.price = price
        self.category = category
        self.description = description
        self.image=image

    def add_visit_to_db(self):
        new_record = VisitDB(name=self.name, price=self.price, category=self.category, description=self.description, image=self.image)
        db.session.add(new_record)
        db.session.commit()

class OrderDB(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    booking = db.Column(db.String(100), nullable=False)
    total = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(15), nullable=False)
    name_on_card = db.Column(db.String(100), nullable=False)
    security_code = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return (f"<UserDB: {self.id}, {self.name}, {self.email}, {self.phone}, {self.store}, {self.total}, "
                f"{self.card_number}, {self.name_on_card}, {self.security_code}>")

class CurrentOrder:
    def __init__(self, name, email, phone, booking, total, card_number, name_on_card, security_code):
        self.name = name
        self.email = email
        self.phone = phone
        self.booking = booking
        self.total = total
        self.card_number = card_number
        self.name_on_card = name_on_card
        self.security_code = security_code

    def add_order_to_db(self):
        new_record = OrderDB(name=self.name, email=self.email, phone=self.phone, booking=self.booking,
                             total=self.total, card_number=self.card_number, name_on_card=self.name_on_card,
                             security_code=self.security_code)
        db.session.add(new_record)
        db.session.commit()

class AddVisitForm(FlaskForm):
    name = StringField("Visit Name:", validators=[InputRequired()])
    price = StringField("Visit Price (DO NOT include pound (£) symbol!):", validators=[InputRequired()])
    category = SelectField("Visit Type:", validators=[InputRequired()], choices=[
        "--Please Select--", "Family Visit", "Solo Visit", "School Visit"
    ])
    description = StringField("Short Description:", validators=[InputRequired()])
    image = FileField("Product Image:")


class CheckOutForm(FlaskForm):
    name = StringField("Full Name:", validators=[InputRequired()])
    email = EmailField("Email:", validators=[InputRequired()])
    phone = StringField("Phone Number:", validators=[InputRequired()])
    store = SelectField("Which store do you want to collect your order form:", validators=[InputRequired()], choices=[
        "--Please Select--", "London", "Bristol", "Swindon"
    ])
    card_number = StringField("Card Number:", validators=[InputRequired()])
    name_on_card = StringField("Name on Card:", validators=[InputRequired()])
    security_code = StringField("Security Code:", validators=[InputRequired()])

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


# routes
@app.route("/register", methods=["GET", "POST"])
def register():
    form = Register()
    if form.validate_on_submit():
        # Save the user to the database
        new_user = User(
            email_address=form.email_address.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            house_number=form.house_number.data,
            street_name=form.street_name.data,
            country=form.country.data,
            post_code=form.post_code.data
        )
        db.session.add(new_user)
        db.session.commit()

        # Redirect to login page instead of success.html
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email_address"]
        password = request.form["password"]
        user = User.query.filter_by(email_address=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # session["user_id"] = user.id
            login_user(user)
            return render_template("menu.html", first_name=user.first_name, last_name=user.last_name)

        else:
            error = "Invalid email or password"
    return render_template("login.html", error=error)


@app.route("/")
def home():
    return render_template("home.html")

@main.route("/attractions/birds")
def birds():
    return render_template("birds.html")

@main.route("/menu", methods=["GET", "POST"])
def menu():
    products = VisitDB.query.all()
    print(products)
    return render_template("menu.html", products=products)


@main.route("/add_visit", methods=["GET", "POST"])
def add_visit():
    form = AddVisitForm()

    if form.validate_on_submit():
        image_file = form.image.data

        filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

        new_product = VisitDB(
            name=form.name.data,
            price=form.price.data,
            category=form.category.data,
            description=form.description.data,
            image=filename
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for("main.menu"))

    return render_template("add_product.html", form=form)


@main.route("/order/add/<product_ordered>")
def add_to_order(product_ordered):
    products = ProductDB.query.all()

    if "order" not in session:
        session["order"] = []

    for product in products:
        if product.name == product_ordered:
            session["order"].append({"name": product.name, "price": product.price})
            flash(f"{product.name} was successfully added to your Order!", "success")
            return redirect("/menu")


@main.route("/order")
def order_basket():
    order = session.get("order", [])
    return render_template("order_basket.html", order_basket=order)


@main.route("/clear")
def clear_basket():
    session["order"] = []
    flash(f"Your Basket was successfully cleared!", "success")
    return redirect("/order")


def create_domo_menu():
    if not db.session.query(VisitDB).all():
        CurrentVisit("Classic Latte", "3.50", "Hot Drinks",
                       "A smooth blend of espresso and steamed milk, topped with a light layer of foam",
                       "classic_latte.jpeg").add_visit_to_db()
        CurrentVisit("Chai Teat Latte", "3.80", "Hot Drinks",
                       "A warm, spiced tea infused with cinnamon, cardamom, and a touch of honey, finished with steamed milk.",
                       "chai_latte.jpeg").add_visit_to_db()
        CurrentVisit("Berry Blast Smoothie", "4.50", "Cold Drinks",
                       "A refreshing mix of strawberries, blueberries, and raspberries blended with yogurt and ice.",
                       "berry_smoothie.jpeg").add_visit_to_db()
        CurrentVisit("Blueberry Muffin", "2.80", "Baked Goods",
                       "A soft and fluffy muffin bursting with fresh blueberries, perfect for a morning treat.",
                       "blueberry_muffin.jpeg").add_visit_to_db()
        CurrentVisit("Chocolate Chip Cookie", "1.80", "Baked Goods",
                       "A large, chewy cookie loaded with gooey chocolate chips.",
                       "choc_chip_muffin.jpeg").add_visit_to_db()


@main.route("/checkout", methods=["GET", "POST"])
def checkout():
    order = session.get("order", [])
    total_price = 0
    summary = "Your order consists of:"

    for item in order:
        total_price += float(item["price"])
        summary += f" {item['name']},"

    form = CheckOutForm()

    if form.validate_on_submit():
        order = CurrentOrder(form.name.data, form.email.data, form.phone.data, form.store.data, total_price,
                             form.card_number.data, form.name_on_card.data, form.security_code.data)

        order.add_order_to_db()

        session["order"] = []

        flash(
            f"Thank you!\nYou have successfully placed on order! Please visit the {form.store.data} store to collect.",
            "success")

        return redirect("/")

    return render_template("checkout.html", price=total_price, summary=summary, type="order",
                           form=form)

@app.route('/carbon')
def carbon():
    return render_template('carbon.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        rating = request.form.get("rating")
        message = request.form.get("message")

        print("\n--- New Feedback Submitted ---")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Rating: {rating}")
        print(f"Message: {message}")
        print("------------------------------\n")

        flash("Thank you for your feedback!", "success")
        return redirect("/feedback")

    return render_template("feedback.html")


@app.route("/bullplinth")
def bullplinth():
    return render_template("bullplinth.html")

@app.route('/educational')
def educational():
    return render_template('educational.html')


# run the app
app.register_blueprint(main)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # create the SQLite database and tables
        #create_domo_menu()
    app.run(debug=True)
