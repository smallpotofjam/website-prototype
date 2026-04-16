from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Product, Order, OrderItem
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 🔑 Secret key for sessions
app.config['SECRET_KEY'] = 'super-secret-key-12345'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Create tables if not exist
with app.app_context():
    db.create_all()


def get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]
# ----------------------
# Routes
# ----------------------


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))  # ✅ Redirect after login
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))

@app.route("/user")
def user_page():
    if not session.get("user_id"):
        return redirect(url_for("login"))  # protect page

    return render_template("userpage.html", username=session.get("username"))

# Example pages
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        image = request.form["image"]
        description = request.form["description"]

        # Category
        category = request.form.get("category")

        # Tags
        tags_list = request.form.getlist("tags")
        tags = ",".join(tags_list)

        new_product = Product(
            name=name,
            price=price,
            image=image,
            description=description,
            category=category,
            tags=tags
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product added!", "success")
        return redirect(url_for("dashboard"))

    # ✅ ALWAYS define orders here
    orders = Order.query.all()

    return render_template("dashboard.html", orders=orders)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    cart = get_cart()

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart

    flash("Added to cart!", "success")
    return redirect(request.referrer)

@app.route("/cart")
def cart():
    cart = get_cart()
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))

        if product:
            item_total = product.price * quantity
            total += item_total

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/increase/<int:product_id>")
def increase_quantity(product_id):
    cart = get_cart()
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/decrease/<int:product_id>")
def decrease_quantity(product_id):
    cart = get_cart()
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        # ❌ Remove if quantity = 0
        if cart[product_id] <= 0:
            del cart[product_id]

    session["cart"] = cart
    return redirect(url_for("cart"))

@app.context_processor
def cart_total():
    cart = session.get("cart", {})
    total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * quantity

    return dict(cart_total=total)
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = get_cart()

    if request.method == "POST":
        address = request.form["address"]
        username = session.get("username", "Guest")

        total = 0
        order = Order(username=username, address=address, total=0)

        db.session.add(order)
        db.session.commit()  # get order ID

        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))

            if product:
                total += product.price * quantity

                item = OrderItem(
                    order_id=order.id,
                    product_name=product.name,
                    quantity=quantity,
                    price=product.price
                )
                db.session.add(item)

        order.total = total
        db.session.commit()

        # 🧹 Clear cart
        session["cart"] = {}

        return redirect(url_for("home"))

    return render_template("checkout.html")

@app.route("/complete_order/<int:order_id>")
def complete_order(order_id):
    order = Order.query.get(order_id)

    if order:
        order.status = "Completed"
        db.session.commit()

    return redirect(url_for("dashboard"))
@app.route("/aarongame")
def aarongame():
    return render_template("aarongame.html")

# Category pages
@app.route("/coffee")
def coffee_page():
    return render_template("coffee.html")

@app.route("/fruit")
def fruit_page():
    return render_template("fruit.html")

@app.route("/meat")
def meat_page():
    return render_template("meat.html")

@app.route("/drinks")
def drinks_page():
    return render_template("drinks.html")

@app.route("/new")
def new_page():
    return render_template("new.html")

@app.route("/products")
def products():
    search = request.args.get("search")
    category = request.args.get("category")
    tags = request.args.getlist("tags")  # ✅ multiple tags

    query = Product.query

    # 🔍 Search
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # 🥩 Category
    if category:
        query = query.filter_by(category=category)

    # 🏷️ Multi-tag filter (must match ALL selected tags)
    if tags:
        for tag in tags:
            query = query.filter(Product.tags.ilike(f"%{tag}%"))

    products = query.all()

    return render_template("products.html", products=products)


# ----------------------
if __name__ == "__main__":
    app.run(debug=True)