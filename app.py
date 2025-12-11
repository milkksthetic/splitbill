# I utilised ChatGPT, Blackbox AI, DeepSeek and Cursor AI to assist with generating code snippets, explanations and debugging.
# The essence of the work is my own, and I have reviewed and modified the AI-generated content.

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, myr

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["myr"] = myr

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///splitbill.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


### ACCOUNT MANAGEMENT ###
@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():

    if request.method == "POST":

        # Get data from form
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Check current password
        user = db.execute("SELECT * FROM users where id = ?", session["user_id"])
        if not check_password_hash(user[0]["hash"], current_password):
            return apology("invalid current password")

        # Check new password
        if new_password != confirmation:
            return apology("passwords do not match")

        # Update users table
        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   generate_password_hash(new_password), session["user_id"])

        return redirect("/")

    else:
        return render_template("changepassword.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User submitted a form
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User clicked a link
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("You are logged out.")

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Check username
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Check password
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Check confirmation
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Check if match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Check if username already exists
        if len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))) != 0:
            return apology("username already exists", 400)

        # Insert the new user into users
        username = request.form.get("username")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username,
                   generate_password_hash(request.form.get("password")))

        # Check for newly inserted user
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


### FRIENDS MANAGEMENT ###
@app.route("/friends")
@login_required
def friends():
    # Get list of current friends
    friends = db.execute("""
        SELECT users.id AS user_id, users.username
        FROM friends
        JOIN users on friends.friend_id = users.id
        WHERE (friends.user_id = ? OR friends.friend_id = ?) AND friends.status = 'accepted' AND users.id != ?
    """, session["user_id"], session["user_id"], session["user_id"])

    # Get list of pending requests
    pending_requests = db.execute("""
        SELECT users.id AS user_id, users.username
        FROM friends
        JOIN users on friends.user_id = users.id
        WHERE friends.friend_id = ? AND friends.status = 'pending'
    """, session["user_id"])

    # Get list of outgoing requests
    outgoing_requests = db.execute("""
        SELECT users.id AS user_id, users.username
        FROM friends
        JOIN users on friends.friend_id = users.id
        WHERE friends.user_id = ? AND friends.status = 'pending'
    """, session["user_id"])

    return render_template("friends.html", friends=friends, pending_requests=pending_requests, outgoing_requests=outgoing_requests)


@app.route("/addfriend", methods=["POST"])
@login_required
def addfriend():
    # Get user id to add as friend
    friend = db.execute("SELECT id FROM users WHERE username = ?", (request.form.get("username"),))

    if not friend:
        return apology("user not found")

    friend_id = friend[0]['id']

    db.execute("""
        INSERT OR IGNORE INTO friends (user_id, friend_id, status)
        VALUES (?, ?, 'pending')
    """, session["user_id"], friend_id)

    flash("Friend request sent.")

    return redirect("/friends")


@app.route("/acceptfriend", methods=["POST"])
@login_required
def acceptfriend():
    # Accept friend request
    friend_id = request.form.get("friend_id")

    db.execute("""
        UPDATE friends
        SET status = 'accepted'
        WHERE user_id = ? AND friend_id = ?
    """, friend_id, session["user_id"])

    db.execute("""
        INSERT INTO friends (user_id, friend_id, status)
        VALUES (?, ?, 'accepted')
    """, session["user_id"], friend_id)

    flash("You are now friends.")

    return redirect("/friends")


@app.route("/removefriend", methods=["POST"])
@login_required
def removefriend():
    # Remove friend
    friend_id = request.form.get("friend_id")
    db.execute("""
        DELETE FROM friends
        WHERE (user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)
    """, session["user_id"], friend_id, friend_id, session["user_id"])

    flash("Removed friend.")

    return redirect("/friends")


### DASHBOARD ###
@app.route("/")
@login_required
def index():
    user_id = session.get("user_id")

    # Get username
    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]

    # Fetch grand summary: total owed by/to others
    grand_summary = db.execute("""
        SELECT
            users.username AS person,
            SUM(CASE WHEN splits.user_id = ? AND bills.paid_by = users.id THEN splits.amount ELSE 0 END) AS amount_you_owe,
            SUM(CASE WHEN bills.paid_by = ? AND splits.user_id = users.id THEN splits.amount ELSE 0 END) AS amount_owed_to_you
        FROM users
        LEFT JOIN bills ON bills.paid_by = users.id OR bills.paid_by = ?
        LEFT JOIN splits ON splits.bill_id = bills.id
        WHERE users.id != ?
            AND (
                (splits.user_id = ? AND bills.paid_by = users.id) -- Shows what I owe to others
                OR
                (bills.paid_by = ? AND splits.user_id = users.id) -- Shows what others owe me
            )
        GROUP BY users.username
    """, user_id, user_id, user_id, user_id, user_id, user_id)

    # Pagination logic
    limit = 5  # Number of records per page
    page = int(request.args.get("page", 1))  # Get current page
    offset = (page - 1) * limit

    # Get total number of bills to calculate total pages
    total_bills = db.execute("""
        SELECT COUNT(*) AS count
        FROM bills
        WHERE id IN (SELECT DISTINCT bill_id FROM splits WHERE user_id = ? OR id IN (SELECT id FROM bills WHERE paid_by = ?))
    """, user_id, user_id)[0]["count"]

    total_pages = (total_bills + limit - 1) // limit

    # Calculate the range of pages to display
    start_page = max(1, page - 2)  # Start from 2 pages before the current page
    end_page = min(total_pages, start_page + 4)  # End at 4 pages after the start

    # Adjust start_page if end_page is less than 5 pages
    if end_page - start_page < 4:
        start_page = max(1, end_page - 4)

    # Create a list of pages to display
    displayed_pages = list(range(start_page, end_page + 1))

    # Get the bills for the current page
    recent_bills = db.execute("""
        SELECT b.id, b.name, b.category, b.total_amount, u.username AS paid_by, b.created_at, b.payment_status
        FROM bills b
        JOIN users u ON b.paid_by = u.id
        WHERE b.id IN (
            SELECT DISTINCT bill_id FROM splits WHERE user_id = ? OR bill_id IN (
                SELECT id FROM bills WHERE paid_by = ?
            )
        )
        ORDER BY b.created_at DESC
        LIMIT ? OFFSET ?
    """, user_id, user_id, limit, offset)

    # Determine next/previous pages
    previous_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    # Get current friends and pending requests
    friends = db.execute("""
        SELECT DISTINCT users.id, users.username,
        CASE
            WHEN friends.status = 'pending' AND friends.friend_id = ? THEN 'pending'
            WHEN friends.status = 'accepted' THEN 'accepted'
        END AS status
        FROM users
        JOIN friends ON
            (friends.user_id = users.id AND friends.friend_id = ?)
            OR (friends.friend_id = users.id AND friends.user_id = ?)
        WHERE (friends.status = 'accepted'
           OR (friends.status = 'pending' AND friends.friend_id = ?))
        AND users.id != ?
    """, user_id, user_id, user_id, user_id, user_id)

    return render_template("index.html", username=username, grand_summary=grand_summary, recent_bills=recent_bills, previous_page=previous_page, next_page=next_page, displayed_pages=displayed_pages, current_page=page, friends=friends)


### BILL CREATION ###
@app.route("/newbill", methods=["GET", "POST"])
@login_required
def newbill():
    user_id = session["user_id"]

    if request.method == "POST":

        # Get form data
        bill_name = request.form.get("bill_name")
        category = request.form.get("category")
        paid_by = request.form.get("paid_by")  # User ID of the payer
        item_count = int(request.form.get("item_count"))

        total_amount = 0
        items = []  # Initialize items list

        # Store items and calculate individual splits
        for i in range(item_count):
            # Get the item's name and price
            item_name = request.form.get(f"items[{i}][name]")
            item_price = float(request.form.get(f"items[{i}][price]"))
            shared_users = request.form.getlist(
                f"items[{i}][shared_by][]")  # Get shared users for this item


            # Ensure the price is split properly among shared users
            if shared_users:  # Only calculate split if there are shared users
                split_amount = (item_price / len(shared_users)) * 1.16
                total_amount += item_price

                # Save the item details in the items list
                items.append({
                    "name": item_name,
                    "price": item_price,
                    "shared_by": shared_users,
                    "split_amount": split_amount  # Store the split amount for this item
                })

        # Add 16% tax to the total amount
        total_amount_with_tax = total_amount * 1.16

        # Store the bill in the database
        bill_id = db.execute("INSERT INTO bills (name, category, total_amount, paid_by) VALUES (?, ?, ?, ?)",
                             bill_name, category, total_amount_with_tax, paid_by)

        # Store each item and its details in the database
        for item in items:
            item_id = db.execute("INSERT INTO items (bill_id, name, price) VALUES (?, ?, ?)",
                                 bill_id, item["name"], item["price"])

            # Link shared users to the item only if there are shared users
            for user_id in item["shared_by"]:
                if user_id:  # Ensure user_id is not empty
                    db.execute("INSERT INTO splits (bill_id, user_id, amount, item_id) VALUES (?, ?, ?, ?)",
                               bill_id, user_id, item["split_amount"], item_id)

        return redirect(f"/billdetails?bill_id={bill_id}")

    # Render the new bill form
    friends = db.execute("""
        SELECT users.id, users.username
        FROM users
        WHERE users.id = ?
        UNION
        SELECT users.id, users.username
        FROM users
        JOIN friends
        ON (friends.user_id = users.id AND friends.friend_id = ?)
        OR (friends.friend_id = users.id AND friends.user_id = ?)
        WHERE friends.status = 'accepted'
    """, user_id, user_id, user_id)

    return render_template("newbill.html", users=friends)


### BILL DETAILS ###
@app.route("/billdetails", methods=["GET"])
@login_required
def billdetails():
    # Get bill ID
    bill_id = request.args.get("bill_id")

    # Get bill details along with the username of the person who paid
    bill = db.execute("""
        SELECT bills.*, users.username AS paid_by_username
        FROM bills
        LEFT JOIN users ON bills.paid_by = users.id
        WHERE bills.id = ?
    """, bill_id)

    if not bill:
        return apology("bill not found")

    bill = bill[0]

    # Get item details along with shared users
    items = db.execute("""
        SELECT items.id, items.name, items.price, GROUP_CONCAT(users.username) AS shared_users
        FROM items
        LEFT JOIN splits ON items.id = splits.item_id
        LEFT JOIN users ON splits.user_id = users.id
        WHERE items.bill_id = ?
        GROUP BY items.id
    """, bill_id)

    # Calculate summary of payments
    summary = {}
    for item in items:
        shared_users = item['shared_users'].split(',') if item['shared_users'] else []
        split_amount = item['price'] / len(shared_users) if shared_users else 0
        for user in shared_users:
            if user in summary:
                summary[user] += split_amount
            else:
                summary[user] = split_amount

    return render_template("billdetails.html", bill=bill, summary=summary, items=items, myr=myr)


### SETTLE BILL ###
@app.route("/settlebills", methods=["POST"])
@login_required
def settlebills():
    #user_id = session.get("user_id")
    selected_bills = request.form.getlist("bills")  # Get the list of selected bill IDs

    # Update the payment status for each selected bill
    for bill_id in selected_bills:
        # Update the payment status to 'Paid.'
        db.execute("UPDATE bills SET payment_status = 'Paid.' WHERE id = ?", bill_id)

        # Get all splits for the current bill
        splits = db.execute("SELECT user_id, amount FROM splits WHERE bill_id = ?", bill_id)

        # Update the amount owed to zero for all users involved in the bill
        for split in splits:
            db.execute("UPDATE splits SET amount = 0 WHERE bill_id = ? AND user_id = ?",
                       bill_id, split['user_id'])

    return redirect("/")

app = app
