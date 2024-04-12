from flask import Flask, request, render_template, flash, session, redirect, abort, url_for
from email.message import EmailMessage
from flask_session import Session
from functools import wraps

import jinja2
import sqlite3
import random
import string
import smtplib
import ssl

from acc_info import *
from add import *

# Setup jinja
jinja = jinja2.Environment(loader=jinja2.FileSystemLoader("template"))
app = Flask(__name__)

# Setup secret key
app.secret_key = "72882373811"

# Secure pages
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Function to identify is user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Function to identify admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("status") is None:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function





# "/login" route
@app.route("/login", methods=["GET", "POST"])
def login():

    # Clear sessions
    session.clear()

    # Button is clicked
    if request.method == "POST":
        
        # Get input uname and pword
        uname = str(request.form.get("uname"))
        pword = str(request.form.get("pword"))

        # Strip input uname and pword
        uname = uname.strip(' ')
        pword = pword.strip(' ')

        # Check if input is comlete
        if len(uname) == 0 or len(pword) == 0:
            flash("Please complete your details!", "danger")
        elif len(uname) < 8 or len(pword) < 8:
            flash("Username and password should contain at least 8 characters!", "danger")
        
        # Input is complete
        else:

            # Connect to database
            con = sqlite3.connect("cloudway_airlines.db")
            cur = con.cursor()      

            # Get all unames
            unames = cur.execute("SELECT uname FROM users")
            check = 0
            for u in unames:
                a = str(u[0])
                if a == uname:
                    check = 1
            
            # Uname is not in database
            if check == 0:
                flash("Username does not exist in our database!", "danger")
            
            # Uname is in database
            else:
                
                # Get pword of uname
                cur.execute("SELECT pword FROM users WHERE uname = ?", [uname])
                db_pword = str(cur.fetchone()[0])

                # Check if pword is correct
                if pword != db_pword:
                    flash("Password is incorrect!", "danger")  

                # Pword is correct
                else:

                    # Get all data and check if it is admin or not
                    data = cur.execute("SELECT * FROM users WHERE uname = ?", [uname])
                    user = 0
                    for d in data:
                        if str(d[0]) == "admin_fname" and str(d[1]) == "admin_lname" and str(d[2]) == "admin_email":
                            user = 1

                    # Admin
                    if user == 1:
                        session["user_id"] = uname
                        session["status"] = uname
                        return redirect("/admin_add")
                    
                    # User
                    else:
                        session["user_id"] = uname
                        return redirect("/")                    

    # Render template login_layout.html
    return render_template("login_layout.html")





# "/signup" route
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Button is clicked
    if request.method == "POST":

        # Get user input
        fname = str(request.form.get("fname"))
        lname = str(request.form.get("lname"))
        email = str(request.form.get("email"))
        uname = str(request.form.get("uname"))
        pword = str(request.form.get("pword"))
    
        # Strip user input
        fname = fname.strip(' ')
        lname = lname.strip(' ')
        email = email.strip(' ')
        uname = uname.strip(' ')
        pword = pword.strip(' ')

        # Check if input is complete
        if len(fname) == 0 or len(lname) == 0 or len(email) == 0 or len(uname) == 0 or len(pword) == 0:
            flash("Please complete your details!", "danger")
        elif len(fname) < 3 or len(lname) < 3:
            flash("First name and last name should contain at least 3 characters!", "danger")
        elif len(email) < 11 or "@" not in email:
            flash("Invalid email!", "danger")
        elif len(uname) < 8 or len(pword) < 8:
            flash("Username and password should contain at least 8 characters!", "danger")    

        # Input is complete
        else:

            # Connect to database
            con = sqlite3.connect("cloudway_airlines.db")
            cur = con.cursor()
            
            # Get all emails
            emails = cur.execute("SELECT email FROM users")
            check = 0
            for e in emails:
                a = str(e[0])
                if a == email:
                    check = 1

            # Email is already in database
            if check == 1:
                flash("Email is already used by another account!", "danger")
            
            # Email is not in dabase
            else:

                # Try creating account
                try:
                    cur.execute("INSERT INTO users (fname, lname, email, uname, pword, money) VALUES (?, ?, ?, ?, ?, ?)", (fname, lname, email, uname, pword, 0))
                    con.commit()
                    flash("Account created successfully!", "success")
                except:
                    flash("Username is already used by another account!", "danger")

    # Render template signup_layout.html
    return render_template("signup_layout.html")





# "/reset" route
@app.route("/reset", methods=["GET", "POST"])
def reset():

    # Button is clicked
    if request.method == "POST":

        # Get uname
        uname = str(request.form.get("uname"))

        # Strip uname
        uname = uname.strip(' ')

        # Check if input is complete
        if len(uname) == 0:
            flash("Please input your username!", "danger")
        elif len(uname) < 8:
            flash("Username should contain at least 8 characters!", "danger")

        # Input is complete
        else:

            # Connect to database
            con = sqlite3.connect("cloudway_airlines.db")
            cur = con.cursor()

            # Get all unames
            unames = cur.execute("SELECT uname FROM users")
            check = 0
            for u in unames:
                a = str(u[0])
                if a == uname:
                    check = 1
            
            # Uname is not in database
            if check == 0:
                flash("Username does not exist in our database!", "danger")
            
            # Uname is in database
            else:

                # Generate new pword
                passSource = string.ascii_lowercase + string.ascii_uppercase + string.digits
                new_pword = (''.join(random.choice(passSource) for ctr in range(12)))

                # Get user email
                cur.execute("SELECT email FROM users WHERE uname = ?", [uname])
                userMail = str(cur.fetchone()[0])

                # Setup sender
                senderMail = acc_info.acc_mail
                senderPass = acc_info.acc_pword

                # Create an email
                subject = "NEW PASSWORD || CLOUDWAY AIRLINES"
                body = "Log in to your cloudway account with this new password: " + new_pword
                emailMessage = EmailMessage()
                emailMessage["From"] = senderMail
                emailMessage["To"] = userMail
                emailMessage["Subject"] = subject
                emailMessage.set_content(body)

                # Send email
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                    smtp.login(senderMail, senderPass)
                    smtp.sendmail(senderMail, userMail, emailMessage.as_string())

                # Update user pword
                cur.execute("UPDATE users SET pword = ? WHERE uname = ?", (new_pword, uname))
                con.commit()

                # Display password sent to email
                flash("New password was sent to email connected to your account!", "success")

    # Render reset_layout.html
    return render_template("reset_layout.html")





# "/" route
@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    # Connect to database
    con = sqlite3.connect("cloudway_airlines.db")
    cur = con.cursor()

    # Get uname of user
    uname = session["user_id"]

    # Button is clicked
    if request.method == "POST":

        # Get flight and seat selected
        flight = str(request.form.get("sel_flig"))
        seat = str(request.form.get("sel_seat"))

        # Get input password
        inp_pword = str(request.form.get("txt_pass"))

        # Strip input
        inp_pword = inp_pword.strip(' ')

        # Check if input is complete
        if flight == "0":
            flash("No flight selected!", "danger")
        elif seat == "0":
            flash("No seat selected!", "danger")
        elif len(inp_pword) == 0:
            flash("Please input your password!", "danger")
        elif len(inp_pword) < 8:
            flash("Password should contain at least 8 characters!", "danger")
        
        # Input is complete
        else:

            # Get status of seat
            cur.execute("SELECT status FROM flight_seat WHERE id = ? AND seat = ?", (flight, seat))
            status = str(cur.fetchone()[0])

            # Seat is unavailabe
            if status != "free":
                flash("Error occurred!", "danger")
            
            # Seat is available
            else:

                # Get pword of user
                cur.execute("SELECT pword FROM users WHERE uname = ?", [uname])
                pword = str(cur.fetchone()[0])

                # Input password is incorrect
                if inp_pword != pword:
                    flash("Password is incorrect!", "danger")
                
                # Password is correct
                else:

                    # Get price of seat
                    cur.execute("SELECT price FROM flight_seat WHERE id = ? AND seat = ?", (flight, seat))
                    price = float(cur.fetchone()[0])

                    # Get money of user
                    cur.execute("SELECT money FROM users WHERE uname = ?", [uname])
                    money = float(cur.fetchone()[0])

                    # Money is not enough
                    if money < price:
                        flash("Insufficient money to buy ticket!", "danger")
                    
                    # Money is enough
                    else:
                        
                        # Get seats count of flight
                        cur.execute("SELECT seats FROM flight_list WHERE id = ?", [flight])
                        seats = int(cur.fetchone()[0])

                        # Add one to seats
                        seats = seats + 1

                        # Subtract price from money
                        money = money - price

                        # Update user money
                        cur.execute("UPDATE users SET money = ? WHERE uname = ?", (money, uname))
                        con.commit()

                        # Update seat status
                        cur.execute("UPDATE flight_seat SET status = ? WHERE id = ? AND seat = ?", (uname, flight, seat))
                        con.commit()

                        # Update number of seats
                        cur.execute("UPDATE flight_list SET seats = ? WHERE id = ?", (seats, flight))
                        con.commit()

                        # Display purchase success
                        flash("Purchase success!", "success")

    # Get all flights
    cur.execute("SELECT * FROM flight_list")
    db = cur.fetchall()

    # Store all ongoing flights to flight_list
    flight_list = []
    for d in db:
        if(str(d[5]) == "ongoing"):
            flight_list.append(d)

    # Get all seats
    cur.execute("SELECT * FROM flight_seat")
    db = cur.fetchall()

    # Store all seats to flight_seat
    flight_seat = []
    for d in db:
        flight_seat.append(d)

    # Render index_layout.html
    return render_template("index_layout.html", flight_list=flight_list, flight_seat=flight_seat)





# "/moneytickets" route
@app.route("/moneytickets", methods=["GET", "POST"])
@login_required
def moneytickets():

    # Connect to database
    con = sqlite3.connect("cloudway_airlines.db")
    cur = con.cursor()
    
    # Get uname of user
    uname = session["user_id"]
    
    # Button is clicked
    if request.method == "POST":

        # Get input amount and password
        inp_amount = str(request.form.get("box_amou"))
        inp_pword = str(request.form.get("box_pass"))

        # Strip input
        inp_amount = inp_amount.strip(' ')
        inp_pword = inp_pword.strip(' ')

        # Try to parse input amount
        parse = 0
        try:
            num = float(inp_amount)
        except:
            parse = 1

        # Check if input is complete
        if len(inp_amount) == 0:
            flash("Please input amount!", "danger")
        elif len(inp_pword) == 0:
            flash("Please input your password!", "danger")        
        elif parse == 1:
            flash("Amount should be numerical value!", "danger")
        elif len(inp_pword) < 8:
            flash("Password should contain at least 8 characters!", "danger")

        # Input is complete
        else:
            
            # Get pword of user
            cur.execute("SELECT pword FROM users WHERE uname = ?", [uname])
            pword = str(cur.fetchone()[0])

            # Input password is incorrect
            if inp_pword != pword:
                flash("Password is incorrect!", "danger")

            # Password is correct
            else:

                # Get money of user
                cur.execute("SELECT money FROM users WHERE uname = ?", [uname])
                money = float(cur.fetchone()[0])

                # Add amount to money
                money = money + float(inp_amount)

                # Update user money
                cur.execute("UPDATE users SET money = ? WHERE uname = ?", (money, uname))
                con.commit()

                # Display money added successfully
                flash("Money added successfully!", "success")

    # Get money of user
    cur.execute("SELECT money FROM users WHERE uname = ?", [uname])
    money = float(cur.fetchone()[0])

    # Get all seats bought by users
    cur.execute("SELECT * FROM flight_seat WHERE status = ?", [uname])
    seats = cur.fetchall()

    # Store all bought seats to tickets
    tickets = []    
    for s in seats:
        id = s[0]

        # Get details from flights where seats was bought
        cur.execute("SELECT * FROM flight_list WHERE id = ?", [id])
        flights = cur.fetchall()

        for f in flights:
            all = [f[1], f[2], f[3], s[1], s[2], s[3]]
            tickets.append(all)

    # Render moneytickets_layout.html
    return render_template("moneytickets_layout.html", money=money, tickets=tickets)





# "/account" route
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():

    # Connect to database
    con = sqlite3.connect("cloudway_airlines.db")
    cur = con.cursor()
 
    # Get uname of user
    uname = session["user_id"]
 
    # Button is clicked
    if request.method == "POST":

        # Get all user data
        cur.execute("SELECT * FROM users WHERE uname = ?", [uname])
        users = cur.fetchall()
        for u in users:
            fname = str(u[0])
            lname = str(u[1])
            email = str(u[2])
            pword = str(u[4])
   
        # Button update is clicked
        if request.form["btn_acc"] == "update":
            
            # Get input
            inp_fname = str(request.form.get("txt_fnam"))
            inp_lname = str(request.form.get("txt_lnam"))
            inp_email = str(request.form.get("txt_emai"))

            # Strip input
            inp_fname = inp_fname.strip(' ')
            inp_lname = inp_lname.strip(' ')
            inp_email = inp_email.strip(' ')

            # Check if input is complete
            if fname == inp_fname and lname == inp_lname and email == inp_email:
                flash("No changes made!", "danger")
            elif len(inp_fname) == 0 or len(inp_lname) == 0 or len(inp_email) == 0:
                flash("Please complete your details!", "danger")
            elif len(inp_fname) < 3 or len(inp_lname) < 3:
                flash("First name and last name should contain at least 3 characters!", "danger")
            elif len(inp_email) < 11 or "@" not in inp_email:
                flash("Invalid email!", "danger")

            # Input is complete
            else:

                # Get all email in users
                check = 0
                cur.execute("SELECT email FROM users")
                emails = cur.fetchall()
                for e in emails:
                    em = str(e[0])
                    if em != email and em == inp_email:
                       check = 1

                # Email is already used
                if check == 1:
                    flash("Email is already used by another account!", "danger")

                # Email is not yet used
                else:
                    
                    # Update user info
                    cur.execute("UPDATE users SET fname = ?, lname = ?, email = ? WHERE uname = ?", (inp_fname, inp_lname, inp_email, uname))
                    con.commit()

                    # Display information updated successfully
                    flash("Information updated successfully!", "success")

        # Button change is clicked
        elif request.form["btn_acc"] == "change":

            # Get input
            inp_cur = str(request.form.get("cur_pass"))
            inp_new = str(request.form.get("new_pass"))

            # Strip input
            inp_cur = inp_cur.strip(' ')
            inp_new = inp_new.strip(' ')

            # Check if input is complete
            if len(inp_cur) == 0 or len(inp_new) == 0:
                flash("Please complete your details!", "danger")
            elif len(inp_cur) < 8 or len(inp_new) < 8:
                flash("Password should contain at least 8 characters!", "danger")
            elif inp_cur == inp_new:
                flash("Passwords are the same!", "danger")
            elif inp_cur != pword:
                flash("Current password is incorrect!", "danger")

            # Input is complete
            else:

                # Update user password
                cur.execute("UPDATE users SET pword = ? WHERE uname = ?", (inp_new, uname))
                con.commit()

                # Display password changed successfully
                flash("Password changed successfully!", "success")

        # Button logout is clicked
        elif request.form["btn_acc"] == "logout":

            # Clear session and redirect to login
            session.clear()
            return redirect(url_for("login"))

    # Get all user data
    cur.execute("SELECT * FROM users WHERE uname = ?", [uname])
    users = cur.fetchall()
    for u in users:
        fname = str(u[0])
        lname = str(u[1])
        email = str(u[2])

    # Render account_layout.html
    return render_template("account_layout.html", fname=fname, lname=lname, email=email, uname=uname)










# "admin_add" route
@app.route("/admin_add", methods=["GET", "POST"])
@login_required
@admin_required
def admin_add():

    # Button is clicked
    if request.method == "POST":

        # Get input
        flight_date = str(request.form.get("flight_date"))
        flight_destination = str(request.form.get("flight_destination"))
        flight_time = str(request.form.get("flight_time"))
        deluxe_price = str(request.form.get("deluxe_price"))
        first_class_price = str(request.form.get("first_class_price"))
        economy_class_price = str(request.form.get("economy_class_price"))
        
        # Check if input is complete
        if len(flight_date) == 0:
            flash("Please Enter a valid Flight Date!", "danger")
        elif len(flight_time) == 0:
            flash("Invalid Flight Time","danger")
        elif len(flight_destination) == 0:
            flash("Invalid Flight Destination","danger")
        elif len(deluxe_price) == 0 or deluxe_price == '0':
            flash("Invalid Deluxe Price","danger")
        elif len(first_class_price) == 0 or deluxe_price == '0':
            flash("Invalid First Class Price","danger") 
        elif len(economy_class_price) == 0 or deluxe_price == '0':
            flash("Invalid Economy Class Price","danger")
        
        # Input is complete
        else:
        
            # Create flight
            flight_add(flight_date, flight_destination, flight_time, deluxe_price, first_class_price,economy_class_price)
            
            # Display flight added successfully
            flash("Flight Added Succesfully!", "success")
    
    # Render template admin_add_layout.html
    return render_template("admin_add_layout.html")





# "admin_edit" route
@app.route("/admin_edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit():

    # Connect to database
    con = sqlite3.connect("cloudway_airlines.db")
    cur = con.cursor() 

    # Button is clicked
    if request.method == "POST":
        
        # Get clicked flight id and status
        flight_id = str(request.form.get("id_form"))
        flight_status = str(request.form["statusSelect"])
        
        # Update flight
        cur.execute("UPDATE flight_list SET  status = ? WHERE id = ?", (flight_status, flight_id))
        con.commit()

    # Get all flight
    flight_data = cur.execute("SELECT id, date, time, destination, seats, status FROM flight_list")
    
    # Render admin_edit_layout.html
    return render_template("admin_edit_layout.html", flight_data=flight_data)





# "admin_acc" route
@app.route("/admin_acc", methods=["GET", "POST"])
@login_required
@admin_required
def admin_acc():

    # Connect to database
    con = sqlite3.connect("cloudway_airlines.db")
    cur = con.cursor()
 
    # Get uname of user
    uname = session["user_id"]
 
    # Button is clicked
    if request.method == "POST":

        # Get all user data
        cur.execute("SELECT * FROM users WHERE uname = ?", [uname])
        users = cur.fetchall()
        for u in users:
            fname = str(u[0])
            lname = str(u[1])
            email = str(u[2])
            pword = str(u[4])
   
        # Button update is clicked
        if request.form["btn_acc"] == "update":
            
            # Get input
            inp_fname = str(request.form.get("txt_fnam"))
            inp_lname = str(request.form.get("txt_lnam"))
            inp_email = str(request.form.get("txt_emai"))

            # Strip input
            inp_fname = inp_fname.strip(' ')
            inp_lname = inp_lname.strip(' ')
            inp_email = inp_email.strip(' ')

            # Check if input is complete
            if fname == inp_fname and lname == inp_lname and email == inp_email:
                flash("No changes made!", "danger")
            elif len(inp_fname) == 0 or len(inp_lname) == 0 or len(inp_email) == 0:
                flash("Please complete your details!", "danger")
            elif len(inp_fname) < 3 or len(inp_lname) < 3:
                flash("First name and last name should contain at least 3 characters!", "danger")
            elif len(inp_email) < 11 or "@" not in inp_email:
                flash("Invalid email!", "danger")

            # Input is complete
            else:

                # Get all email in users
                check = 0
                cur.execute("SELECT email FROM users")
                emails = cur.fetchall()
                for e in emails:
                    em = str(e[0])
                    if em != email and em == inp_email:
                       check = 1

                # Email is already used
                if check == 1:
                    flash("Email is already used by another account!", "danger")

                # Email is not yet used
                else:
                    
                    # Update user info
                    cur.execute("UPDATE users SET fname = ?, lname = ?, email = ? WHERE uname = ?", (inp_fname, inp_lname, inp_email, uname))
                    con.commit()

                    # Display information updated successfully
                    flash("Information updated successfully!", "success")

        # Button change is clicked
        elif request.form["btn_acc"] == "change":

            # Get input
            inp_cur = str(request.form.get("cur_pass"))
            inp_new = str(request.form.get("new_pass"))

            # Strip input
            inp_cur = inp_cur.strip(' ')
            inp_new = inp_new.strip(' ')

            # Check if input is complete
            if len(inp_cur) == 0 or len(inp_new) == 0:
                flash("Please complete your details!", "danger")
            elif len(inp_cur) < 8 or len(inp_new) < 8:
                flash("Password should contain at least 8 characters!", "danger")
            elif inp_cur == inp_new:
                flash("Passwords are the same!", "danger")
            elif inp_cur != pword:
                flash("Current password is incorrect!", "danger")

            # Input is complete
            else:

                # Update user password
                cur.execute("UPDATE users SET pword = ? WHERE uname = ?", (inp_new, uname))
                con.commit()

                # Display password changed successfully
                flash("Password changed successfully!", "success")

        # Button logout is clicked
        elif request.form["btn_acc"] == "logout":

            # Clear session and redirect to login
            session.clear()
            return redirect(url_for("login"))

    # Get all user data
    cur.execute("SELECT * FROM users WHERE uname = ?", [uname])
    users = cur.fetchall()
    for u in users:
        fname = str(u[0])
        lname = str(u[1])
        email = str(u[2])

    # Render account_layout.html
    return render_template("admin_acc_layout.html", fname=fname, lname=lname, email=email, uname=uname)